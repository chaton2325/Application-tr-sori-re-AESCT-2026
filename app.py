from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
bcrypt = Bcrypt()
csrf = CSRFProtect()
limiter = Limiter(key_func=get_remote_address, default_limits=["500 per day", "100 per hour"])

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Register Blueprints
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.members import members_bp
    from routes.cotisations import cotisations_bp
    from routes.causes import causes_bp
    from routes.finance import finance_bp
    from routes.reports import reports_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(cotisations_bp)
    app.register_blueprint(causes_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(admin_bp)

    return app
