# Project Summary - Yale Newcomer Survival Guide

## ✅ Deliverables Completed

### 1. Project Structure
- ✅ Project package: `config/` (settings, urls, wsgi, asgi)
- ✅ Main app: `core/` (models, views, forms, admin, urls)
- ✅ Templates: `templates/` with base.html and all required pages
- ✅ Static files: `static/css/app.css`
- ✅ Management commands: `core/management/commands/`

### 2. Models
- ✅ `Category` (name, slug, description, created_at)
- ✅ `Post` (title, slug, content, category, author, status, updated_at, published_at)
- ✅ `Bookmark` (user, post, unique_together)
- ✅ `ExternalLink` (title, url, category)
- ✅ Database indexes on posts(status), posts(category_id), posts(updated_at)

### 3. Views & URLs
- ✅ `/` - Home (category hub + latest approved posts + search)
- ✅ `/c/<slug>/` - Category listing
- ✅ `/p/<slug>/` - Post detail
- ✅ `/submit/` - Contributor submit post
- ✅ `/submit/<post_id>/` - Edit post
- ✅ `/dashboard/` - Admin dashboard (staff only)
- ✅ `/dashboard/approve/<post_id>/` - Approve post
- ✅ `/dashboard/reject/<post_id>/` - Reject post
- ✅ `/admin/` - Django admin
- ✅ `/login/` - Login
- ✅ `/logout/` - Logout

### 4. Authentication & Permissions
- ✅ Django auth system with Groups
- ✅ Reader, Contributor, Admin roles
- ✅ Role-based access control
- ✅ Admin dashboard protected with `@user_passes_test(is_admin)`
- ✅ Contributor submit protected with `@user_passes_test(is_contributor)`

### 5. Database Configuration
- ✅ DuckDB with SQLite fallback
- ✅ Environment variable: `DUCKDB_PATH` (defaults to `app_data/yale_newcomer.duckdb`)
- ✅ Auto-creates `app_data/` directory
- ✅ Proper error handling for missing DuckDB backend

### 6. Deployment
- ✅ Dockerfile (Python 3.11, gunicorn with 1 worker)
- ✅ render.yaml (Docker, persistent disk, env vars)
- ✅ WhiteNoise for static files
- ✅ Health check configured

### 7. Git & GitHub
- ✅ Git repository initialized
- ✅ Initial commit created
- ✅ .gitignore configured
- ✅ README with push instructions (no credentials)

### 8. Management Commands
- ✅ `setup_groups` - Create user groups
- ✅ `seed_data` - Seed categories, users, posts

## File Tree

```
yale-newcomer-survival-guide/
├── config/                      # Project configuration
│   ├── __init__.py
│   ├── settings.py             # Django settings with DuckDB config
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application
│   └── asgi.py                  # ASGI application
├── core/                        # Main application
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py                # Category, Post, Bookmark, ExternalLink
│   ├── views.py                 # All views including dashboard
│   ├── forms.py                 # Post submission form
│   ├── urls.py                  # App URL patterns
│   ├── admin.py                 # Django admin configuration
│   └── management/
│       └── commands/
│           ├── __init__.py
│           ├── setup_groups.py # Create user groups
│           └── seed_data.py    # Seed initial data
├── templates/
│   ├── base.html               # Base template
│   ├── core/
│   │   ├── home.html           # Home page
│   │   ├── category_list.html  # Category listing
│   │   ├── post_detail.html    # Post detail
│   │   ├── submit_post.html    # Submit/edit post
│   │   └── dashboard.html      # Admin dashboard
│   └── registration/
│       └── login.html          # Login page
├── static/
│   └── css/
│       └── app.css             # Custom CSS
├── app_data/                    # Database files (created at runtime)
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Docker configuration
├── render.yaml                  # Render deployment config
├── .gitignore                   # Git ignore rules
├── .dockerignore                # Docker ignore rules
├── README.md                    # Comprehensive documentation
└── SETUP_COMMANDS.md            # Quick reference commands
```

