from rest_framework import status
from rest_framework.test import APITestCase

from .models import College


class CollegeMatchTests(APITestCase):
	def setUp(self):
		self.small_class = College.objects.create(
			name='Small Class College',
			location='North',
			setting='urban',
			class_size_avg=15,
			party_score=5,
			residential_rate=60,
			net_price_estimate=20000,
		)
		self.large_class = College.objects.create(
			name='Large Class College',
			location='South',
			setting='urban',
			class_size_avg=60,
			party_score=5,
			residential_rate=60,
			net_price_estimate=20000,
		)

	def test_class_size_preference_affects_ranking_and_explanation(self):
		response = self.client.post('/api/match/', {
			'track': 'freshman',
			'preferences': {'class_size_max': 20},
			'weights': {
				'academics': 0,
				'campus': 1,
				'cost': 0,
				'social': 0,
				'practical': 0,
			},
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		matches = response.data['matches']
		self.assertEqual(matches[0]['id'], self.small_class.id)
		self.assertIn('Average class size within your preference', matches[0]['matching_factors'])
		large_match = next(match for match in matches if match['id'] == self.large_class.id)
		self.assertIn('Average class size above your preferred range', large_match['mismatches'])
