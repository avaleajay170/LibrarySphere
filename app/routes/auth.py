from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.forms import LoginForm
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# ---- Role Decorators ----
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Access denied! Admin only.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

def librarian_or_admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role not in ['admin', 'librarian']:
            flash('Access denied!', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

# ---- Login ----
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            if not user.is_active:
                flash('Your account is inactive. Contact admin.', 'danger')
                return render_template('auth/login.html', form=form)
            login_user(user, remember=form.remember.data)
            flash(f'Welcome back, {user.username}! 👋', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash('Invalid username or password!', 'danger')

    return render_template('auth/login.html', form=form)

# ---- Logout ----
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out. See you soon! 👋', 'info')
    return redirect(url_for('auth.login'))