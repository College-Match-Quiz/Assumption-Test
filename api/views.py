from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import College

@api_view(['POST'])
def calculate_matches(request):
    data = request.data
    preferred_setting = data.get('setting')
    pain_points = data.get('painPoints', [])

    colleges = College.objects.all()
    results = []

    for college in colleges:
        score = 100
        if preferred_setting and college.setting == preferred_setting:
            score += 15
        if 'too_big' in pain_points and college.class_size_avg > 150:
            score -= 25
        if 'too_party' in pain_points and college.party_score > 7:
            score -= 20

        results.append({
            'id': college.id,
            'name': college.name,
            'match_score': max(0, min(100, score)),
            'transfer_friendly': college.transfer_friendly
        })

    results.sort(key=lambda x: x['match_score'], reverse=True)
    return Response({'status': 'success', 'matches': results[:5]})