# 🔍 HireSense — Job Search & Application Platform

A backend-focused, full-stack job search web application built with **Python**, **Flask**, and **MySQL**. The core of this project is a well-structured Flask backend with modular SQLAlchemy database queries, secure authentication using bcrypt, session-based access control, and parameterized SQL search — served through Jinja2 templates with a Bootstrap UI.

![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.1-black?logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?logo=mysql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

<p align="center">
  <a href="https://job-search-website-s9sr.onrender.com/"><strong>🌐 Live Demo</strong></a> &nbsp;•&nbsp;
  <a href="https://github.com/banerjee003/Job-Search-Website"><strong>💻 GitHub Repo</strong></a>
</p>

---

## ✨ Features

### 🐍 Backend & Database
- **Flask Application Factory** — Clean route definitions with `app.py` as the single entry point handling 8+ routes
- **SQLAlchemy Core** — Raw SQL queries via `text()` with parameterized bindings to prevent SQL injection
- **MySQL Database** — Relational schema with 3 normalized tables (`users`, `jobs`, `applications`) connected via foreign keys
- **Server-Side Search** — SQL `LIKE` query matching against `title`, `company`, and `location` columns with wildcard parameters
- **Secure Authentication** — bcrypt password hashing with salt generation, session-based login/logout, and route-level access guards
- **CSRF Protection** — Flask-WTF `CSRFProtect` applied globally across all POST forms
- **Environment Configuration** — Secrets and DB connection strings loaded via `python-dotenv`, never hardcoded
- **Form Validation** — WTForms with custom validators (e.g., duplicate email check queries the DB in real-time)
- **Application Tracking** — SQL `JOIN` queries linking `jobs` and `applications` tables to build the user's application history

### 🌐 Frontend (Jinja2 + Bootstrap)
- Server-side rendered templates with Jinja2
- Bootstrap 5 responsive layout
- Reusable template components via `{% include %}`

---

## 🗄️ Database Schema

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│      users       │     │   applications   │     │      jobs        │
├──────────────────┤     ├──────────────────┤     ├──────────────────┤
│ user_id (PK)     │────▶│ user_id (FK)     │     │ job_id (PK)      │
│ name             │     │ job_id (FK)      │◀────│ title            │
│ email (unique)   │     │ status           │     │ company          │
│ password (hash)  │     │ applied_on       │     │ location         │
│ headline         │     └──────────────────┘     │ salary           │
│ linkedin_url     │                              │ currency         │
│ education        │                              │ responsibility   │
│ work_experience  │                              │ requirements     │
│ resume_url       │                              └──────────────────┘
└──────────────────┘
```

---

## 🛠️ Tech Stack

| Layer            | Technology                                    |
|------------------|-----------------------------------------------|
| **Language**     | Python 3.x                                    |
| **Framework**    | Flask 3.1                                     |
| **Database**     | MySQL (via PyMySQL driver)                    |
| **ORM / Queries**| SQLAlchemy Core (`text()` with param binding) |
| **Auth**         | bcrypt (hashing + salt), Flask sessions       |
| **Forms**        | Flask-WTF, WTForms (with custom validators)   |
| **Security**     | CSRF tokens, parameterized queries, dotenv    |
| **Templating**   | Jinja2 (server-side rendering)                |
| **Frontend**     | Bootstrap 5                                   |
| **Deployment**   | Gunicorn (production WSGI server)             |

---

## ⚙️ Backend Architecture

### Route Map (`app.py`)

| Method     | Route                    | Auth Required | Description                          |
|------------|--------------------------|:------------:|---------------------------------------|
| `GET`      | `/`                      | ✗            | Homepage — loads all jobs from DB     |
| `GET`      | `/search?q=`             | ✗            | Search jobs by title/company/location |
| `GET/POST` | `/register`              | ✗            | User registration with validation     |
| `GET/POST` | `/login`                 | ✗            | User login with bcrypt verification   |
| `GET`      | `/logout`                | ✓            | Clear session and redirect            |
| `GET`      | `/jobs/<job_id>`         | ✓            | View job details + apply section      |
| `POST`     | `/jobs/<job_id>/apply`   | ✓            | Submit application to DB              |
| `GET/POST` | `/dashboard`             | ✓            | User profile + application tracker    |
| `GET/POST` | `/edit`                  | ✓            | Edit user profile                     |
| `GET`      | `/api/jobs`              | ✗            | JSON API — returns all jobs           |

### Database Layer (`database.py`)

All database operations are isolated in `database.py` using **SQLAlchemy Core**:

```python
# Example: Parameterized search query (prevents SQL injection)
def search_jobs_from_db(query):
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT * FROM jobs WHERE title LIKE :q OR company LIKE :q OR location LIKE :q"),
            {"q": f"%{query}%"}
        )
        return [dict(row._mapping) for row in result.all()]
