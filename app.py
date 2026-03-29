from flask import Flask, jsonify, send_from_directory
from extensions import db, jwt, bcrypt, cors
from routes.auth import auth_bp
from routes.tasks import tasks_bp
import os

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'dev-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///primetrade.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'jwt-secret-key'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400

    db.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    cors.init_app(app)

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/v1/tasks')

    @app.route('/')
    def frontend():
        return send_from_directory('frontend', 'index.html')

    @app.route('/api/v1/health')
    def health():
        return jsonify({'status': 'ok', 'message': 'API is running'}), 200

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @jwt.unauthorized_loader
    def unauthorized(e):
        return jsonify({'error': 'Missing or invalid token'}), 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_data):
        return jsonify({'error': 'Token expired, please login again'}), 401

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

    


