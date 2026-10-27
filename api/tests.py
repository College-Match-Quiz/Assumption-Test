from rest_framework import status
from rest_framework.test import APITestCase
from unittest.mock import patch

from .models import College
from .scorecard import ScorecardError


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
		self.assertEqual(response.data['source'], 'local')
		self.assertIn('Student population is within your preferred size', matches[0]['matching_factors'])
		large_match = next(match for match in matches if match['id'] == self.large_class.id)
		self.assertIn('Student population is above your preferred size', large_match['mismatches'])

	@patch('api.views.get_scorecard_schools')
	def test_scorecard_data_is_used_for_matches(self, get_scorecard_schools):
		get_scorecard_schools.return_value = [
			{
				'id': 101,
				'school.name': 'Small City College',
				'school.city': 'Boston',
				'school.state': 'MA',
				'school.locale': 11,
				'school.ownership': 1,
				'latest.student.size': 4000,
				'latest.cost.avg_net_price.public': 12000,
				'latest.admissions.admission_rate.overall': 0.4,
			},
			{
				'id': 102,
				'school.name': 'Large Rural College',
				'school.city': 'Ruralville',
				'school.state': 'VT',
				'school.locale': 43,
				'school.ownership': 1,
				'latest.student.size': 25000,
				'latest.cost.avg_net_price.public': 28000,
				'latest.admissions.admission_rate.overall': 0.6,
			},
		]

		with self.settings(SCORECARD_API_KEY='test-key'):
			response = self.client.post('/api/match/', {
				'track': 'freshman',
				'preferences': {
					'setting': 'urban',
					'student_size_max': 5000,
					'max_tuition': 15000,
				},
				'weights': {
					'academics': 0,
					'campus': 0.5,
					'cost': 0.5,
					'social': 0,
					'practical': 0,
				},
			}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['source'], 'college_scorecard')
		self.assertEqual(response.data['matches'][0]['id'], 101)
		self.assertEqual(response.data['matches'][0]['location'], 'Boston, MA')
		self.assertEqual(response.data['matches'][0]['scorecard_details'], {
			'student_size': 4000,
			'net_price': 12000,
			'admit_rate': 0.4,
		})
		self.assertIn('College Scorecard', response.data['notice'])
		get_scorecard_schools.assert_called_once_with()

	@patch('api.views.get_scorecard_schools', side_effect=ScorecardError('Scorecard unavailable'))
	def test_scorecard_errors_are_reported_instead_of_using_local_data(self, get_scorecard_schools):
		with self.settings(SCORECARD_API_KEY='test-key'):
			response = self.client.post('/api/match/', {}, format='json')

		self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
		self.assertEqual(response.data['detail'], 'Scorecard unavailable')
		get_scorecard_schools.assert_called_once_with()
