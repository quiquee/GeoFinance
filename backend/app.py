from flask import Flask, send_from_directory, request, render_template, session
import os
from config import Config
from models import db
from routes.main import main_bp
from routes.accounts_routes import accounts_bp  # For account operations
from routes.journal_routes import journal_bp  # For journal operations
from routes.ledger_routes import ledger_bp  # For ledger operations
from routes.apitest_endpoints import apitest_bp
from routes.auth_routes import auth_bp  # Import the authentication routes
from datetime import timedelta

# Define the path to the webapp directory relative to the backend directory
webapp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'webapp'))

def create_app(config_class=Config):
    # Configure static folder to point to the webapp directory
    app = Flask(__name__, static_folder=webapp_dir, static_url_path='')
    app.config.from_object(config_class)
    
    # Configure session
    app.secret_key = os.environ.get('SECRET_KEY', 'dev_secret_key')
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # Session lasts 7 days

    db.init_app(app)

    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()

    # Add a global after_request handler to add CORS headers manually
    @app.after_request
    def add_cors_headers(response):
        response.headers.add('Access-Control-Allow-Origin', 'http://127.0.0.1:5173')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        
        # Handle preflight OPTIONS requests
        if request.method == 'OPTIONS':
            return response
            
        return response

    # Register the API blueprints
    app.register_blueprint(main_bp, url_prefix='/api')
    app.register_blueprint(accounts_bp, url_prefix='/api/ledger/accounts')  # Account CRUD operations
    app.register_blueprint(journal_bp, url_prefix='/api/ledger/journal')  # Journal entry operations
    app.register_blueprint(ledger_bp, url_prefix='/api/ledger')  # Ledger management & reports
    app.register_blueprint(apitest_bp)  # Register apitest blueprint
    app.register_blueprint(auth_bp)  # Register authentication routes

    # Route to serve the index.html from the webapp directory
    @app.route('/')
    def serve_index():
        return send_from_directory(app.static_folder, 'index.html')

    # Route to serve apitest.html from the templates directory
    @app.route('/apitest')
    def serve_apitest():
        return render_template('apitest.html')

    # Handle OPTIONS requests for CORS preflight
    @app.route('/api/login', methods=['OPTIONS'])
    def options_login():
        response = app.make_default_options_response()
        return response

    # Optional: Route to handle client-side routing (if you use a JS framework later)
    @app.errorhandler(404)
    def not_found(e):
        # If the path doesn't match an API route or a static file, serve index.html
        if not request.path.startswith('/api/'):
            return send_from_directory(app.static_folder, 'index.html')
        # Otherwise, it's a real 404 for an API endpoint
        return e

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
