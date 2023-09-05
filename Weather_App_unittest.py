import unittest
import mock
from unittest.mock import patch
from flask import Flask, session, jsonify, request
from Weather_App import app, validate_location, forecast_data, forecast

class TestWeatherApp(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app.config['SECRET_KEY'] = 'your_secret_key_here'  # Set the secret key
        self.client = self.app.test_client()
        self.client.testing = True

    # User Authentication
    @patch('requests.post')
    def test_successful_login(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'username': 'test_user'}
        with self.client.session_transaction() as sess:
            sess['username'] = None
        response = self.client.post('/', data={'username': 'test_user', 'password': 'test_pass'})
        with self.client.session_transaction() as sess:
            self.assertEqual(sess['username'], 'test_user')

    # Registering a user
    @patch('requests.post')
    @patch('requests.get')
    def test_successful_register(self, mock_get, mock_post):
        mock_get.return_value.status_code = 404  # No existing user
        mock_post.return_value.status_code = 201  # Created
        response = self.client.post('/register', data={
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'test_user',
            'profile_image': 'user_bright.png',
            'email': 'test@email.com',
            'password': 'test_pass'
        })
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to /home

    # Home Page
    @patch('requests.get')
    def test_home_page_access(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'username': 'test_user'}
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = self.client.get('/home')
        self.assertEqual(response.status_code, 200)

    # Modify Favorites
    @patch('requests.post')
    @patch('requests.delete')
    def test_modify_favorites(self, mock_delete, mock_post):
        mock_post.return_value.status_code = 200
        mock_delete.return_value.status_code = 200
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = self.client.post('/modify_favorites', data={'action': 'add', 'zip_data': '12345'})
        self.assertEqual(response.status_code, 302)  # Expecting a redirect to /home

    # Town Page
    def test_town_page(self):
        response = self.client.get('/town', query_string={'searched_town': '12345'})
        self.assertEqual(response.status_code, 200)

    # Auxiliary Functions
    def test_validate_location(self):
        self.assertTrue(validate_location('10001'))
        self.assertFalse(validate_location('invalid_zip'))


if __name__ == "__main__":
    unittest.main()
