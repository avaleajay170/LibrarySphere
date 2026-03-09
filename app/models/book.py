from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    author = db.Column(db.String(255), nullable=False)
    publisher = db.Column(db.String(255), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    total_copies = db.Column(db.Integer, default=1, nullable=False)
    available_copies = db.Column(db.Integer, default=1, nullable=False)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(500), nullable=True)
    language = db.Column(db.String(50), default='English')
    pages = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    issues = db.relationship('BookIssue', backref='book', lazy=True)

    @property
    def is_available(self):
        return self.available_copies > 0

    @property
    def availability_percentage(self):
        if self.total_copies == 0:
            return 0
        return int((self.available_copies / self.total_copies) * 100)

    def __repr__(self):
        return f'<Book {self.title}>'