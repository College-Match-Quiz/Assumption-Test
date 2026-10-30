from django.contrib.auth import get_user_model
from django.test import TestCase


class AccountFlowTests(TestCase):
    def test_university_directory_page_loads(self):
        response = self.client.get('/universities/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'directory-filters')

    def test_homepage_view_all_links_to_directory(self):
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/universities/"')

    def test_quiz_includes_additional_major_choices(self):
        response = self.client.get('/quiz/')

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Accounting"')
        self.assertContains(response, 'value="Environmental Science"')
        self.assertContains(response, 'value="Public Health"')

    def test_signup_creates_account_and_logs_user_in(self):
        response = self.client.post('/signup/', {
            'username': 'newstudent',
            'password1': 'A-strong-test-password-482!',
            'password2': 'A-strong-test-password-482!',
        })

        self.assertRedirects(response, '/')
        user = get_user_model().objects.get(username='newstudent')
        self.assertEqual(int(self.client.session['_auth_user_id']), user.pk)

    def test_login_accepts_valid_credentials(self):
        get_user_model().objects.create_user(
            username='returningstudent',
            password='A-strong-test-password-482!',
        )

        response = self.client.post('/login/', {
            'username': 'returningstudent',
            'password': 'A-strong-test-password-482!',
        })

        self.assertRedirects(response, '/')
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post('/login/', {
            'username': 'missingstudent',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
        self.assertNotIn('_auth_user_id', self.client.session)