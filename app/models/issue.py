from app import db
from datetime import datetime, date
from flask import current_app

class BookIssue(db.Model):
    __tablename__ = 'book_issues'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    issue_date = db.Column(db.Date, default=date.today, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('issued', 'returned', 'overdue'), default='issued', nullable=False)
    renewal_count = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    fine = db.relationship('Fine', backref='issue', lazy=True, uselist=False)

    @property
    def is_overdue(self):
        if self.status == 'issued' and date.today() > self.due_date:
            return True
        return False

    @property
    def overdue_days(self):
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0

    @property
    def calculated_fine(self):
        if self.is_overdue:
            fine_per_day = current_app.config.get('FINE_PER_DAY', 5.0)
            return round(self.overdue_days * fine_per_day, 2)
        return 0.0

    @property
    def days_remaining(self):
        if self.status == 'issued':
            delta = self.due_date - date.today()
            return delta.days
        return 0

    def can_renew(self):
        max_renewals = 2
        return self.renewal_count < max_renewals and self.status == 'issued'

    def __repr__(self):
        return f'<BookIssue {self.id} - Book:{self.book_id} Member:{self.member_id}>'