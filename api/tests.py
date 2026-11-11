import json
from rest_framework import status
from rest_framework.test import APITestCase
from django.test import override_settings
from django.core.cache import cache
from unittest.mock import patch

from .models import College
from .insights import generate_fit_insights
from .scorecard import CACHE_KEY, ScorecardError, get_scorecard_schools


@override_settings(SCORECARD_API_KEY='')
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

	def test_importance_ratings_change_match_ranking(self):
		expensive_small = College.objects.create(
			name='Expensive Small College',
			location='North',
			setting='urban',
			class_size_avg=500,
			party_score=5,
			net_price_estimate=50000,
		)
		affordable_large = College.objects.create(
			name='Affordable Large College',
			location='South',
			setting='urban',
			class_size_avg=5000,
			party_score=5,
			net_price_estimate=10000,
		)
		payload = {
			'track': 'freshman',
			'preferences': {'student_size_max': 1000, 'max_tuition': 20000},
		}

		campus_focused = self.client.post('/api/match/', {
			**payload,
			'importance': {'campus': 5, 'cost': 1},
		}, format='json')
		cost_focused = self.client.post('/api/match/', {
			**payload,
			'importance': {'campus': 1, 'cost': 5},
		}, format='json')

		self.assertEqual(campus_focused.status_code, status.HTTP_200_OK)
		self.assertEqual(cost_focused.status_code, status.HTTP_200_OK)
		campus_order = [match['id'] for match in campus_focused.data['matches']]
		cost_order = [match['id'] for match in cost_focused.data['matches']]
		self.assertLess(campus_order.index(expensive_small.id), campus_order.index(affordable_large.id))
		self.assertLess(cost_order.index(affordable_large.id), cost_order.index(expensive_small.id))

	def test_importance_ratings_must_be_between_one_and_five(self):
		response = self.client.post('/api/match/', {
			'importance': {'cost': 6},
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
		self.assertIn('whole number from 1 to 5', response.data['detail'])

	def test_neutral_importance_ratings_preserve_existing_scores(self):
		payload = {
			'track': 'freshman',
			'preferences': {'setting': 'urban', 'student_size_max': 20},
		}
		without_importance = self.client.post('/api/match/', payload, format='json')
		with_neutral_importance = self.client.post('/api/match/', {
			**payload,
			'importance': {
				'academics': 3,
				'campus': 3,
				'location': 3,
				'cost': 3,
				'student_life': 3,
			},
		}, format='json')

		self.assertEqual(with_neutral_importance.status_code, status.HTTP_200_OK)
		self.assertEqual(
			with_neutral_importance.data['matches'],
			without_importance.data['matches'],
		)

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

	@patch('api.views.get_scorecard_schools')
	def test_state_preference_filters_scorecard_matches(self, get_scorecard_schools):
		get_scorecard_schools.return_value = [
			{
				'id': 101,
				'school.name': 'Alabama College',
				'school.city': 'Birmingham',
				'school.state': 'AL',
				'school.locale': 11,
			},
			{
				'id': 102,
				'school.name': 'Vermont College',
				'school.city': 'Burlington',
				'school.state': 'VT',
				'school.locale': 11,
			},
		]

		with self.settings(SCORECARD_API_KEY='test-key'):
			response = self.client.post('/api/match/', {
				'preferences': {'state': 'vt'},
			}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual([match['name'] for match in response.data['matches']], ['Vermont College'])
		self.assertEqual(response.data['matches'][0]['state'], 'VT')

	@patch('api.views.get_scorecard_schools')
	def test_unfiltered_matches_include_multiple_states(self, get_scorecard_schools):
		get_scorecard_schools.return_value = [
			{
				'id': index,
				'school.name': f'{state} College {index}',
				'school.city': 'College Town',
				'school.state': state,
				'school.locale': 11,
			}
			for index, state in enumerate(['AL', 'AL', 'AL', 'VT', 'CA', 'WA', 'OR'])
		]

		with self.settings(SCORECARD_API_KEY='test-key'):
			response = self.client.post('/api/match/', {}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		states = [match['state'] for match in response.data['matches']]
		self.assertEqual(len(states), len(set(states)))

	@patch('api.views.get_scorecard_schools', side_effect=ScorecardError('Scorecard unavailable'))
	def test_scorecard_errors_are_reported_instead_of_using_local_data(self, get_scorecard_schools):
		with self.settings(SCORECARD_API_KEY='test-key'):
			response = self.client.post('/api/match/', {}, format='json')

		self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
		self.assertEqual(response.data['detail'], 'Scorecard unavailable')
		get_scorecard_schools.assert_called_once_with()

	def test_college_directory_returns_paginated_local_records(self):
		response = self.client.get('/api/colleges/', {'page_size': 1})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['source'], 'local')
		self.assertEqual(response.data['count'], 2)
		self.assertEqual(response.data['page_size'], 1)
		self.assertEqual(len(response.data['results']), 1)

	def test_pre_med_interest_is_acknowledged_but_not_scored(self):
		response = self.client.post('/api/match/', {
			'track': 'freshman',
			'preferences': {'pre_med_track': True},
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertIn('pre-med interest is noted', response.data['notice'])
		self.assertIn('not included in this match score', response.data['notice'])

	def test_college_directory_filters_scorecard_records(self):
		records = [{
			'id': 101,
			'school.name': 'City College',
			'school.city': 'Boston',
			'school.state': 'MA',
			'school.locale': 11,
			'school.ownership': 1,
			'latest.student.size': 4000,
			'latest.cost.avg_net_price.public': 12000,
		}]
		with self.settings(SCORECARD_API_KEY='test-key'):
			with patch('api.views.get_scorecard_schools', return_value=records):
				response = self.client.get('/api/colleges/', {'q': 'Boston', 'setting': 'urban'})

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['source'], 'college_scorecard')
		self.assertEqual(response.data['results'][0]['name'], 'City College')


@override_settings(SCORECARD_API_KEY='test-key')
class ScorecardFetchingTests(APITestCase):
	def test_fetches_all_reported_pages_and_caches_results(self):
		cache.delete(CACHE_KEY)

		def request_page(api_key, page):
			return ([{'page': page}], {'total': 250})

		with patch('api.scorecard._request_page', side_effect=request_page) as mock_request:
			schools = get_scorecard_schools()

		self.assertEqual(schools, [{'page': 0}, {'page': 1}, {'page': 2}])
		self.assertEqual(
			sorted(call.args[1] for call in mock_request.call_args_list),
			[0, 1, 2],
		)
		request_count = mock_request.call_count
		self.assertEqual(get_scorecard_schools(), schools)
		self.assertEqual(mock_request.call_count, request_count)


class AIInsightTests(APITestCase):
	def test_ai_insight_endpoint_returns_insights_for_matches(self):
		matches = [{
			'id': 101,
			'name': 'Example College',
			'location': 'Albany, NY',
			'match_percentage': 80,
			'scorecard_details': {'student_size': 5000},
			'matching_factors': ['Enrollment meets your preference'],
			'mismatches': [],
		}]
		with patch('api.views.generate_fit_insights', return_value={'101': 'A small-campus fit.'}) as generate:
			response = self.client.post('/api/insights/', {
				'track': 'freshman',
				'preferences': {'state': 'NY'},
				'importance': {'cost': 5},
				'matches': matches,
			}, format='json')

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data['insights'], {'101': 'A small-campus fit.'})
		generate.assert_called_once_with({'state': 'NY'}, 'freshman', [], matches, {'cost': 5})

	@override_settings(OPENAI_API_KEY='')
	def test_ai_insights_report_missing_key(self):
		response = self.client.post('/api/insights/', {
			'preferences': {},
			'matches': [{'id': 1, 'name': 'Example College'}],
		}, format='json')

		self.assertEqual(response.status_code, status.HTTP_503_SERVICE_UNAVAILABLE)
		self.assertIn('OPENAI_API_KEY', response.data['detail'])

	@override_settings(OPENAI_API_KEY='')
	def test_ai_insights_are_rate_limited(self):
		self.client.defaults['REMOTE_ADDR'] = '198.51.100.77'
		payload = {
			'preferences': {},
			'matches': [{'id': 1, 'name': 'Example College'}],
		}
		responses = [
			self.client.post('/api/insights/', payload, format='json').status_code
			for _ in range(6)
		]
		self.assertEqual(
			responses,
			[status.HTTP_503_SERVICE_UNAVAILABLE] * 5 + [status.HTTP_429_TOO_MANY_REQUESTS],
		)

	@override_settings(OPENAI_API_KEY='test-key', OPENAI_MODEL='test-model')
	def test_ai_service_sends_limited_quiz_context_and_parses_response(self):
		class FakeResponse:
			def __enter__(self):
				return self

			def __exit__(self, *args):
				return False

			def read(self):
				return json.dumps({
					'choices': [{
						'message': {
							'content': json.dumps({
								'insights': [{
									'id': '101',
									'insight': 'Its enrollment is within your preferred range.',
								}],
							}),
						},
					}],
				}).encode()

		matches = [{
			'id': 101,
			'name': 'Example College',
			'location': 'Albany, NY',
			'match_percentage': 80,
			'scorecard_details': {'student_size': 5000, 'untrusted': 'ignored'},
			'matching_factors': ['Enrollment meets your preference'],
			'mismatches': [],
		}]
		with patch('api.insights.urlopen', return_value=FakeResponse()) as urlopen:
			insights = generate_fit_insights(
				{'state': 'NY', 'unrelated': 'ignored'},
				'freshman',
				[],
				matches,
				{'cost': 5, 'student_life': True, 'unrecognized': 4},
			)

		request = urlopen.call_args.args[0]
		payload = json.loads(request.data)
		user_context = json.loads(payload['messages'][1]['content'])
		self.assertEqual(insights, {'101': 'Its enrollment is within your preferred range.'})
		self.assertEqual(request.get_header('Authorization'), 'Bearer test-key')
		self.assertEqual(payload['model'], 'test-model')
		self.assertEqual(user_context['preferences'], {'state': 'NY'})
		self.assertEqual(user_context['importance'], {'cost': 5})
		self.assertEqual(user_context['matches'][0]['scorecard_details'], {'student_size': 5000})
