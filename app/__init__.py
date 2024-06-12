from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    CORS(app)
    db.init_app(app)

    with app.app_context():
        from .models import User, KeyValue
        db.create_all()

        if not User.query.filter_by(username='admin').first():
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', password=generate_password_hash('admin'), is_admin=True, password_reset=False)
            db.session.add(admin)
            db.session.commit()

        from .routes import main, auth, api
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(api.bp)

    return app
