from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField, ValidationError, FileField
from wtforms.validators import DataRequired, Email, EqualTo
from recycle_project import db
from recycle_project.models import Users


class LoginForm(FlaskForm):
    email = StringField('Enter mail',validators=[DataRequired(),Email()])
    password = PasswordField('Enter password',validators=[DataRequired()])
    login = SubmitField('Login')

class RegisterForm(FlaskForm):
    email = StringField('Enter email',validators=[DataRequired(),Email()])
    username = StringField('User name',validators=[DataRequired()])
    password = PasswordField('enter password',validators=[DataRequired(),EqualTo('confirm_password')])
    confirm_password = PasswordField('Confirm password',validators=[DataRequired()])
    register = SubmitField('Register')

    def validate_email(self, email):
        if db.session.query(Users).filter_by(email=email.data).first():
            raise ValidationError('this email is already registered')
            
        
    def validate_username(self,username):
        if db.session.query(Users).filter_by(username=username.data).first():
            raise ValidationError('this username already registered')


class UpdateUserForm(FlaskForm):
    email = StringField('Enter email',validators=[DataRequired(),Email()])
    username = StringField('User name',validators=[DataRequired()])
    picture = FileField('update profile picture') # filefield used for upload files and fileallowed validator validates file type
    submit = SubmitField('Update')

    def validate_email(self, email):
        if db.session.query(Users).filter_by(email=email.data).first():
            raise ValidationError('this email is already registered')
            
        
    def validate_username(self,username):
        if db.session.query(Users).filter_by(username=username.data).first():
            raise ValidationError('this username already registered')
