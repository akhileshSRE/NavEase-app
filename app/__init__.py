from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.security import generate_password_hash

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)
    db.init_app(app)

    with app.app_context():
        from .models import User, KeyValue, Organization, Team
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',  # Add a valid email
                first_name='Admin',         # Add a valid first name
                last_name='User',           # Add a valid last name
                password=generate_password_hash('admin'),
                is_admin=True,
                password_reset=False
            )
            db.session.add(admin)
            db.session.commit()

        from .routes import main, auth, api, settings
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(api.bp)
        app.register_blueprint(settings.bp)

    return app
