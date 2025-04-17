import os
import json
import unittest
from flask import Flask
from flask_socketio import SocketIO
from flask3d.api_routes import api_bp, BUTTON_CONFIG_FILE, load_button_config, save_button_config

class TestApiRoutes(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test_secret'
        self.socketio = SocketIO(self.app)
        self.app.register_blueprint(api_bp)
        self.client = self.app.test_client()

        # Create a temporary button config file for testing
        self.temp_button_config_file = BUTTON_CONFIG_FILE + '.test'
        self.app.config['BUTTON_CONFIG_FILE'] = self.temp_button_config_file

    def tearDown(self):
        # Remove the temporary button config file after each test
        if os.path.exists(self.temp_button_config_file):
            os.remove(self.temp_button_config_file)

    def test_update_button_config(self):
        # Test valid button config update
        response = self.client.post('/button/config', json={
            'id': 'button1',
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': 1
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('button1', load_button_config())

        # Test invalid button config update (missing id)
        response = self.client.post('/button/config', json={
            'position': {'x': 1, 'y': 2, 'z': 3},
            'rotation': {'x': 0, 'y': 0, 'z': 0},
            'scale': 1
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json['status'], 'error')

    def test_get_button_config(self):
        # Test retrieving button config
        save_button_config({'button1': {'id': 'button1', 'position': {'x': 1, 'y': 2, 'z': 3}, 'rotation': {'x': 0, 'y': 0, 'z': 0}, 'scale': 1}})
        response = self.client.get('/button/config')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('button1', response.json['data'])

    def test_capture_browser(self):
        # Test headless browser capture
        response = self.client.post('/api/browser/capture', json={'url': 'http://example.com'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['status'], 'success')
        self.assertIn('content', response.json)

if __name__ == '__main__':
    unittest.main()
