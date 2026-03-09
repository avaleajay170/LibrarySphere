from flask import Blueprint, render_template
from flask_login import login_required
from app import db
from app.models.book import Book
from app.models.member import Member
from app.models.issue import BookIssue
from app.models.fine import Fine
from app.models.category import Category
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def index():
    # KPI Stats
    total_books = Book.query.filter_by(is_active=True).count()
    total_members = Member.query.filter_by(status='active').count()
    active_issues = BookIssue.query.filter_by(status='issued').count()
    pending_fines = db.session.query(
        db.func.sum(Fine.amount)
    ).filter_by(status='pending').scalar() or 0

    # Overdue count
    from datetime import date
    overdue_count = BookIssue.query.filter(
        BookIssue.status == 'issued',
        BookIssue.due_date < date.today()
    ).count()

    # Recent issues
    recent_issues = BookIssue.query.order_by(
        BookIssue.created_at.desc()
    ).limit(8).all()

    # Last 6 months chart data
    months = []
    issues_data = []
    for i in range(5, -1, -1):
        month_date = datetime.now() - relativedelta(months=i)
        month_name = month_date.strftime('%b %Y')
        months.append(month_name)
        count = BookIssue.query.filter(
            db.extract('month', BookIssue.issue_date) == month_date.month,
            db.extract('year', BookIssue.issue_date) == month_date.year
        ).count()
        issues_data.append(count)

    # Category chart data
    categories = Category.query.all()
    category_labels = []
    category_data = []
    for cat in categories:
        book_count = Book.query.filter_by(
            category_id=cat.id, is_active=True
        ).count()
        if book_count > 0:
            category_labels.append(cat.name)
            category_data.append(book_count)

    return render_template('dashboard/index.html',
        total_books=total_books,
        total_members=total_members,
        active_issues=active_issues,
        pending_fines=pending_fines,
        overdue_count=overdue_count,
        recent_issues=recent_issues,
        months=months,
        issues_data=issues_data,
        category_labels=category_labels,
        category_data=category_data
    )