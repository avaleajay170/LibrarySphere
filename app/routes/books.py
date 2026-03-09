from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models.book import Book
from app.models.category import Category
from datetime import datetime
import requests
from app.routes.auth import admin_required
books_bp = Blueprint('books', __name__, url_prefix='/books')

# ---- List All Books ----
@books_bp.route('/')
@login_required
def index():
    search = request.args.get('search', '')
    category_id = request.args.get('category', '')
    availability = request.args.get('availability', '')

    query = Book.query.filter_by(is_active=True)

    if search:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search}%'),
                Book.author.ilike(f'%{search}%'),
                Book.isbn.ilike(f'%{search}%')
            )
        )
    if category_id:
        query = query.filter_by(category_id=category_id)
    if availability == 'available':
        query = query.filter(Book.available_copies > 0)
    elif availability == 'unavailable':
        query = query.filter(Book.available_copies == 0)

    books = query.order_by(Book.created_at.desc()).all()
    categories = Category.query.all()

    return render_template('books/index.html',
        books=books,
        categories=categories,
        search=search,
        selected_category=category_id,
        selected_availability=availability
    )

# ---- Add Book ----
@books_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    categories = Category.query.all()

    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        title = request.form.get('title', '').strip()
        author = request.form.get('author', '').strip()
        publisher = request.form.get('publisher', '').strip()
        publication_year = request.form.get('publication_year', '')
        category_id = request.form.get('category_id', '')
        total_copies = int(request.form.get('total_copies', 1))
        description = request.form.get('description', '').strip()
        language = request.form.get('language', 'English').strip()
        pages = request.form.get('pages', '')
        cover_image = request.form.get('cover_image', '').strip()

        if not title or not author:
            flash('Title and Author are required!', 'danger')
            return render_template('books/add.html', categories=categories)

        # Check duplicate ISBN
        if isbn and Book.query.filter_by(isbn=isbn).first():
            flash('A book with this ISBN already exists!', 'warning')
            return render_template('books/add.html', categories=categories)

        book = Book(
            isbn=isbn or None,
            title=title,
            author=author,
            publisher=publisher or None,
            publication_year=int(publication_year) if publication_year else None,
            category_id=int(category_id) if category_id else None,
            total_copies=total_copies,
            available_copies=total_copies,
            description=description or None,
            language=language,
            pages=int(pages) if pages else None,
            cover_image=cover_image or None,
        )

        db.session.add(book)
        db.session.commit()
        flash(f'Book "{title}" added successfully! 📚', 'success')
        return redirect(url_for('books.index'))

    return render_template('books/add.html', categories=categories)

# ---- ISBN Lookup API ----
@books_bp.route('/isbn-lookup')
@login_required
def isbn_lookup():
    isbn = request.args.get('isbn', '').strip()
    if not isbn:
        return jsonify({'error': 'ISBN required'}), 400
    try:
        url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'
        response = requests.get(url, timeout=5)
        data = response.json()
        key = f'ISBN:{isbn}'
        if key in data:
            book_data = data[key]
            result = {
                'title': book_data.get('title', ''),
                'author': ', '.join([a['name'] for a in book_data.get('authors', [])]),
                'publisher': ', '.join([p['name'] for p in book_data.get('publishers', [])]),
                'year': book_data.get('publish_date', ''),
                'pages': book_data.get('number_of_pages', ''),
                'cover': book_data.get('cover', {}).get('medium', ''),
            }
            return jsonify(result)
        return jsonify({'error': 'Book not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ---- Edit Book ----
@books_bp.route('/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit(book_id):
    book = Book.query.get_or_404(book_id)
    categories = Category.query.all()

    if request.method == 'POST':
        book.isbn = request.form.get('isbn', '').strip() or None
        book.title = request.form.get('title', '').strip()
        book.author = request.form.get('author', '').strip()
        book.publisher = request.form.get('publisher', '').strip() or None
        book.publication_year = int(request.form.get('publication_year')) if request.form.get('publication_year') else None
        book.category_id = int(request.form.get('category_id')) if request.form.get('category_id') else None
        book.total_copies = int(request.form.get('total_copies', 1))
        book.description = request.form.get('description', '').strip() or None
        book.language = request.form.get('language', 'English')
        book.pages = int(request.form.get('pages')) if request.form.get('pages') else None
        book.cover_image = request.form.get('cover_image', '').strip() or None
        book.updated_at = datetime.utcnow()

        if not book.title or not book.author:
            flash('Title and Author are required!', 'danger')
            return render_template('books/edit.html', book=book, categories=categories)

        db.session.commit()
        flash(f'Book "{book.title}" updated successfully! ✅', 'success')
        return redirect(url_for('books.index'))

    return render_template('books/edit.html', book=book, categories=categories)

# ---- Book Detail ----
@books_bp.route('/detail/<int:book_id>')
@login_required
def detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('books/detail.html', book=book)

# ---- Delete Book ----
@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
@admin_required
def delete(book_id):
    book = Book.query.get_or_404(book_id)
    book.is_active = False
    db.session.commit()
    flash(f'Book "{book.title}" deleted successfully!', 'success')
    return redirect(url_for('books.index'))

# ---- Categories ----
@books_bp.route('/categories')
@login_required
@admin_required
def categories():
    cats = Category.query.all()
    return render_template('books/categories.html', categories=cats)

@books_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    description = request.form.get('description', '').strip()
    if not name:
        flash('Category name is required!', 'danger')
        return redirect(url_for('books.categories'))
    if Category.query.filter_by(name=name).first():
        flash('Category already exists!', 'warning')
        return redirect(url_for('books.categories'))
    cat = Category(name=name, description=description or None)
    db.session.add(cat)
    db.session.commit()
    flash(f'Category "{name}" added! ✅', 'success')
    return redirect(url_for('books.categories'))

@books_bp.route('/categories/delete/<int:cat_id>', methods=['POST'])
@login_required
@admin_required
def delete_category(cat_id):
    cat = Category.query.get_or_404(cat_id)
    db.session.delete(cat)
    db.session.commit()
    flash(f'Category "{cat.name}" deleted!', 'success')
    return redirect(url_for('books.categories'))