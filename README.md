# 📚 LibrarySphere — Advanced Library Management System

A full-featured Library Management System built with **Python Flask**, **MySQL**, and **Bootstrap 5**.

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![MySQL](https://img.shields.io/badge/MySQL-8.x-orange?logo=mysql)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap)

---

## 🌟 Features

- 🔐 **Authentication** — Secure login with role-based access control
- 📊 **Dashboard** — Real-time KPI cards and Chart.js analytics
- 📚 **Books Management** — Full CRUD with ISBN auto-lookup via Open Library API
- 👥 **Member Management** — Auto member code generation, membership renewal
- 🔄 **Issue & Return** — Book issuing, returning, and renewal system
- 💰 **Fines Management** — Automatic fine calculation @ ₹5/day
- 📈 **Reports & Analytics** — Visual reports with charts
- 👤 **User Management** — Admin can create/manage librarian accounts

---

## 🔑 Role-Based Access

| Feature | Admin | Librarian |
|---|---|---|
| Dashboard | ✅ | ✅ |
| Books CRUD | ✅ | ✅ |
| Delete Books / Categories | ✅ | ❌ |
| Members CRUD | ✅ | ✅ |
| Suspend Members | ✅ | ❌ |
| Issue & Return | ✅ | ✅ |
| Collect Fines | ✅ | ✅ |
| Waive Fines | ✅ | ❌ |
| Reports | ✅ | ✅ |
| User Management | ✅ | ❌ |

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11, Flask 3.x, SQLAlchemy ORM, Flask-Migrate
- **Frontend:** Bootstrap 5, Jinja2, Chart.js, Material Icons
- **Database:** MySQL 8.x
- **Auth:** Flask-Login, Flask-Bcrypt, Flask-WTF (CSRF)

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/avaleajay170/LibrarySphere.git
cd LibrarySphere
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Create `.env` file
```env
SECRET_KEY=your-secret-key
DATABASE_URL=mysql+pymysql://root:root@localhost/library_ms
FINE_PER_DAY=5.0
LOAN_DAYS=14
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your@gmail.com
MAIL_PASSWORD=your_app_password
```

### 5. Setup Database
```bash
mysql -u root -p
CREATE DATABASE library_ms;
exit
```
```bash
flask db upgrade
python seed.py
```

### 6. Run the project
```bash
python run.py
```

Visit: **http://127.0.0.1:5000**

---

## 🔐 Default Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| Librarian | `librarian` | `Librarian@123` |

---

## 📁 Project Structure
```
LibrarySphere/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Blueprint routes
│   ├── templates/       # Jinja2 HTML templates
│   ├── static/          # CSS, JS assets
│   ├── __init__.py      # App factory
│   ├── config.py        # Configuration
│   └── forms.py         # WTForms
├── migrations/          # Flask-Migrate files
├── .env                 # Environment variables (not committed)
├── .gitignore
├── requirements.txt
├── run.py               # Entry point
└── seed.py              # Database seeder
```

---

## 📸 Screenshots

> Dashboard, Books, Members, Issues, Fines, Reports modules

---

## 📄 License

MIT License — feel free to use and modify.

---

Built with ❤️ by [@avaleajay170](https://github.com/avaleajay170)