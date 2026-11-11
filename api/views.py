from dataclasses import dataclass
from math import ceil

from django.conf import settings
from rest_framework.decorators import api_view, throttle_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle

from .insights import AIInsightError, generate_fit_insights
from .models import College
from .scorecard import ScorecardError, get_scorecard_schools, normalize_school


US_STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID',
    'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS',
    'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK',
    'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
    'WI', 'WY',
}


class AIInsightThrottle(ScopedRateThrottle):
    scope = 'ai_insights'


@dataclass
class MatchCollege:
    id: int | str
    name: str
    location: str
    state: str | None
    setting: str | None
    student_size: int | None
    party_score: int | None
    net_price_estimate: int | None
    transfer_friendly: bool | None
    majors: str | None
    residential_rate: int | None
    scorecard_details: dict | None = None


def _parse_majors(text):
    return [major.strip().lower() for major in text.split(',') if major.strip()]


def _explain_factor(college, preferences, scorecard_source):
    matches = []
    mismatches = []
    pref_setting = preferences.get('setting')
    if pref_setting and college.setting:
        if college.setting == pref_setting:
            matches.append('Campus setting matches your preference')
        else:
            mismatches.append('Campus setting differs from your preference')

    majors_pref = preferences.get('majors', [])
    if majors_pref:
        if college.majors is None and scorecard_source:
            matches.append('Major offerings are not included in Scorecard institution data')
        else:
            college_majors = _parse_majors(college.majors or '')
            intersect = [major for major in majors_pref if major.lower() in college_majors]
            if intersect:
                matches.append(f"Offers majors: {', '.join(intersect)}")
            else:
                mismatches.append('Does not offer preferred majors')

    party_pref = preferences.get('party_pref')
    if party_pref and college.party_score is None and scorecard_source:
        matches.append('Social scene is not reported in Scorecard institution data')
    elif party_pref and college.party_score is not None:
        if party_pref == 'low' and college.party_score > 7:
            mismatches.append('High party culture')
        elif party_pref == 'high' and college.party_score < 4:
            mismatches.append('Low party culture')
        else:
            matches.append('Vibe aligns with party preference')

    max_tuition = preferences.get('max_tuition')
    if max_tuition is not None and college.net_price_estimate is not None:
        if college.net_price_estimate <= max_tuition:
            matches.append('Estimated net price within budget')
        else:
            mismatches.append('Estimated net price may exceed budget')

    student_size_max = preferences.get('student_size_max', preferences.get('class_size_max'))
    if student_size_max is not None and college.student_size is not None:
        if college.student_size <= student_size_max:
            matches.append('Student population is within your preferred size')
        else:
            mismatches.append('Student population is above your preferred size')
    elif student_size_max is not None and scorecard_source:
        matches.append('Student population is not reported for this institution')
    return matches, mismatches


def _score_college(college, preferences, weights, track, pain_points, scorecard_source, importance=None):
    importance = importance or {
        'academics': 3,
        'campus': 3,
        'location': 3,
        'cost': 3,
        'student_life': 3,
    }
    pref_majors = preferences.get('majors', [])
    if pref_majors and college.majors is not None:
        college_majors = _parse_majors(college.majors)
        matched = sum(1 for major in pref_majors if major.lower() in college_majors)
        academics_score = min(1.0, matched / max(1, len(pref_majors)))
    else:
        academics_score = 0.5

    campus_scores = []
    setting_pref = preferences.get('setting')
    if setting_pref and college.setting:
        campus_scores.append((1.0 if college.setting == setting_pref else 0.0, importance['location']))
    desired_residential = preferences.get('residential_rate')
    if desired_residential is not None and college.residential_rate is not None:
        campus_scores.append((
            max(0, 1 - abs(college.residential_rate - desired_residential) / 100),
            importance['campus'],
        ))
    student_size_max = preferences.get('student_size_max', preferences.get('class_size_max'))
    if student_size_max is not None and college.student_size is not None:
        size_score = 1 - max(0, college.student_size - student_size_max) / max(1, student_size_max)
        campus_scores.append((max(0.0, size_score), importance['campus']))
    campus_score = (
        sum(score * factor for score, factor in campus_scores) / sum(factor for _, factor in campus_scores)
        if campus_scores
        else 0.5
    )

    cost_score = 0.5
    max_tuition = preferences.get('max_tuition')
    if max_tuition is not None and college.net_price_estimate is not None:
        if college.net_price_estimate <= max_tuition:
            cost_score = 1.0
        else:
            cost_score = max(
                0.0,
                1 - (college.net_price_estimate - max_tuition) / max(1, max_tuition),
            )

    social_score = 0.5
    party_pref = preferences.get('party_pref')
    if party_pref and college.party_score is not None:
        if party_pref == 'low':
            social_score = max(0.0, 1 - college.party_score / 10)
        elif party_pref == 'high':
            social_score = min(1.0, college.party_score / 10)

    practical_score = 0.5
    if track == 'transfer' and college.transfer_friendly is not None:
        practical_score = 1.0 if college.transfer_friendly else 0.0

    total = (
        academics_score * weights.get('academics', 0)
        + campus_score * weights.get('campus', 0)
        + cost_score * weights.get('cost', 0)
        + social_score * weights.get('social', 0)
        + practical_score * weights.get('practical', 0)
    )

    penalty = 0.0
    if track == 'transfer' and pain_points:
        if 'too_party' in pain_points and college.party_score is not None and college.party_score > 7:
            penalty += 0.15
        if 'too_big' in pain_points and college.student_size is not None and college.student_size > 150:
            penalty += 0.15
        if (
            'commuter' in pain_points
            and college.residential_rate is not None
            and college.residential_rate < 40
        ):
            penalty += 0.1

    match_score = max(0.0, total - penalty)
    matching_factors, mismatches = _explain_factor(college, preferences, scorecard_source)
    if scorecard_source and track == 'transfer':
        matching_factors.append('Transfer acceptance data is not included in Scorecard institution data')
    elif track == 'transfer' and college.transfer_friendly:
        matching_factors.append('Generally transfer-friendly')
    elif track == 'transfer' and college.transfer_friendly is False:
        mismatches.append('May be less transfer-friendly')

    return {
        'id': college.id,
        'name': college.name,
        'location': college.location,
        'state': college.state,
        'match_percentage': round(match_score * 100, 1),
        'explanation': 'Match scores reflect your stated priorities and reported college data where available.',
        'matching_factors': matching_factors,
        'mismatches': mismatches,
        'transfer_friendly': college.transfer_friendly,
        'scorecard_details': college.scorecard_details,
    }


