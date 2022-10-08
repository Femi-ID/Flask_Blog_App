import os
from os import path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
DB_NAME = 'database.db'  # defining the name of the database


def create_app():
    # create and configure the app
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'cooking'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"  # tell flask the path of the database
    app.config['USE_SESSION_FOR_NEXT'] = True

    db.init_app(app)  # to initialize the database (reference sqlalchemy doc)

    from . import views
    app.register_blueprint(views.views)

    from . import auth
    app.register_blueprint(auth.auth)

    from .models import User, Post, Comment, Like

    create_database(app)

    login_manager = LoginManager()
    # the page to redirect the client to if it tries to access a page when not logged in
    login_manager.login_view = 'auth.login'
    # to customize the login message for users to access a page
    login_manager.login_message = 'You are required to login to access the page'
    # to customize the login message category
    login_manager.login_message_category = 'info'

    # Use the @fresh_login_required to differentiate btwn a 'fresh' session and a 'non-fresh' session (@login_required can't tell)
    # in addition to verifying the user is logged in, it will tell the diff and ensure that the login is 'fresh'.
    # if not it will redirect them a page to login ( login page to re-enter credentials).
    # Best scenario for this will be when they change their password. To customize the behavior:
    login_manager.refresh_view = 'auth.login'
    login_manager.needs_refresh_message = 'To protect your account please re-authenticate to access the page/ or to ' \
                                          'login '
    login_manager.needs_refresh_message_category = 'info'

    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    migrate = Migrate(app, db)
    # to make changes to your database after initializing it:
    # from flask_migrate import Migrate
    # then initialize the Migrate class with the app and db as arguments passed in
    # then in the virtual terminal; flask db init to initialize a migrate repository
    # flask db migrate to create a migration module i.e. to kind of stage it
    # flask db upgrade to push the migration changes to the database. cheers

    return app


# as the name implies; the function creates a database if it doesn't exist
def create_database(app):
    if not path.exists('blog_site/' + DB_NAME):
        db.create_all(app=app)
        print('Database initialized')

