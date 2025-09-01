# Metro Reads - A Django Library Management System

![Build Status](https://img.shields.io/badge/build-passing-brightgreen)![Python Version](https://img.shields.io/badge/python-3.11-blue)![Django Version](https://img.shields.io/badge/django-5.x-blueviolet)![License](https://img.shields.io/badge/license-MIT-lightgrey)

A comprehensive, production-ready Library Management System built with Django, DRF, PostgreSQL, Redis, and Celery, all orchestrated with Docker and ready for cloud deployment.

## 📖 Overview

Metro Reads is a full-stack backend system designed to manage the core operations of a modern academic or public library. It provides a robust API for handling users, books, loans, and fines, and includes advanced features like a real-time queuing system for popular books, automated email notifications, and on-demand generation of digital library cards.

The entire application is containerized with Docker for consistent development and seamless deployment to platforms like Render or Railway.

## ✨ Features

-   **User Management:**
    -   Secure JWT-based authentication.
    -   Role-based access control (`Admin`, `Librarian`, `Member`).
    -   Automated email verification for new user registrations.
    -   User profile management with optional profile pictures.
-   **Book & Loan System:**
    -   Full CRUD API for managing the book catalog.
    -   Robust logic for borrowing and returning books.
    -   Inventory tracking (`total_copies` vs. `available_copies`).
-   **High-Performance Caching:**
    -   Redis caching for book searches and detail views to reduce database load.
    -   Automatic cache invalidation when book data changes.
-   **Automated Queue System:**
    -   Users can join a waiting list for unavailable books.
    -   Celery-powered FIFO promotion system automatically reserves books for the next user in line.
    -   Automated email notifications inform users when their reservation is ready.
-   **Fine Management System:**
    -   Celery Beat task runs daily to calculate fines for overdue books.
    -   Configurable fine-per-day setting in the admin panel.
    -   Automated daily email reminders for users with outstanding fines.
-   **Digital Library Cards:**
    -   On-demand PDF library card generation for members.
    -   Professionally designed, two-sided card with library branding.
    -   Includes user photo (with fallback) and a scannable QR code linking to their profile.
-   **Production-Ready Admin Panel:**
    -   Custom dashboard homepage with KPIs and widgets (e.g., Active Loans, Overdue Books, Top 5 Longest Queues).
    -   Enhanced `ModelAdmin` views for easy management of all library data.
-   **Deployment Ready:**
    -   Fully containerized with a multi-stage `Dockerfile`.
    -   Includes a production startup script (`entrypoint.sh`) that handles database migrations and superuser creation.
    -   Configured with `whitenoise` for efficient static file serving in production.

## 🛠️ Tech Stack

| Category           | Technology                                     |
| ------------------ | ---------------------------------------------- |
| **Backend**        | Python 3.11, Django 5.x, Django REST Framework |
| **Database**       | PostgreSQL 17                                  |
| **Cache & Broker** | Redis 8                                        |
| **Async Tasks**    | Celery 5, Celery Beat                          |
| **API Docs**       | `drf-yasg` (Swagger & ReDoc)                   |
| **Authentication** | `djangorestframework-simplejwt`                |
| **PDF Generation** | `reportlab`, `qrcode`, `Pillow`                |
| **Deployment**     | Docker, Gunicorn, `whitenoise`                 |
| **Testing**        | `unittest`, `locust` (for load testing)        |

## 📂 Project Structure

```
metro-reads-library/
├── .env                  # Local environment variables
├── Dockerfile              # Production-ready multi-stage Dockerfile
├── docker-compose.yml      # Local development environment setup
├── entrypoint.sh           # Production startup script
├── locustfile.py
├── manage.py
├── README.md               # You are here
├── requirements.txt        # Production Python dependencies
├── config/                 # Django project configuration
├── apps/                   # All custom Django applications
│   ├── users/
│   ├── books/
│   ├── loans/
│   ├── cards/
│   ├── queues/
│   ├── site_config/
│   └── academic/
├── media/                  # User-uploaded files (profile pics, PDFs)
├── static/                 # Project-wide static assets (logo.png)
└── templates/              # HTML templates (admin dashboard, emails)
```

## 🚀 Getting Started (Local Development)

### Prerequisites

-   Git
-   Docker & Docker Compose

### 1. Clone the Repository

```bash
git clone https://github.com/imsay3m/metro-reads-server
cd metro-reads-library
```

### 2. Configure Environment Variables

Create a `.env` file in the project root. You can copy the example:

```bash
cp .env.example .env
```

Now, open the `.env` file and fill in the required values, especially `SECRET_KEY`, `MAIL_USER`, and `MAIL_PASSWORD`.

### 3. Build and Run the Application

This command will build the Docker images and start all the services (web, db, redis, celery, etc.).

```bash
docker-compose up --build -d
```

### 4. Initialize the Database

Run the database migrations and create your first superuser for the admin panel.

```bash
# Apply migrations
docker-compose exec web python manage.py migrate

# Create an admin user
docker-compose exec web python manage.py createsuperuser
```

### 5. First-Time Admin Setup

1.  Navigate to `http://localhost/admin/` in your browser.
2.  Log in with the superuser you just created.
3.  In the sidebar, find **SITE_CONFIG** and click on **Library Settings**.
4.  Click **"Add Library Settings"** and then **Save**. This initializes the default fine rate.

**Your local environment is now running!**

-   **API:** `http://localhost/api/`
-   **Admin Panel:** `http://localhost/admin/`
-   **API Docs (Swagger):** `http://localhost/swagger/`

## Swagger API

The API is documented automatically via Swagger and ReDoc. However, here are some key endpoints for quick reference.

**Authentication Header:** All protected endpoints require an `Authorization` header with the value `Bearer <your_access_token>`.

### Authentication

-   **Register User:** `POST /api/users/register/`
    -   **Auth:** Public
    -   **Body:** `{ "email": "...", "password": "...", "first_name": "...", "last_name": "..." }`
-   **Login (Get Token):** `POST /api/users/login/`
    -   **Auth:** Public
    -   **Body:** `{ "email": "...", "password": "..." }`
-   **Verify Account:** `GET /api/users/verify/<uidb64>/<token>/`
    -   **Auth:** Public (link from email)

### Books

-   **List/Search Books:** `GET /api/books/`
    -   **Auth:** Authenticated
    -   **Query Params:** `?search=<query>`
-   **Create Book:** `POST /api/books/`
    -   **Auth:** Admin/Librarian

### Loans

-   **Borrow a Book:** `POST /api/loans/`
    -   **Auth:** Authenticated
    -   **Body:** `{ "book": <book_id> }`
-   **Return a Book:** `POST /api/loans/<loan_id>/return/`
    -   **Auth:** Authenticated (must be the user who borrowed it)

### Queues

-   **Join a Queue:** `POST /api/books/<book_id>/join-queue/`
    -   **Auth:** Authenticated
-   **View My Queues:** `GET /api/queues/`
    -   **Auth:** Authenticated

## ⚙️ Environment Variables

The following environment variables are used for configuration. For production, these should be set in your hosting provider's dashboard (e.g., Render, Railway).

| Variable               | Description                                                     | Example                                 |
| ---------------------- | --------------------------------------------------------------- | --------------------------------------- |
| `SECRET_KEY`           | **Required.** A long, random string for cryptographic signing.  | `your-super-secret-key-here`            |
| `DEBUG`                | Set to `True` for development, `False` for production.          | `False`                                 |
| `DATABASE_URL`         | **Required in Prod.** The full connection URL for PostgreSQL.   | `postgres://user:pass@host:port/dbname` |
| `REDIS_URL`            | **Required in Prod.** The full connection URL for Redis.        | `rediss://:pass@host:port`              |
| `ALLOWED_HOSTS`        | **Required in Prod.** Comma-separated list of allowed domains.  | `metro-reads.onrender.com`              |
| `CSRF_TRUSTED_ORIGINS` | **Required in Prod.** Comma-separated list of frontend origins. | `https://metro-reads-frontend.com`      |
| `MAIL_USER`            | Your Gmail address for sending emails.                          | `youremail@gmail.com`                   |
| `MAIL_PASSWORD`        | Your 16-character Gmail "App Password".                         | `abcd efgh ijkl mnop`                   |
| `ADMIN_EMAIL`          | The email for the auto-created superuser.                       | `admin@example.com`                     |
| `ADMIN_PASSWORD`       | The password for the auto-created superuser.                    | `a-very-strong-password`                |
| `ADMIN_FIRST_NAME`     | The first name for the auto-created superuser.                  | `Admin`                                 |
| `ADMIN_LAST_NAME`      | The last name for the auto-created superuser.                   | `User`                                  |

## 📜 License

This project is licensed under the MIT License. See the `LICENSE` file for details.
