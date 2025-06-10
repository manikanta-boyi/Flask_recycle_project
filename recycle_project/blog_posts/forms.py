from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField

from wtforms.validators import DataRequired

class BlogPostForm(FlaskForm):
    title = StringField('title',validators=[DataRequired()])
    text = TextAreaField('text',validators=[DataRequired()])
    submit = SubmitField('Post')
    