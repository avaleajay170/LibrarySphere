from app import db
from datetime import datetime, date

class Member(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    member_code = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    gender = db.Column(db.Enum('male', 'female', 'other'), nullable=True)
    date_of_birth = db.Column(db.Date, nullable=True)
    membership_date = db.Column(db.Date, default=date.today)
    expiry_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.Enum('active', 'inactive', 'suspended'), default='active')
    photo = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issues = db.relationship('BookIssue', backref='member', lazy=True)

    @staticmethod
    def generate_member_code():
        last_member = Member.query.order_by(Member.id.desc()).first()
        if last_member:
            last_number = int(last_member.member_code.replace('LIB', ''))
            new_number = last_number + 1
        else:
            new_number = 1
        return f'LIB{new_number:04d}'

    @property
    def is_expired(self):
        if self.expiry_date:
            return date.today() > self.expiry_date
        return False

    @property
    def days_until_expiry(self):
        if self.expiry_date:
            delta = self.expiry_date - date.today()
            return delta.days
        return None

    @property
    def active_issues_count(self):
        from app.models.issue import BookIssue
        return BookIssue.query.filter_by(
            member_id=self.id,
            status='issued'
        ).count()

    @property
    def pending_fines(self):
        from app.models.fine import Fine
        from app.models.issue import BookIssue
        total = db.session.query(db.func.sum(Fine.amount)).join(
            BookIssue, Fine.issue_id == BookIssue.id
        ).filter(
            BookIssue.member_id == self.id,
            Fine.status == 'pending'
        ).scalar()
        return total or 0.0

    def __repr__(self):
        return f'<Member {self.member_code} - {self.name}>'