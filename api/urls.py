from django.urls import path
from .views import calculate_matches

urlpatterns = [
    path('match/', calculate_matches, name='calculate_matches'),
]