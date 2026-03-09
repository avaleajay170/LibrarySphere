from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.routes.auth import admin_required

users_bp = Blueprint('users', __name__, url_prefix='/users')

@users_bp.route('/')
@login_required
@admin_required
def index():
    from app import db
    from app.models.user import User
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('users/index.html', users=users)

@users_bp.route('/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add():
    from app import db
    from app.models.user import User
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'librarian')

        if not username or not email or not password:
            flash('All fields are required!', 'danger')
            return render_template('users/add.html')
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'warning')
            return render_template('users/add.html')
        if User.query.filter_by(email=email).first():
            flash('Email already exists!', 'warning')
            return render_template('users/add.html')
        if len(password) < 6:
            flash('Password must be at least 6 characters!', 'danger')
            return render_template('users/add.html')

        user = User(username=username, email=email, role=role, is_active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash(f'User "{username}" created successfully! ✅', 'success')
        return redirect(url_for('users.index'))

    return render_template('users/add.html')

@users_bp.route('/toggle/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def toggle_status(user_id):
    from app import db
    from app.models.user import User
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate yourself!', 'danger')
        return redirect(url_for('users.index'))
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'User "{user.username}" {status}! ✅', 'success')
    return redirect(url_for('users.index'))

@users_bp.route('/reset-password/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def reset_password(user_id):
    from app import db
    from app.models.user import User
    user = User.query.get_or_404(user_id)
    new_password = request.form.get('new_password', '').strip()
    if not new_password or len(new_password) < 6:
        flash('Password must be at least 6 characters!', 'danger')
        return redirect(url_for('users.index'))
    user.set_password(new_password)
    db.session.commit()
    flash(f'Password for "{user.username}" reset successfully! ✅', 'success')
    return redirect(url_for('users.index'))