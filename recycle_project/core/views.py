# cores/views.py
from flask import render_template,Blueprint,redirect,request
from recycle_project import db
from recycle_project.models import Posts
import os
import google.generativeai as genai
from flask_login import login_required

core = Blueprint('core',__name__)

@core.route('/')
def index():
    page=request.args.get('page',1,type=int)
    blog_posts = Posts.query.order_by(Posts.date.desc()).paginate(page=page,per_page=5)



    return render_template('index.html',blog_posts=blog_posts)

gemini_api_key = os.environ.get('gemini_api_key')
genai.configure(api_key=gemini_api_key)



@core.route('/recycle_bot', methods=["GET", "POST"])
@login_required
def recycle_bot():
    suggestion = None
    if request.method == "POST":
        user_item = request.form["item"]
        prompt = f"Provide 5 distinct recycling ideas for a {user_item}, each idea formatted as a short bullet point "

        try:
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = model.generate_content(prompt)
            suggestion = response.text
        except Exception as e:
            suggestion = f"Error: {str(e)}"

    return render_template("bot.html", suggestion=suggestion)


@core.route('/info')
def info():

    return render_template('info.html')


