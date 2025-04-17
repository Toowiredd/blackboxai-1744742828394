import unittest
from flask import Flask
from flask_login import LoginManager, UserMixin
from flask3d.app import app, socketio

class User(UserMixin):
    def __init__(self, id):
        self.id = id

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

        # Set up Flask-Login
        self.login_manager = LoginManager()
        self.login_manager.init_app(self.app)
        self.login_manager.user_loader(self.load_user)

    def load_user(self, user_id):
        return User(user_id)

    def test_login(self):
        response = self.client.post('/login', json={'username': 'admin', 'password': 'password'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_login_invalid_credentials(self):
        response = self.client.post('/login', json={'username': 'admin', 'password': 'wrongpassword'})
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json['status'], 'error')

    def test_logout(self):
        self.client.post('/login', json={'username': 'admin', 'password': 'password'})
        response = self.client.post('/logout')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_update_button_config(self):
        self.client.post('/login', json={'username': 'admin', 'password': 'password'})
        response = self.client.post('/api/button/config', json={
            'id': 'button1',
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')

    def test_capture_browser(self):
        self.client.post('/login', json={'username': 'admin', 'password': 'password'})
        response = self.client.post('/api/browser/capture', json={'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('content', response.json)

if __name__ == '__main__':
    unittest.main()