def _local_colleges():
    return [
        MatchCollege(
            id=college.id,
            name=college.name,
            location=college.location,
            state=(
                college.location.rsplit(',', 1)[-1].strip().upper()
                if ',' in college.location
                and college.location.rsplit(',', 1)[-1].strip().upper() in US_STATE_CODES
                else None
            ),
            setting=college.setting or None,
            student_size=college.class_size_avg,
            party_score=college.party_score,
            net_price_estimate=college.net_price_estimate,
            transfer_friendly=college.transfer_friendly,
            majors=college.majors,
            residential_rate=college.residential_rate,
        )
        for college in College.objects.all()
    ]


def _scorecard_colleges(records):
    colleges = []
    for record in records:
        school = normalize_school(record)
        if school is None:
            continue
        colleges.append(MatchCollege(
            id=school['id'],
            name=school['name'],
            location=school['location'],
            state=school['state'],
            setting=school['setting'],
            student_size=school['student_size'],
            party_score=None,
            net_price_estimate=school['net_price'],
            transfer_friendly=None,
            majors=None,
            residential_rate=None,
            scorecard_details={
                key: school[key]
                for key in (
                    'student_size',
                    'net_price',
                    'tuition_in_state',
                    'tuition_out_state',
                    'admit_rate',
                )
                if school[key] is not None
            },
        ))
    return colleges


