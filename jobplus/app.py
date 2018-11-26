import datetime
from flask import Flask
from flask_migrate import Migrate
from jobplus.config import configs
from jobplus.models import db, User
from flask_login import LoginManager


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    
    register_extensions(app)
    
    return app