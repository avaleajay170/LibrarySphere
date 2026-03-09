from app import db
from datetime import datetime

class Fine(db.Model):
    __tablename__ = 'fines'

    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('book_issues.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Enum('pending', 'paid', 'waived'), default='pending', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    waived_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    waived_at = db.Column(db.DateTime, nullable=True)
    waive_reason = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    # Relationships
    waived_by_user = db.relationship('User', foreign_keys=[waived_by], backref='waived_fines', lazy=True)

    @property
    def is_paid(self):
        return self.status == 'paid'

    @property
    def is_waived(self):
        return self.status == 'waived'

    @property
    def is_pending(self):
        return self.status == 'pending'

    def mark_paid(self):
        self.status = 'paid'
        self.paid_at = datetime.utcnow()

    def mark_waived(self, user_id, reason=None):
        self.status = 'waived'
        self.waived_by = user_id
        self.waived_at = datetime.utcnow()
        self.waive_reason = reason

    def __repr__(self):
        return f'<Fine {self.id} - Amount:{self.amount} Status:{self.status}>'