@api_view(['POST'])
def calculate_matches(request):
    data = request.data
    track = data.get('track', 'freshman')
    preferences = data.get('preferences', {})
    importance = data.get('importance')
    if importance is not None:
        importance_keys = {'academics', 'campus', 'location', 'cost', 'student_life'}
        if not isinstance(importance, dict):
            return Response(
                {'status': 'error', 'detail': 'importance must be an object with ratings from 1 to 5.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if any(
            key in importance_keys
            and (
                isinstance(value, bool)
                or not isinstance(value, int)
                or not 1 <= value <= 5
            )
            for key, value in importance.items()
        ):
            return Response(
                {'status': 'error', 'detail': 'Each importance rating must be a whole number from 1 to 5.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        importance = {key: importance.get(key, 3) for key in importance_keys}
    weights = data.get('weights', {
        'academics': 0.3,
        'campus': 0.2,
        'cost': 0.2,
        'social': 0.15,
        'practical': 0.15,
    })
    if importance is not None:
        adjusted_weights = weights.copy()
        adjusted_weights['academics'] = weights.get('academics', 0) * importance['academics'] / 3
        adjusted_weights['practical'] = weights.get('practical', 0) * importance['academics'] / 3
        adjusted_weights['cost'] = weights.get('cost', 0) * importance['cost'] / 3
        adjusted_weights['social'] = weights.get('social', 0) * importance['student_life'] / 3
        setting_pref = preferences.get('setting')
        campus_preferences = (
            preferences.get('student_size_max', preferences.get('class_size_max')) is not None
            or preferences.get('residential_rate') is not None
        )
        campus_importance = []
        if campus_preferences:
            campus_importance.append(importance['campus'])
        if setting_pref:
            campus_importance.append(importance['location'])
        if not campus_importance:
            campus_importance = [importance['campus'], importance['location']]
        adjusted_weights['campus'] = (
            weights.get('campus', 0) * sum(campus_importance) / (3 * len(campus_importance))
        )
        total_weight = sum(adjusted_weights.values())
        if total_weight > 0:
            weights = {key: value / total_weight for key, value in adjusted_weights.items()}
        else:
            weights = adjusted_weights
    pain_points = data.get('painPoints', [])

    scorecard_source = bool(getattr(settings, 'SCORECARD_API_KEY', ''))
    notice = None
    if scorecard_source:
        try:
            colleges = _scorecard_colleges(get_scorecard_schools())
        except ScorecardError as error:
            return Response(
                {'status': 'error', 'detail': str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        if not colleges:
            return Response(
                {'status': 'error', 'detail': 'College Scorecard returned no active institutions.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        source = 'college_scorecard'
        notice = (
            'Data source: U.S. Department of Education College Scorecard. Program offerings, '
            'social scene, housing, and transfer acceptance are not in the institution data '
            'used here, so those preferences are not scored. Verify current costs and details '
            'with each college.'
        )
    else:
        colleges = _local_colleges()
        source = 'local'
        notice = (
            'College Scorecard is not configured yet; these results use the locally stored '
            'college list. Set SCORECARD_API_KEY to use current U.S. Department of Education data.'
        )

    if preferences.get('pre_med_track'):
        notice += ' Your pre-med interest is noted, but pre-med advising and preparation are not included in this match score.'

    state_preference = preferences.get('state')
    if state_preference:
        state_preference = str(state_preference).strip().upper()
        if state_preference not in US_STATE_CODES:
            state_preference = None
        else:
            if not scorecard_source:
                notice += ' Local records are matched by state only when their location includes a U.S. state abbreviation.'
            colleges = [college for college in colleges if college.state == state_preference]

    results = [
        _score_college(college, preferences, weights, track, pain_points, scorecard_source, importance)
        for college in colleges
    ]
    results.sort(key=lambda result: result['match_percentage'], reverse=True)
    if not state_preference:
        diverse_results = []
        other_results = []
        seen_states = set()
        for result in results:
            state = result['state']
            if state and state not in seen_states:
                seen_states.add(state)
                diverse_results.append(result)
            else:
                other_results.append(result)
        results = diverse_results + other_results
    return Response({
        'status': 'success',
        'source': source,
        'notice': notice,
        'matches': results[:5],
    })


@api_view(['GET'])
def list_colleges(request):
    scorecard_source = bool(getattr(settings, 'SCORECARD_API_KEY', ''))
    if scorecard_source:
        try:
            colleges = _scorecard_colleges(get_scorecard_schools())
        except ScorecardError as error:
            return Response(
                {'status': 'error', 'detail': str(error)},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        source = 'college_scorecard'
        notice = 'Data source: U.S. Department of Education College Scorecard.'
    else:
        colleges = _local_colleges()
        source = 'local'
        notice = (
            'Showing locally stored institution records. Configure SCORECARD_API_KEY to use '
            'current U.S. Department of Education data.'
        )

    query = request.query_params.get('q', '').strip().casefold()
    setting = request.query_params.get('setting', '').strip().casefold()
    try:
        max_price = int(request.query_params['max_price']) if request.query_params.get('max_price') else None
    except ValueError:
        return Response(
            {'status': 'error', 'detail': 'max_price must be a whole number.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if max_price is not None and max_price < 0:
        return Response(
            {'status': 'error', 'detail': 'max_price cannot be negative.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    colleges = [college for college in colleges if (
        (not query or query in college.name.casefold() or query in college.location.casefold())
        and (not setting or (college.setting or '').casefold() == setting)
        and (max_price is None or (
            college.net_price_estimate is not None and college.net_price_estimate <= max_price
        ))
    )]
    if source == 'college_scorecard':
        colleges.sort(key=lambda college: college.student_size or 0, reverse=True)
    else:
        colleges.sort(key=lambda college: college.name.casefold())

    try:
        page = max(1, int(request.query_params.get('page', '1')))
        page_size = min(100, max(1, int(request.query_params.get('page_size', '24'))))
    except ValueError:
        return Response(
            {'status': 'error', 'detail': 'page and page_size must be whole numbers.'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    count = len(colleges)
    start = (page - 1) * page_size
    results = [{
        'id': college.id,
        'name': college.name,
        'location': college.location,
        'state': college.state,
        'setting': college.setting,
        'student_size': college.student_size,
        'net_price': college.net_price_estimate,
        'tuition_in_state': (college.scorecard_details or {}).get('tuition_in_state'),
        'tuition_out_state': (college.scorecard_details or {}).get('tuition_out_state'),
    } for college in colleges[start:start + page_size]]

    return Response({
        'status': 'success',
        'source': source,
        'notice': notice,
        'count': count,
        'page': page,
        'page_size': page_size,
        'pages': ceil(count / page_size),
        'results': results,
    })


@api_view(['POST'])
@throttle_classes([AIInsightThrottle])
def generate_ai_insights(request):
    preferences = request.data.get('preferences', {})
    track = request.data.get('track', 'freshman')
    pain_points = request.data.get('painPoints', [])
    matches = request.data.get('matches', [])
    importance = request.data.get('importance')
    try:
        insights = generate_fit_insights(preferences, track, pain_points, matches, importance)
    except AIInsightError as error:
        return Response(
            {'status': 'error', 'detail': str(error)},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )
    return Response({'status': 'success', 'insights': insights})


generate_ai_insights.cls.throttle_scope = 'ai_insights'
