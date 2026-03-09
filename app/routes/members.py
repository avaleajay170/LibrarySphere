from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.member import Member
from datetime import date
from dateutil.relativedelta import relativedelta
from app.routes.auth import admin_required
members_bp = Blueprint('members', __name__, url_prefix='/members')

# ---- List All Members ----
@members_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    status = request.args.get('status', '')

    query = Member.query

    if search:
        query = query.filter(
            db.or_(
                Member.name.ilike(f'%{search}%'),
                Member.email.ilike(f'%{search}%'),
                Member.member_code.ilike(f'%{search}%'),
                Member.phone.ilike(f'%{search}%')
            )
        )
    if status:
        query = query.filter_by(status=status)

    members = query.order_by(Member.created_at.desc()).all()

    return render_template('members/index.html',
        members=members,
        search=search,
        selected_status=status
    )

# ---- Add Member ----
@members_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        address = request.form.get('address', '').strip()
        gender = request.form.get('gender', '')
        date_of_birth = request.form.get('date_of_birth', '')
        membership_months = int(request.form.get('membership_months', 12))

        if not name or not email:
            flash('Name and Email are required!', 'danger')
            return render_template('members/add.html')

        if Member.query.filter_by(email=email).first():
            flash('A member with this email already exists!', 'warning')
            return render_template('members/add.html')

        member_code = Member.generate_member_code()
        membership_date = date.today()
        expiry_date = membership_date + relativedelta(months=membership_months)

        member = Member(
            member_code=member_code,
            name=name,
            email=email,
            phone=phone or None,
            address=address or None,
            gender=gender or None,
            date_of_birth=date.fromisoformat(date_of_birth) if date_of_birth else None,
            membership_date=membership_date,
            expiry_date=expiry_date,
            status='active'
        )

        db.session.add(member)
        db.session.commit()
        flash(f'Member "{name}" registered successfully! Member Code: {member_code} 🎉', 'success')
        return redirect(url_for('members.index'))

    return render_template('members/add.html')

# ---- Edit Member ----
@members_bp.route('/edit/<int:member_id>', methods=['GET', 'POST'])
@login_required
def edit(member_id):
    member = Member.query.get_or_404(member_id)

    if request.method == 'POST':
        member.name = request.form.get('name', '').strip()
        member.email = request.form.get('email', '').strip()
        member.phone = request.form.get('phone', '').strip() or None
        member.address = request.form.get('address', '').strip() or None
        member.gender = request.form.get('gender', '') or None
        dob = request.form.get('date_of_birth', '')
        member.date_of_birth = date.fromisoformat(dob) if dob else None

        if not member.name or not member.email:
            flash('Name and Email are required!', 'danger')
            return render_template('members/edit.html', member=member)

        db.session.commit()
        flash(f'Member "{member.name}" updated successfully! ✅', 'success')
        return redirect(url_for('members.index'))

    return render_template('members/edit.html', member=member)

# ---- Member Profile ----
@members_bp.route('/profile/<int:member_id>')
@login_required
def profile(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template('members/profile.html', member=member)

# ---- Change Status ----
@members_bp.route('/status/<int:member_id>/<string:new_status>', methods=['POST'])
@login_required
@admin_required
def change_status(member_id, new_status):
    member = Member.query.get_or_404(member_id)
    if new_status in ['active', 'inactive', 'suspended']:
        member.status = new_status
        db.session.commit()
        flash(f'Member "{member.name}" status changed to {new_status}! ✅', 'success')
    return redirect(url_for('members.index'))

# ---- Renew Membership ----
@members_bp.route('/renew/<int:member_id>', methods=['POST'])
@login_required
def renew(member_id):
    member = Member.query.get_or_404(member_id)
    months = int(request.form.get('months', 12))
    if member.expiry_date and member.expiry_date > date.today():
        member.expiry_date = member.expiry_date + relativedelta(months=months)
    else:
        member.expiry_date = date.today() + relativedelta(months=months)
    member.status = 'active'
    db.session.commit()
    flash(f'Membership renewed for {months} months! ✅', 'success')
    return redirect(url_for('members.profile', member_id=member_id))