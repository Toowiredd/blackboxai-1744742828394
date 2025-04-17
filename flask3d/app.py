import eventlet
eventlet.monkey_patch()

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import logging
import os
import subprocess

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
    r"/*": {
        "origins": "*",
        "allow_headers": ["Content-Type"],
        "methods": ["GET", "POST", "OPTIONS"],
        "expose_headers": ["Content-Type"]
    }
})

# Configure static files with proper MIME types
@app.after_request
def add_header(response):
    if response.mimetype == 'application/javascript':
        response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

# Serve JavaScript modules with proper MIME type
@app.route('/static/js/<path:filename>')
def serve_js(filename):
    logger.info(f"Serving JavaScript file: {filename}")
    response = send_from_directory('static/js', filename)
    if filename.endswith('.js'):
        response.headers['Content-Type'] = 'application/javascript; charset=utf-8'
    return response

# Debug route to check module loading
@app.route('/debug/modules')
def debug_modules():
    """List all available JavaScript modules."""
    js_dir = os.path.join(app.static_folder, 'js')
    files = []
    for file in os.listdir(js_dir):
        if file.endswith('.js'):
            with open(os.path.join(js_dir, file), 'r') as f:
                content = f.read()
                files.append({
                    'name': file,
                    'size': len(content),
                    'imports': [line for line in content.split('\n') if line.startswith('import')]
                })
    return jsonify(files)

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

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@socketio.on_error()
def error_handler(e):
    """Handle all socket.io errors."""
    logger.error(f"SocketIO error: {str(e)}")
    return {'status': 'error', 'message': str(e)}

@app.route('/')
def index():
    """Serve the main 3D environment page."""
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    # TODO: Implement proper authentication
    if username == 'admin' and password == 'password':
        user = User(id=1)
        login_user(user)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return jsonify({'status': 'success'})

@app.route('/api/button/config', methods=['POST'])
@login_required
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
@login_required
def capture_browser():
    """Capture headless browser content."""
    try:
        data = request.get_json()
        url = data.get('url')
        if not url:
            raise ValueError('URL is required for browser capture')
        
        # Use Puppeteer to capture the browser content
        result = subprocess.run(['node', 'capture.js', url], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"Failed to capture browser content: {result.stderr}")
        
        logger.info(f"Captured content from URL: {url}")
        return jsonify({'status': 'success', 'content': result.stdout})
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 400
    except RuntimeError as e:
        logger.error(f"Runtime error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
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
    try:
        # Get port from environment or use default
        port = int(os.environ.get('PORT', 5000))
        
        # Log startup information
        logger.info(f"Starting server on port {port}")
        logger.info(f"SocketIO async mode: {socketio.async_mode}")
        logger.info(f"Debug mode: {app.debug}")
        
        # Create eventlet WSGI server
        eventlet.wsgi.server(
            eventlet.listen(('0.0.0.0', port)),
            app,
            log_output=True,
            debug=app.debug,
            log=logger
        )
    except Exception as e:
        logger.error(f"Failed to start server: {str(e)}")
        raise
