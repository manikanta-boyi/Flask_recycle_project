from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_login import LoginManager
from flask_mail import Mail, Message


app = Flask(__name__) # initialising application

app.config['SECRET_KEY']='mysecretkey'

# Flask-Mail Configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('EMAIL_USER')
app.config['MAIL_PASSWORD'] = os.environ.get('EMAIL_PASS')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('EMAIL_USER')

mail = Mail(app) # Initialize Flask-Mail

###########################################
########## SETTING DATABASE ###############

basedir = os.path.abspath(os.path.dirname(__file__))

app.config['SQLALCHEMY_DATABASE_URI']=os.environ.get('DATABASE_URL') or 'sqlite:///'+os.path.join(basedir,'sqlite.data') # used "or " for deployment purpose
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

db = SQLAlchemy(app) # setup for database
Migrate(app,db) #setup for migration


############################################

# login config

login_manager = LoginManager()

login_manager.init_app(app) # setup our app for login configeration
login_manager.login_view = 'users.login' # here users is blueprint name








from recycle_project.core.views import core
from recycle_project.error_pages.handlers import error_pages
from recycle_project.users.views import users
from recycle_project.blog_posts.views import blog_posts
from recycle_project.api.endpoints import api


app.register_blueprint(core)
app.register_blueprint(users)
app.register_blueprint(error_pages)
app.register_blueprint(blog_posts)
app.register_blueprint(api)







