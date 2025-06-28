from recycle_project import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime
import datetime
from datetime import UTC
import random # For OTP generation
from flask import flash


# this will use for is_user_authenticated call in templates
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(Users,int(user_id))

class Users(db.Model,UserMixin):

    __tablename__ = 'users'
    __table_args__ = {"schema":'recycle_project_schema'} # added this schema because i have only one database ind Render

    id = db.Column(db.Integer(),primary_key = True)
    profile_pic = db.Column(db.String(64),nullable=False,default='default_profile.png')
    email = db.Column(db.String(64),unique = True,index=True)
    username = db.Column(db.String(64),unique=True,index=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Posts',backref='author',lazy=True)

    def __init__(self,email,username,password):
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):
        return check_password_hash(self.password_hash,password)
    
    def __str__(self):
        return f'Username {self.username}'


class Posts(db.Model):

    __table_args__ = {'schema': 'recycle_project_schema'}
    
    

    id = db.Column(db.Integer,primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('recycle_project_schema.users.id'),nullable = False) # connecting posts to user
    date = db.Column(db.DateTime,nullable=False,default=datetime.datetime.now(UTC))
    title = db.Column(db.String(128),nullable =False)
    text = db.Column(db.Text,nullable=False)

    def __init__(self,title,text,user_id):
        self.title = title
        self.text = text
        self.user_id = user_id

    def __str__(self):
        return f'Post id:{self.id}--date:{self.date}--{self.title}'
    

    

class OTP(db.Model):

    __table_args__ = {'schema': 'recycle_project_schema'}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=False, nullable=False)
    username = db.Column(db.String(64), nullable=False) # New: to store username
    temp_password_hash = db.Column(db.String(128), nullable=False) # New: to store hashed password temporarily
    otp_code = db.Column(db.String(6), nullable=False) # 6-digit OTP
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.datetime.now)
    expires_at = db.Column(db.DateTime, nullable=False) # When the OTP expires

    def __init__(self, email, username, temp_password_hash): # Updated __init__
        self.email = email
        self.username = username
        self.temp_password_hash = temp_password_hash
        self.otp_code = self.generate_otp()
        # OTP valid for 5 minutes (adjust as needed)
        self.expires_at = datetime.datetime.now() + datetime.timedelta(minutes=5)

    def generate_otp(self):
        # Generate a 6-digit OTP
        return str(random.randint(100000, 999999))

    def is_valid(self, user_entered_otp):
        return self.otp_code == user_entered_otp and datetime.datetime.now() < self.expires_at

    def __repr__(self):
        return f"OTP('{self.email}', '{self.otp_code}', '{self.expires_at}')"