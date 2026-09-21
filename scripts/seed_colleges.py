"""Seed script for simple sample colleges.
Run with: .venv\Scripts\python.exe scripts\seed_colleges.py
"""
import os
import django
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

django.setup()

from api.models import College

SAMPLES = [
    {
        'name': 'Northwood State',
        'location': 'Northwood, State',
        'setting': 'suburban',
        'class_size_avg': 120,
        'party_score': 4,
        'tuition_in_state': 15000,
        'tuition_out_state': 25000,
        'transfer_friendly': True,
        'majors': 'Computer Science, Engineering, Economics',
        'residential_rate': 70,
        'admit_rate': 0.45,
        'net_price_estimate': 18000,
    },
    {
        'name': 'Evergreen University',
        'location': 'Evergreen City',
        'setting': 'urban',
        'class_size_avg': 90,
        'party_score': 6,
        'tuition_in_state': 20000,
        'tuition_out_state': 30000,
        'transfer_friendly': False,
        'majors': 'Biology, Environmental Science, Computer Science',
        'residential_rate': 60,
        'admit_rate': 0.55,
        'net_price_estimate': 22000,
    },
    {
        'name': 'Hillside College',
        'location': 'Hillside',
        'setting': 'rural',
        'class_size_avg': 200,
        'party_score': 8,
        'tuition_in_state': 12000,
        'tuition_out_state': 22000,
        'transfer_friendly': False,
        'majors': 'Business, Psychology, Education',
        'residential_rate': 40,
        'admit_rate': 0.6,
        'net_price_estimate': 16000,
    },
]

for s in SAMPLES:
    obj, created = College.objects.get_or_create(name=s['name'], defaults=s)
    if created:
        print('Created', obj.name)
    else:
        print('Exists', obj.name)

print('Done')
