from flask import Blueprint, jsonify, request, url_for
from flask_login import LoginManager, login_required, current_user
from recycle_project import db
from recycle_project.models import Posts,Users
import datetime
from datetime import UTC


# creating blueprint 
api = Blueprint('api',__name__,url_prefix='/api/v1')


#function to serialize Post object to a dictionary
def serialize_post(post):

    return {'id':post.id,'title':post.title,'content':post.text,'auther_id':post.user_id,'auther_name':post.auther.username,
            'date_posted':post.date.isoformat(),'url':url_for('api.get_single_post',post_id=post.id, _external=True)}

def error_response(message, status_code=400):
    
    return jsonify({'error': message}), status_code


def success_response(message, status_code=200):
    
    return jsonify({'message': message}), status_code


# Endpoints #
@api.route('/posts', methods=['GET'])
def get_post(): # end point for to retrive list of all blog posts
    page = request.args.get('page', 1, type=int)
    posts_per_page = 10

    # to get all posts by date. page value comes from request object
    all_posts = Posts.query.order_by(Posts.date.desc()).paginate(page=page, per_page=posts_per_page)

    serialized_posts = [serialize_post(post) for post in all_posts.items] #list of serialized posts

    
    return jsonify({
        'posts': serialized_posts,
        'total_posts': all_posts.total,
        'current_page': all_posts.page,
        'pages': all_posts.pages,
        'has_next': all_posts.has_next,
        'has_prev': all_posts.has_prev
    })

# to retrieve single post by its id 
@api.route('/posts/<int:post_id>', methods=['GET'])
def get_single_post(post_id):
    """
    API endpoint to retrieve a single blog post by its ID.
    """
    post = Posts.query.get_or_404(post_id) # Returns 404 if post not found
    return jsonify(serialize_post(post))

