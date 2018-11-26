import datetime
from flask import Flask, render_template
from flask_migrate import Migrate
from jobplus.config import configs
from jobplus.models import db, User
from flask_login import LoginManager


def register_extensions(app):
    db.init_app(app)
    Migrate(app, db)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def user_loader(id):
        return User.query.get(id)

    login_manager.login_view = 'front.login'

def register_blueprints(app):
    from .handlers import front, admin, user, company, job
    app.register_blueprint(front)
    app.register_blueprint(admin)
    app.register_blueprint(user)
    app.register_blueprint(company)
    app.register_blueprint(job)

def register_filters(app):

    @app.template_filter()
    def timesince(value):
        now = datetime.datetime.utcnow()
        delta = now - value
        if delta.days > 365:
            return '{}??'.format(delta.days // 365)
        if delta.days > 30:
            return '{}??'.format(delta.days // 30)
        if delta.days > 0:
            return '{}??'.format(delta.days)
        if delta.seconds > 3600:
            return '{}???'.format(delta.seconds // 3600)
        if delta.seconds > 60:
            return '{}???'.format(delta.seconds // 60)
        return '??'

def register_error_hanlers(app):
    """ ??????????????? JSON ??
    """

    @app.errorhandler(404)
    def not_found(error):
        return render_template('error/404.html'), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template('error/500.html'), 500
def create_app(config):
    app = Flask(__name__)
    app.config.from_object(configs.get(config))
    
    register_extensions(app)
    register_blueprints(app)
    register_filters(app)
    register_error_hanlers(app)
    return app