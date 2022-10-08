import babel
from click import prompt
from flask import Blueprint, render_template, request, flash, url_for, redirect, jsonify
from flask_login import login_required, current_user
from .models import Post, User, Comment, Like
from . import db
from flask_wtf import Form
from wtforms import StringField, PasswordField, TextAreaField

views = Blueprint('views', __name__)


class WtForm(Form):
    Post_header = StringField('post_header')
    Post_body = TextAreaField('post_body')


# @views.add_app_template_filter()
# def format_datetime(value, format='medium'):
#     if format == 'full':
#         format="EEEE, d. MMMMM y HH:mm"
#     elif format == 'medium':
#         format='EE dd.MM.y HH:mm'
#     return babel.dates.format_datetime(value, format)

@views.route('/')
@login_required
def index():
    posts = Post.query.all()
    return render_template('index.html', user=current_user, posts=posts)


@views.route('/general_index', methods=['GET', 'POST'])
def general_index():
    return render_template('general_index.html', user=current_user)


@views.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if request.method == 'POST':
        text = request.form.get('text')

        if not text:
            error = 'Empty post not accepted!'
            flash(message=error, category='info')

        else:
            error = 'Post successfully created!'
            flash(message=error, category='success')
            post = Post(text=text, author=current_user.id)
            db.session.add(post)
            db.session.commit()
            return redirect(url_for('views.index', post=post))
    return render_template('create_post.html', user=current_user)


@views.route('/edit_post/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()

    # If post doesn't exist
    if not post:
        error = 'Post does not exist!'
        flash(message=error, category='error')

    # if the current user is not the owner of the post
    elif current_user.id != post.author:
        error = 'Unauthorized request for this action!'
        flash(message=error, category='error')
        return redirect(url_for('views.index', post=post))

    elif request.method == 'POST':
        post.text = request.form.get('text')
        if post.text == post.text:
            pass
        elif '(Edited)' not in post.text:
            post.text = post.text + ' (edited)'
        if post.text == '':
            error = 'Post cannot be empty!'
            flash(message=error, category='error')
            return render_template('edit_post.html', post=post, user=current_user)
        # post = Post(text=post.text, author=current_user.id)
        db.session.add(post)
        db.session.commit()
        error = 'Post successfully edited!'
        flash(message=error, category='success')
        return redirect(url_for('views.index', post=post))

    # request.form['text'] = post.text
    return render_template('edit_post.html', post=post, user=current_user)


@views.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.filter_by(id=id).first()
    # user = User.query.filter_by(id=id).first()
    error = None

    if not post:
        error = 'Post does not exist!'
        flash(message=error, category='error')
    elif current_user.id != post.author:
        error = 'Unauthorized access to complete delete action'
        flash(message=error, category='error')
    else:
        # response = prompt('Confirm to delete post')
        # response_input = input(response)
        # if response_input is True:
        db.session.delete(post)
        db.session.commit()
        flash(message='Post successfully deleted', category='success')

    return redirect(url_for('views.index'))


@views.route('/posts/<username>')
def posts(username):
    user = User.query.filter_by(username=username).first()

    if not user:
        error = 'User does not exist!'
        flash(message=error, category='error')
        return redirect(url_for('views.index'))

    posts = user.posts
    # posts = Post.query.filter_by(author=user.id).all()
    return render_template('posts.html', user=current_user, posts=posts, username=username)


@views.route('/create_comment/<int:post_id>', methods=['POST'])
@login_required
def create_comment(post_id):
    post = Post.query.filter_by(id=post_id).first()
    posts = Post.query.all()
    if not post:
        error = 'Post does not exist!'
        flash(message=error, category='error')

    if request.method == 'POST':
        text = request.form.get('text')
        if text == '':
            error = 'Comment field cannot be empty'
            flash(message=error, category='info')
            return redirect(url_for('views.index', post=post, user=current_user))
        comment = Comment(text=text, user_id=current_user.id, post_id=post.id)
        db.session.add(comment)
        db.session.commit()

    return redirect(url_for('views.index'))
    # return render_template('index.html', post=post, user=current_user, posts=posts)


@views.route('/delete_comments/<int:comment_id>')
@login_required
def delete_comments(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    error = None

    if not comment:
        error = 'Comment does not exist!'
        flash(message=error, category='error')

    elif comment.user_id != current_user.id and current_user.id != comment.post.author:
        error = 'Unauthorized permission to complete this request!'
        flash(message=error, category='error')

    elif error is None:
        db.session.delete(comment)
        db.session.commit()

    return redirect(url_for('views.index'))


@views.route('/wt_forms', methods=['GET', 'POST'])
def wt_forms():
    form = WtForm()
    return render_template('wt_forms.html', user=current_user, form=form)


@views.route('/like_post/<int:post_id>', methods=['POST'])
@login_required
def like(post_id):
    post = Post.query.filter_by(id=post_id).first()
    like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    error = None

    if not post:
        error = 'Post does not exist!'
        flash(message=error, category='error')
        return jsonify({"error": "Post does not exist"}, 400)
    elif like:
        db.session.delete(like)
        db.session.commit()
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()

    return jsonify({"likes": len(post.likes), "liked": current_user.id in map(lambda x: x.user_id, post.likes)})
    # redirect(url_for('views.index'))

