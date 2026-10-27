from dataclasses import dataclass

from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import College
from .scorecard import ScorecardError, get_scorecard_schools, normalize_school


@dataclass
class MatchCollege:
    id: int | str
    name: str
    location: str
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


def _score_college(college, preferences, weights, track, pain_points, scorecard_source):
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
        campus_scores.append(1.0 if college.setting == setting_pref else 0.0)
    desired_residential = preferences.get('residential_rate')
    if desired_residential is not None and college.residential_rate is not None:
        campus_scores.append(max(0, 1 - abs(college.residential_rate - desired_residential) / 100))
    student_size_max = preferences.get('student_size_max', preferences.get('class_size_max'))
    if student_size_max is not None and college.student_size is not None:
        size_score = 1 - max(0, college.student_size - student_size_max) / max(1, student_size_max)
        campus_scores.append(max(0.0, size_score))
    campus_score = sum(campus_scores) / len(campus_scores) if campus_scores else 0.5

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
        'match_percentage': round(match_score * 100, 1),
        'explanation': 'Match score uses reported College Scorecard cost, enrollment, and campus location data where available.',
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
    weights = data.get('weights', {
        'academics': 0.3,
        'campus': 0.2,
        'cost': 0.2,
        'social': 0.15,
        'practical': 0.15,
    })
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

    results = [
        _score_college(college, preferences, weights, track, pain_points, scorecard_source)
        for college in colleges
    ]
    results.sort(key=lambda result: result['match_percentage'], reverse=True)
    return Response({
        'status': 'success',
        'source': source,
        'notice': notice,
        'matches': results[:5],
    })
