from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.fine import Fine
from app.models.issue import BookIssue
from app.models.member import Member
from datetime import datetime
from app.routes.auth import admin_required

fines_bp = Blueprint('fines', __name__, url_prefix='/fines')

# ---- List All Fines ----
@fines_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = Fine.query

    if status:
        query = query.filter_by(status=status)

    if search:
        query = query.join(BookIssue).join(Member).filter(
            db.or_(
                Member.name.ilike(f'%{search}%'),
                Member.member_code.ilike(f'%{search}%')
            )
        )

    fines = query.order_by(Fine.created_at.desc()).all()

    total_pending = sum(f.amount for f in Fine.query.filter_by(status='pending').all())
    total_collected = sum(f.amount for f in Fine.query.filter_by(status='paid').all())
    total_waived = sum(f.amount for f in Fine.query.filter_by(status='waived').all())

    return render_template('fines/index.html',
        fines=fines,
        selected_status=status,
        search=search,
        total_pending=total_pending,
        total_collected=total_collected,
        total_waived=total_waived
    )

# ---- Collect Fine (Mark as Paid) ----
@fines_bp.route('/collect/<int:fine_id>', methods=['POST'])
@login_required
def collect(fine_id):
    fine = Fine.query.get_or_404(fine_id)
    fine.mark_paid()
    db.session.commit()
    flash(f'Fine of ₹{fine.amount:.0f} collected successfully! ✅', 'success')
    return redirect(url_for('fines.index'))

# ---- Waive Fine ----
@fines_bp.route('/waive/<int:fine_id>', methods=['POST'])
@login_required
@admin_required
def waive(fine_id):
    fine = Fine.query.get_or_404(fine_id)
    reason = request.form.get('reason', 'Waived by admin')
    fine.mark_waived(user_id=current_user.id, reason=reason)
    db.session.commit()
    flash(f'Fine of ₹{fine.amount:.0f} waived! ✅', 'success')
    return redirect(url_for('fines.index'))