## Exact Commands to Run

### A) Run Locally

```bash
# 1. Activate virtual environment
source venv/bin/activate  # (or create new: python3 -m venv venv)

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Set up user groups
python manage.py setup_groups

# 5. Seed initial data
python manage.py seed_data

# 6. Create superuser (IMPORTANT: set is_staff=True)
python manage.py createsuperuser

# 7. Run server
python manage.py runserver
```

**Access:**
- Home: http://localhost:8000/
- Admin: http://localhost:8000/admin/
- Dashboard: http://localhost:8000/dashboard/ (admin only)

**Sample Users (from seed_data):**
- Admin: `admin` / `admin123`
- Contributor: `contributor` / `contributor123`

### B) Push to GitHub

```bash
# 1. Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 2. Push to GitHub
git branch -M main
git push -u origin main
```

**Note:** You will be prompted to authenticate. Use your GitHub credentials.

### C) Deploy on Render

1. **Create Web Service:**
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub repository
   - Select repository

2. **Configure:**
   - Name: `yale-newcomer-survival-guide`
   - Environment: `Docker` (auto-detects Dockerfile)

3. **Set Environment Variables:**
   - `DJANGO_SECRET_KEY`: Click "Generate"
   - `DEBUG`: `0`
   - `DUCKDB_PATH`: `/var/data/yale_newcomer.duckdb`
   - `ALLOWED_HOSTS`: (auto-set by Render)

4. **Add Persistent Disk:**
   - Go to "Disks" tab
   - Add disk: name `yale-guide-data`, mount `/var/data`, size 1GB

5. **Deploy:**
   - Click "Create Web Service"
   - Wait for build to complete

6. **Run Migrations (in Render Shell):**
   ```bash
   python manage.py migrate
   python manage.py setup_groups
   python manage.py seed_data
   python manage.py createsuperuser
   ```

7. **Access:**
   - Your app: `https://<service-name>.onrender.com`
   - Admin: `https://<service-name>.onrender.com/admin/`
   - Dashboard: `https://<service-name>.onrender.com/dashboard/`

## Key Features Implemented

1. **Admin Dashboard** (`/dashboard/`):
   - Lists pending posts with Approve/Reject buttons
   - Lists draft posts
   - Only accessible to staff users
   - Uses `@user_passes_test(is_admin)` decorator

2. **Contributor Submission** (`/submit/`):
   - Form for creating/editing posts
   - Contributors can set status to "draft" or "pending"
   - Only Contributors and Admins can access
   - Uses `@user_passes_test(is_contributor)` decorator

3. **Post Workflow**:
   - Draft → Pending → Approved/Rejected
   - Auto-sets `published_at` when approved
   - Role-based visibility

4. **Search**:
   - Simple keyword search on home page
   - Searches post titles and content

5. **DuckDB Configuration**:
   - Tries to import `duckdb_backend`
   - Falls back to SQLite if unavailable
   - Creates `app_data/` directory automatically
   - Configurable via `DUCKDB_PATH` env var

## Admin Login Verification

After creating superuser, verify:
1. Can access `/admin/` - Django admin panel
2. Can access `/dashboard/` - Custom admin dashboard
3. User has `is_staff=True` and `is_superuser=True`

If login fails:
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.is_staff = True
user.is_superuser = True
user.save()
```

## Notes

- **Python Version**: Django 5 requires Python 3.10+. If using Python 3.9, change `requirements.txt` to `Django==4.2.26`
- **Old Files**: Some old files from previous structure (guide/, yale_newcomer_survival_guide/) exist but are not used. The active structure uses `config/` and `core/`.
- **Database**: DuckDB backend may not be available; app automatically falls back to SQLite.
- **Static Files**: Served via WhiteNoise in production.

## Contact

For questions: chun-hung.yeh@yale.edu

