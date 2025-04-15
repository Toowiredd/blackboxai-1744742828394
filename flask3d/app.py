import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['DEBUG'] = True

# Enable CORS for all routes
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "allow_headers": ["Content-Type"],
        "methods": ["GET", "POST", "OPTIONS"]
    }
})

# Initialize SocketIO with eventlet and CORS
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='eventlet',
    logger=True,
    engineio_logger=True,
    ping_timeout=60,
    ping_interval=25,
    max_http_buffer_size=1e8,
    async_handlers=True
)

@socketio.on_error()
def error_handler(e):
    """Handle all socket.io errors."""
    logger.error(f"SocketIO error: {str(e)}")
    return {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    """Serve the main 3D environment page."""
    return render_template('index.html')

@app.route('/api/button/config', methods=['POST'])
def update_button_config():
    """Update button configuration."""
    try:
        data = request.get_json()
        if not data or 'id' not in data:
            raise ValueError('Invalid button configuration: missing id')
        
        required_fields = ['position', 'rotation', 'scale']
        for field in required_fields:
            if field not in data:
                data[field] = {'x': 0, 'y': 0, 'z': 0} if field != 'scale' else 1
                logger.warning(f"Missing {field} in button config, using default")
        
        logger.info(f"Received button config update: {data}")
        socketio.emit('button_config_updated', data)
        return jsonify({'status': 'success', 'data': data})
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except Exception as e:
        logger.error(f"Error updating button configuration: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/browser/capture', methods=['POST'])
def capture_browser():
    """Capture headless browser content."""
    try:
        data = request.get_json()
        url = data.get('url')
        # TODO: Implement headless browser capture
        logger.info(f"Capturing content from URL: {url}")
        return jsonify({'status': 'success', 'url': url})
    except Exception as e:
        logger.error(f"Error capturing browser content: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info('Client connected')
    emit('connection_response', {'status': 'connected'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info('Client disconnected')

@socketio.on('button_interaction')
def handle_button_interaction(data):
    """Handle button interactions (hover, click, etc.)."""
    try:
        if not data or 'type' not in data or 'button_id' not in data:
            raise ValueError('Invalid button interaction data')
            
        interaction_type = data.get('type')
        button_id = data.get('button_id')
        logger.info(f"Button interaction: {interaction_type} on button {button_id}")
        
        # Broadcast the interaction to all clients with correct data structure
        emit('button_state_changed', {
            'id': button_id,  # Changed from button_id to id
            'state': interaction_type,  # Changed from type to state
            'status': 'success'
        }, broadcast=True)
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        emit('button_state_changed', {
            'status': 'error',
            'message': str(e)
        })
    except Exception as e:
        logger.error(f"Error handling button interaction: {str(e)}")
        emit('button_state_changed', {
            'status': 'error',
            'message': str(e)
        })

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Not found', 'message': 'The requested resource does not exist'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    return jsonify({'error': 'Internal server error', 'message': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, debug=True, host='0.0.0.0', port=port)
