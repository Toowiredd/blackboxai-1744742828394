import os
import json
from flask import Blueprint, request, jsonify, current_app
from flask_socketio import emit

api_bp = Blueprint('api', __name__)

BUTTON_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'button_config.json')

def load_button_config():
    if not os.path.exists(BUTTON_CONFIG_FILE):
        return {}
    with open(BUTTON_CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_button_config(config):
    with open(BUTTON_CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

@api_bp.route('/button/config', methods=['POST'])
def update_button_config():
    """Validate and persist button configuration updates."""
    try:
        data = request.get_json()
        # Basic validation
        if not data or 'id' not in data:
            return jsonify({'status': 'error', 'message': 'Invalid button config data'}), 400

        config = load_button_config()
        config[data['id']] = data

        save_button_config(config)

        # Emit update to all clients
        emit('button_config_updated', data, broadcast=True, namespace='/')

        return jsonify({'status': 'success', 'data': data})
    except Exception as e:
        current_app.logger.error(f"Error updating button configuration: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@api_bp.route('/button/config', methods=['GET'])
def get_button_config():
    """Retrieve all saved button configurations."""
    try:
        config = load_button_config()
        return jsonify({'status': 'success', 'data': config})
    except Exception as e:
        current_app.logger.error(f"Error retrieving button configuration: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
