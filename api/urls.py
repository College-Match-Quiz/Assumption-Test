from django.urls import path
from .views import calculate_matches, list_colleges

urlpatterns = [
    path('colleges/', list_colleges, name='list_colleges'),
    path('match/', calculate_matches, name='calculate_matches'),
]