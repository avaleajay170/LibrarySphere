from flask import Flask, app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from app.config import config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
mail = Mail()
csrf = CSRFProtect()

login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.config['REMEMBER_COOKIE_DURATION'] = 0
    app.config['SESSION_PERMANENT'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    with app.app_context():
        from app.routes.auth import auth_bp
        from app.routes.books import books_bp
        from app.routes.members import members_bp
        from app.routes.issues import issues_bp
        from app.routes.fines import fines_bp
        from app.routes.dashboard import dashboard_bp
        from app.routes.reports import reports_bp
        from app.routes.users import users_bp

        app.register_blueprint(auth_bp)
        app.register_blueprint(books_bp)
        app.register_blueprint(members_bp)
        app.register_blueprint(issues_bp)
        app.register_blueprint(fines_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(reports_bp)
        app.register_blueprint(users_bp)

    return app