```

Key database functions:
| Function                     | SQL Operation                         |
|------------------------------|---------------------------------------|
| `load_jobs_from_db()`        | `SELECT * FROM jobs`                  |
| `load_one_job_from_db(id)`   | `SELECT ... WHERE job_id = :val`      |
| `search_jobs_from_db(query)` | `SELECT ... WHERE title LIKE :q OR ...`|
| `add_users_to_db(...)`       | `INSERT INTO users (...)`             |
| `get_user_from_db(email)`    | `SELECT ... WHERE email = :email`     |
| `add_application_to_db(...)` | `INSERT INTO applications (...)`      |
| `get_application_info_from_db(uid)` | `JOIN jobs ON applications`    |
| `had_user_applied(uid, jid)` | `SELECT 1 ... LIMIT 1` (existence check)|
| `update_user_profile(...)`   | `UPDATE users SET ... WHERE user_id`  |

### Authentication Flow

```
Register → bcrypt.hashpw(password, salt) → INSERT into users
Login    → SELECT user by email → bcrypt.checkpw() → session['user_id'] = id
Logout   → session.clear() → redirect to login
Guards   → session.get('user_id') checked on protected routes
```

---

## 📁 Project Structure

```
HireSense/
├── app.py                  # Flask app — routes, forms, auth, session logic
├── database.py             # All SQL queries (SQLAlchemy Core)
├── requirements.txt        # Python dependencies
├── .env                    # DB_CONNECTION_STRING + APP_SECRET_KEY
├── static/
│   ├── style.css
│   └── images/
└── templates/
    ├── index.html           # Homepage + search
    ├── navbar.html          # Navigation bar
    ├── job_items.html       # Job card component
    ├── jobpage.html         # Job details + apply
    ├── login.html           # Login form
    ├── register.html        # Registration form
    ├── dashboard.html       # User dashboard
    ├── edit_profile.html    # Profile editor
    ├── application_form.html
    └── footer.html
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- MySQL server running
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone YOUR_GITHUB_LINK_HERE
   cd HireSense
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv myenv
   
   # Windows
   .\myenv\Scripts\activate
   
   # macOS / Linux
   source myenv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Create a `.env` file:
   ```env
   DB_CONNECTION_STRING=mysql+pymysql://username:password@host/database_name
   APP_SECRET_KEY=your-secret-key-here
   ```

5. **Set up MySQL tables**

   ```sql
   CREATE TABLE jobs (
       job_id INT PRIMARY KEY AUTO_INCREMENT,
       title VARCHAR(255),
       company VARCHAR(255),
       location VARCHAR(255),
       salary INT,
       currency VARCHAR(10),
       responsibility TEXT,
       requirements TEXT
   );

   CREATE TABLE users (
       user_id INT PRIMARY KEY AUTO_INCREMENT,
       name VARCHAR(255),
       email VARCHAR(255) UNIQUE,
       password VARCHAR(255),
       headline VARCHAR(255),
       linkedin_url VARCHAR(500),
       education VARCHAR(500),
       work_experience VARCHAR(500),
       resume_url VARCHAR(500)
   );

   CREATE TABLE applications (
       user_id INT,
       job_id INT,
       status VARCHAR(50),
       applied_on DATE,
       FOREIGN KEY (user_id) REFERENCES users(user_id),
       FOREIGN KEY (job_id) REFERENCES jobs(job_id)
   );
   ```

6. **Run the app**
   ```bash
   python app.py
   ```

7. **Visit** → `http://127.0.0.1:5000`

---

## 🔗 Links

| | Link |
|---|---|
| 🌐 **Live App** | [YOUR_LIVE_APP_LINK_HERE](YOUR_LIVE_APP_LINK_HERE) |
| 💻 **GitHub** | [YOUR_GITHUB_LINK_HERE](YOUR_GITHUB_LINK_HERE) |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -m 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Open a Pull Request

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  Built with ❤️ using Python, Flask & MySQL
</p>