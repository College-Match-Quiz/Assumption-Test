from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import College
from django.db.models import Q

def _parse_majors(text):
    return [m.strip().lower() for m in text.split(',') if m.strip()]

def _explain_factor(college, preferences):
    matches = []
    mismatches = []
    # setting
    pref_setting = preferences.get('setting')
    if pref_setting:
        if college.setting == pref_setting:
            matches.append('Setting matches preference')
        else:
            mismatches.append('Different campus setting')
    # majors
    majors_pref = preferences.get('majors', [])
    if majors_pref:
        college_majors = _parse_majors(college.majors)
        intersect = [m for m in majors_pref if m.lower() in college_majors]
        if intersect:
            matches.append(f"Offers majors: {', '.join(intersect)}")
        else:
            mismatches.append('Does not offer preferred majors')
    # party / vibe
    party_pref = preferences.get('party_pref')
    if party_pref:
        if party_pref == 'low' and (college.party_score or 5) > 7:
            mismatches.append('High party culture')
        if party_pref == 'high' and (college.party_score or 5) < 4:
            mismatches.append('Low party culture')
        else:
            matches.append('Vibe aligns with party preference')
    # cost
    max_tuition = preferences.get('max_tuition')
    if max_tuition is not None and college.net_price_estimate is not None:
        if college.net_price_estimate <= max_tuition:
            matches.append('Estimated net price within budget')
        else:
            mismatches.append('Estimated net price may exceed budget')
    return matches, mismatches

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
        'practical': 0.15
    })
    pain_points = data.get('painPoints', [])

    colleges = College.objects.all()
    results = []

    for college in colleges:
        # compute category scores 0..1
        # academics: preferred majors
        academics_score = 0.0
        pref_majors = preferences.get('majors', [])
        if pref_majors and college.majors:
            college_majors = _parse_majors(college.majors)
            matched = sum(1 for m in pref_majors if m.lower() in college_majors)
            academics_score = min(1.0, matched / max(1, len(pref_majors)))

        # campus: setting and residential rate
        campus_score = 0.0
        setting_pref = preferences.get('setting')
        if setting_pref and college.setting:
            campus_score += 0.6 if college.setting == setting_pref else 0.0
        if college.residential_rate is not None:
            desired_res = preferences.get('residential_rate')
            if desired_res is not None:
                # proximity in percentage
                campus_score += max(0, 1 - abs(college.residential_rate - desired_res) / 100) * 0.4

        # cost
        cost_score = 0.0
        max_tuition = preferences.get('max_tuition')
        if max_tuition is not None and college.net_price_estimate is not None:
            cost_score = 1.0 if college.net_price_estimate <= max_tuition else max(0.0, 1 - (college.net_price_estimate - max_tuition) / max_tuition)

        # social
        social_score = 0.5
        party_pref = preferences.get('party_pref')
        if party_pref and college.party_score is not None:
            if party_pref == 'low':
                social_score = max(0.0, 1 - (college.party_score or 5) / 10)
            elif party_pref == 'high':
                social_score = min(1.0, (college.party_score or 5) / 10)

        # practical
        practical_score = 0.5
        # transfer friendliness
        if track == 'transfer':
            practical_score = 1.0 if college.transfer_friendly else 0.0

        # weighted sum
        total = (
            academics_score * weights.get('academics', 0)
            + campus_score * weights.get('campus', 0)
            + cost_score * weights.get('cost', 0)
            + social_score * weights.get('social', 0)
            + practical_score * weights.get('practical', 0)
        )

        # apply transfer pain-point penalties
        penalty = 0.0
        if track == 'transfer' and pain_points:
            # example pain points: too_party, too_big, commuter
            if 'too_party' in pain_points and college.party_score and college.party_score > 7:
                penalty += 0.15
            if 'too_big' in pain_points and college.class_size_avg and college.class_size_avg > 150:
                penalty += 0.15
            if 'commuter' in pain_points and college.residential_rate is not None and college.residential_rate < 40:
                penalty += 0.1

        match_score = max(0.0, total - penalty)

        matches_expl, mismatches_expl = _explain_factor(college, preferences)
        transfer_notes = None
        if track == 'transfer':
            transfer_notes = []
            if college.transfer_friendly:
                transfer_notes.append('Generally transfer-friendly')
            else:
                transfer_notes.append('May be less transfer-friendly')
            if pain_points:
                transfer_notes.append('Penalties applied for reported dislikes')

        results.append({
            'id': college.id,
            'name': college.name,
            'match_percentage': round(match_score * 100, 1),
            'explanation': 'Score composed from academics, campus, cost, social, practical factors',
            'matching_factors': matches_expl,
            'mismatches': mismatches_expl,
            'transfer_notes': transfer_notes,
            'transfer_friendly': college.transfer_friendly
        })

    results.sort(key=lambda x: x['match_percentage'], reverse=True)
    return Response({'status': 'success', 'matches': results[:5]})