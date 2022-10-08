from urllib.parse import urlparse, urljoin
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from . import db
from .models import User
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required, current_user, fresh_login_required

auth = Blueprint('auth', __name__, url_prefix='/auth')


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.values.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


def redirect_back(endpoint, **values):
    target = request.form['next']
    if not target or not is_safe_url(target):
        target = url_for(endpoint, **values)
    return redirect(target)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        error = None
        # session['next'] = request.args.get('next')

        user = User.query.filter_by(email=email).first()

        if not user:
            error = 'Invalid Email or Password'
            flash(error, category='error')

        if error is None:
            if check_password_hash(user.password, password):
                flash('Logged in!', category='success')
                login_user(user, remember=True)

                if 'next' in session:
                    next = session['next']
                    if is_safe_url(next):
                        return redirect(next)

                return redirect(url_for('views.index'))
            else:
                error = 'Invalid Email or Password'
                flash(error, category='error')
        # else:
        #     error = 'Invalid Email or Password'
        #     flash(error, category='error')

    return render_template('login.html', user=current_user)


@auth.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # username = request.form['username']
        username = request.form.get('username')
        email = request.form.get('email')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        error = None

        username_exists = User.query.filter_by(username=username).first()
        user_email_exists = User.query.filter_by(email=email).first()

        if username_exists:
            error = 'Username already exists'
            flash(error, category='error')

        elif user_email_exists:
            error = 'Account with email already exists'
            flash(error, category='error')

        elif password1 != password2:
            error = 'Passwords don\'t match!'
            flash(error, category='error')

        elif len(password1) < 6:
            error = 'Passwords too short!'
            flash(error, category='error')

        elif len(username) < 3:
            error = 'Username too short.'
            flash(error, category='error')

        elif len(email) < 5:
            error = 'Invalid Email'
            flash(error, category='error')

        if error is None:
            new_user = User(username=username, email=email, password=generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('User created!')
            login_user(new_user, remember=True)
            return redirect(url_for('auth.login'))

    return render_template('sign_up.html', user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.general_index'))


@auth.route('/settings')
@login_required
def settings():
    return render_template('settings.html', user=current_user)


@auth.route('/fresh_login')
@fresh_login_required
def fresh_login():
    return 'you must be a new user, recently logged in OR have changed your password to see this page.'

# from urlparse import urlparse, urljoin
