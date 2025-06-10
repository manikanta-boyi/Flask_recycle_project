from flask import render_template,redirect,url_for,flash,Blueprint,abort,request
from flask_login import current_user,login_required

from recycle_project import db

from recycle_project.models import Posts

from recycle_project.blog_posts.forms import BlogPostForm

blog_posts = Blueprint('blog_posts',__name__)

#creating post
@blog_posts.route('/create',methods=['GET','POST'])
@login_required
def create_post():
    form = BlogPostForm()
    if form.validate_on_submit():

        blog_post = Posts(title=form.title.data,
                          text=form.text.data,
                          user_id=current_user.id)

        db.session.add(blog_post)
        db.session.commit()
        flash('Blog post created')
        return redirect(url_for('core.index'))
    return render_template('create_post.html',form=form)

#blog post(view)
@blog_posts.route('/<int:blog_post_id>')
def blog_post(blog_post_id):
    blog_post=db.session.get(Posts,blog_post_id)

    return render_template('blog_post.html',title=blog_post.title,
                           date=blog_post.date,blog_post=blog_post)

#update
@blog_posts.route('/<int:blog_post_id>/update',methods = ['GET','POST'])
@login_required
def update(blog_post_id):
    blog_post=db.session.get(Posts,blog_post_id)
    if blog_post.author != current_user:
        abort(403)
    form = BlogPostForm()

    if form.validate_on_submit():

        blog_post.title = form.title.data
        blog_post.text = form.text.data
        db.session.commit()
        flash('Blog post Updated')
        return redirect(url_for('blog_posts.blog_post',blog_post_id=blog_post.id))
    elif request.method=='GET':
        form.title.data = blog_post.title
        form.text.data = blog_post.text

    return render_template('create_post.html',title='updating',form=form)
#delete
@blog_posts.route('/<blog_post_id>/delete',methods=['GET','POST'])
@login_required
def delete(blog_post_id):
    blog_post=db.session.get(Posts,blog_post_id)

    if blog_post.author != current_user:
        abort(403)

    db.session.delete(blog_post)
    db.session.commit()
    flash('Blog post deleted')
    return redirect(url_for('core.index'))
