from flask import url_for,redirect,render_template,Blueprint,request, flash
from flask_login import login_user,login_required,logout_user,current_user
from recycle_project import db, mail
from recycle_project.models import Users, Posts, OTP
from recycle_project.users.forms import RegisterForm, LoginForm,   UpdateUserForm
from recycle_project.users.image_handler import add_profile_pic
from flask_mail import Message # Import Message for sending emails
from werkzeug.security import generate_password_hash # Import for hashing password
import datetime # For OTP expiration calculation

#for otp form
from flask_wtf import FlaskForm # Import FlaskForm for the simple OTPForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length





users = Blueprint('users',__name__)

#register

@users.route('/register', methods=['GET', 'POST'])
def register():
    
    form = RegisterForm()

    if form.validate_on_submit():
        email = form.email.data
        username = form.username.data
        raw_password = form.password.data # Get the raw password
        hashed_password = generate_password_hash(raw_password) # Hash the password

        
        OTP.query.filter_by(email=email).delete()
        db.session.commit()

        #  Create a new OTP entry, storing temporary user data
        otp_entry = OTP(email=email, username=username, temp_password_hash=hashed_password)
        db.session.add(otp_entry)
        db.session.commit() # Commit to save the OTP entry

        #  Send OTP to user's email
        msg = Message('Your OTP for Recycle Project Registration', recipients=[email])
        msg.body = f"Hello {username},\n\n" \
                   f"Your One-Time Password (OTP) for Recycle Project registration is: {otp_entry.otp_code}\n\n" \
                   f"This OTP is valid for 5 minutes. Do not share it with anyone.\n\n" \
                   f"If you did not request this, please ignore this email."
        try:
            mail.send(msg)
            flash(f'An OTP has been sent to {email}. Please check your inbox and spam folder to complete registration.', 'info')
            # Redirect to OTP verification page, passing the email for context
            return redirect(url_for('users.verify_otp', email=email))
        except Exception as e:
            # If email sending fails, rollback the OTP creation
            db.session.rollback()
            flash(f'Failed to send OTP. Please ensure your email configuration is correct and try again later. Error: {e}', 'danger')
            return redirect(url_for('users.register')) # Stay on registration page

    return render_template('register.html', form=form)

#login
@users.route('/login',methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(Users).filter_by(email=form.email.data).first()

        if user is not None and user.validate_password(form.password.data):
            login_user(user)

            next = request.args.get('next')

            if next==None or not next[0]=='/':
                next = url_for('core.index')
            return redirect(next)
    return render_template('login.html',form=form)
            

            

#logout
@users.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('core.index')) # we mentioned core because of blueprints



@users.route('/account',methods=['GET','POST'])
@login_required
def account():
    form = UpdateUserForm()
    if form.validate_on_submit():
        if form.picture.data:
            username = current_user.username
            pic = add_profile_pic(form.picture.data,username)
            current_user.profile_pic = pic

        current_user.username = form.username.data
        current_user.email= form.email.data
        db.session.commit()
        

        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email

    profile_pic = url_for('static',filename='profile_pics/'+current_user.profile_pic)
    return render_template('account.html',profile_pic = profile_pic,form=form)

@users.route('/<username>')
def user_post(username):
    page = request.args.get('page',1,type=int)
    user = db.session.query(Users).filter_by(username=username).first_or_404()
    blog_posts = db.session.query(Posts).filter_by(author=user).order_by(Posts.date.desc()).paginate(page=page,per_page=5)
    return render_template('user_blog_posts.html',blog_posts=blog_posts,user=user)



#otp verification form
class OTPVerificationForm(FlaskForm):
    otp = StringField('Enter OTP', validators=[DataRequired(), Length(min=6, max=6, message='OTP must be 6 digits.')])
    submit = SubmitField('Verify OTP')




@users.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    email = request.args.get('email') # Get email from URL query parameter

    # If email is not in the URL, redirect back to register
    if not email:
        flash('Email missing for OTP verification. Please register again.', 'danger')
        return redirect(url_for('users.register'))

    form = OTPVerificationForm()

    if form.validate_on_submit():
        user_entered_otp = form.otp.data

        # Find the latest OTP entry for this email
        # We order by created_at.desc() to get the most recent OTP in case multiple were sent
        otp_entry = OTP.query.filter_by(email=email)\
                             .order_by(OTP.created_at.desc())\
                             .first()

        if otp_entry and otp_entry.is_valid(user_entered_otp):
            # OTP is valid, now create the actual Users entry
            # Use the temporarily stored username and hashed password
            new_user = Users(email=otp_entry.email,
                             username=otp_entry.username,
                             password="temporary_dummy_password_for_init") # Use any non-empty string here
            
            #  IMPORTANT: OVERWRITE the password_hash with the correct, single-hashed password
            #    that was stored in the OTP table.
            new_user.password_hash = otp_entry.temp_password_hash

            db.session.add(new_user)
            db.session.delete(otp_entry) # Delete the used OTP entry
            db.session.commit()

            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('users.login')) # Redirect to login page

        else:
            # OTP is invalid or expired
            flash('Invalid or expired OTP. Please try again or re-register to get a new OTP.', 'danger')
            return redirect(url_for('users.verify_otp', email=email)) # Stay on verification page or redirect to register

    return render_template('verify_otp.html', form=form, email=email)