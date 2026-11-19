from django.urls import path
from .views import calculate_matches, generate_ai_insights, list_colleges

urlpatterns = [
    path('colleges/', list_colleges, name='list_colleges'),
    path('match/', calculate_matches, name='calculate_matches'),
    path('insights/', generate_ai_insights, name='generate_ai_insights'),
]