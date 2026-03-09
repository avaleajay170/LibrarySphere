from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models.book import Book
from app.models.member import Member
from app.models.issue import BookIssue
from app.models.fine import Fine
from datetime import date, timedelta
from flask import current_app

issues_bp = Blueprint('issues', __name__, url_prefix='/issues')

# ---- List All Issues ----
@issues_bp.route('/')
@login_required
def index():
    status = request.args.get('status', '')
    search = request.args.get('search', '')

    query = BookIssue.query

    if status == 'overdue':
        query = query.filter(
            BookIssue.status == 'issued',
            BookIssue.due_date < date.today()
        )
    elif status:
        query = query.filter_by(status=status)

    if search:
        query = query.join(Member).filter(
            db.or_(
                Member.name.ilike(f'%{search}%'),
                Member.member_code.ilike(f'%{search}%')
            )
        )

    issues = query.order_by(BookIssue.created_at.desc()).all()

    return render_template('issues/index.html',
        issues=issues,
        selected_status=status,
        search=search,
        today=date.today()
    )

# ---- Issue Book ----
@issues_bp.route('/issue', methods=['GET', 'POST'])
@login_required
def issue_book():
    members = Member.query.filter_by(status='active').all()
    books = Book.query.filter(
        Book.is_active == True,
        Book.available_copies > 0
    ).all()

    if request.method == 'POST':
        member_id = request.form.get('member_id')
        book_id = request.form.get('book_id')
        notes = request.form.get('notes', '').strip()

        if not member_id or not book_id:
            flash('Please select both member and book!', 'danger')
            return render_template('issues/issue_book.html',
                members=members, books=books,
                today=date.today(), timedelta=timedelta)

        member = Member.query.get_or_404(member_id)
        book = Book.query.get_or_404(book_id)

        if member.status != 'active':
            flash('Member is not active!', 'danger')
            return render_template('issues/issue_book.html',
                members=members, books=books,
                today=date.today(), timedelta=timedelta)

        if book.available_copies <= 0:
            flash('No copies available for this book!', 'danger')
            return render_template('issues/issue_book.html',
                members=members, books=books,
                today=date.today(), timedelta=timedelta)

        if member.pending_fines > 100:
            flash(f'Member has pending fines of ₹{member.pending_fines:.0f}. Please clear fines first!', 'warning')
            return render_template('issues/issue_book.html',
                members=members, books=books,
                today=date.today(), timedelta=timedelta)

        existing = BookIssue.query.filter_by(
            member_id=member.id,
            book_id=book.id,
            status='issued'
        ).first()
        if existing:
            flash('Member already has this book issued!', 'warning')
            return render_template('issues/issue_book.html',
                members=members, books=books,
                today=date.today(), timedelta=timedelta)

        loan_days = current_app.config.get('LOAN_DAYS', 14)
        issue = BookIssue(
            book_id=book.id,
            member_id=member.id,
            issued_by=current_user.id,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=loan_days),
            status='issued',
            notes=notes or None
        )

        book.available_copies -= 1
        db.session.add(issue)
        db.session.commit()

        flash(f'Book "{book.title}" issued to {member.name} successfully! Due: {issue.due_date.strftime("%d %b %Y")} 📚', 'success')
        return redirect(url_for('issues.index'))

    return render_template('issues/issue_book.html',
        members=members, books=books,
        today=date.today(), timedelta=timedelta)

# ---- Return Book ----
@issues_bp.route('/return/<int:issue_id>', methods=['GET', 'POST'])
@login_required
def return_book(issue_id):
    issue = BookIssue.query.get_or_404(issue_id)

    if request.method == 'POST':
        issue.return_date = date.today()
        issue.status = 'returned'
        issue.book.available_copies += 1

        if issue.is_overdue:
            fine_amount = issue.calculated_fine
            fine = Fine(
                issue_id=issue.id,
                amount=fine_amount,
                status='pending'
            )
            db.session.add(fine)
            flash(f'Book returned! Fine of ₹{fine_amount:.0f} created for {issue.overdue_days} overdue days.', 'warning')
        else:
            flash(f'Book "{issue.book.title}" returned successfully! ✅', 'success')

        db.session.commit()
        return redirect(url_for('issues.index'))

    return render_template('issues/return_book.html', issue=issue, today=date.today())

# ---- Renew Book ----
@issues_bp.route('/renew/<int:issue_id>', methods=['POST'])
@login_required
def renew_book(issue_id):
    issue = BookIssue.query.get_or_404(issue_id)

    if not issue.can_renew():
        flash('This book cannot be renewed (max renewals reached or already returned)!', 'danger')
        return redirect(url_for('issues.index'))

    loan_days = current_app.config.get('LOAN_DAYS', 14)
    issue.due_date = issue.due_date + timedelta(days=loan_days)
    issue.renewal_count += 1
    db.session.commit()

    flash(f'Book "{issue.book.title}" renewed! New due date: {issue.due_date.strftime("%d %b %Y")} ✅', 'success')
    return redirect(url_for('issues.index'))