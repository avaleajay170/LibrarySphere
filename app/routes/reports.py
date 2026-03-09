from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app import db
from app.models.book import Book
from app.models.member import Member
from app.models.issue import BookIssue
from app.models.fine import Fine
from app.models.category import Category
from datetime import date, timedelta
from sqlalchemy import func

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def index():
    today = date.today()
    month_start = today.replace(day=1)

    # ---- Overview Stats ----
    total_books = Book.query.filter_by(is_active=True).count()
    total_members = Member.query.count()
    active_members = Member.query.filter_by(status='active').count()
    total_issues = BookIssue.query.count()
    active_issues = BookIssue.query.filter_by(status='issued').count()
    overdue_issues = BookIssue.query.filter(
        BookIssue.status == 'issued',
        BookIssue.due_date < today
    ).count()
    total_fines = db.session.query(func.sum(Fine.amount)).filter_by(status='pending').scalar() or 0
    collected_fines = db.session.query(func.sum(Fine.amount)).filter_by(status='paid').scalar() or 0

    # ---- Monthly Issues (last 6 months) ----
    monthly_data = []
    for i in range(5, -1, -1):
        month_date = today - timedelta(days=i * 30)
        m_start = month_date.replace(day=1)
        if month_date.month == 12:
            m_end = month_date.replace(year=month_date.year + 1, month=1, day=1)
        else:
            m_end = month_date.replace(month=month_date.month + 1, day=1)
        count = BookIssue.query.filter(
            BookIssue.issue_date >= m_start,
            BookIssue.issue_date < m_end
        ).count()
        monthly_data.append({
            'month': m_start.strftime('%b %Y'),
            'count': count
        })

    # ---- Top 5 Most Issued Books ----
    top_books = db.session.query(
        Book.title, Book.author,
        func.count(BookIssue.id).label('issue_count')
    ).join(BookIssue).group_by(Book.id).order_by(
        func.count(BookIssue.id).desc()
    ).limit(5).all()

    # ---- Top 5 Most Active Members ----
    top_members = db.session.query(
        Member.name, Member.member_code,
        func.count(BookIssue.id).label('issue_count')
    ).join(BookIssue).group_by(Member.id).order_by(
        func.count(BookIssue.id).desc()
    ).limit(5).all()

    # ---- Books by Category ----
    category_data = db.session.query(
        Category.name,
        func.count(Book.id).label('book_count')
    ).join(Book).group_by(Category.id).order_by(
        func.count(Book.id).desc()
    ).all()

    # ---- Overdue List ----
    overdue_list = BookIssue.query.filter(
        BookIssue.status == 'issued',
        BookIssue.due_date < today
    ).order_by(BookIssue.due_date.asc()).limit(10).all()

    # ---- Members expiring soon (next 30 days) ----
    expiring_members = Member.query.filter(
        Member.expiry_date >= today,
        Member.expiry_date <= today + timedelta(days=30),
        Member.status == 'active'
    ).order_by(Member.expiry_date.asc()).all()

    return render_template('reports/index.html',
        today=today,
        total_books=total_books,
        total_members=total_members,
        active_members=active_members,
        total_issues=total_issues,
        active_issues=active_issues,
        overdue_issues=overdue_issues,
        total_fines=total_fines,
        collected_fines=collected_fines,
        monthly_data=monthly_data,
        top_books=top_books,
        top_members=top_members,
        category_data=category_data,
        overdue_list=overdue_list,
        expiring_members=expiring_members
    )