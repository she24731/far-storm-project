# Yale Newcomer Survival Guide

A Django 5 web application that helps Yale newcomers find categorized tips and resources for life in New Haven.

## Features

- **Role-Based Access Control**: Reader, Contributor, and Admin roles
- **Category-Based Content**: Browse posts organized by categories
- **Post Workflow**: Draft → Pending → Approved/Rejected
- **Admin Dashboard**: Custom dashboard at `/dashboard/` for reviewing pending posts
- **Contributor Submission**: Contributors can submit posts for review
- **Search**: Simple keyword search on home page
- **DuckDB Database**: File-backed database with SQLite fallback
- **Bootstrap UI**: Modern, responsive interface

## Tech Stack

- **Backend**: Django 5 (Python 3.11+)
- **Database**: DuckDB (file-backed) with SQLite fallback
- **Frontend**: Django Templates + Bootstrap 5
- **Static Files**: WhiteNoise
- **Deployment**: Docker + Render

## Project Structure

```
yale-newcomer-survival-guide/
├── config/                 # Project configuration package
│   ├── settings.py         # Django settings
│   ├── urls.py            # Root URL configuration
│   ├── wsgi.py            # WSGI application
│   └── asgi.py            # ASGI application
├── core/                   # Main application
│   ├── models.py          # Category, Post, Bookmark, ExternalLink
│   ├── views.py           # All views (home, category, post, submit, dashboard)
│   ├── forms.py           # Post submission form
│   ├── urls.py            # App URL patterns
│   ├── admin.py           # Django admin configuration
│   └── management/
│       └── commands/
│           ├── setup_groups.py  # Create user groups
│           └── seed_data.py     # Seed initial data
├── templates/             # HTML templates
│   ├── base.html
│   ├── core/
│   │   ├── home.html
│   │   ├── category_list.html
│   │   ├── post_detail.html
│   │   ├── submit_post.html
│   │   └── dashboard.html
│   └── registration/
│       └── login.html
├── static/                # Static files
│   └── css/
│       └── app.css
├── app_data/              # Database files (created at runtime)
├── manage.py
├── requirements.txt
├── Dockerfile
├── render.yaml
└── README.md
```

## Local Development Setup

### Prerequisites

- Python 3.11+ (Django 5 requires Python 3.10+)
- pip
- (Optional) Docker for containerized deployment

### Step-by-Step Setup

1. **Create and activate virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Set up user groups**:
   ```bash
   python manage.py setup_groups
   ```

5. **Seed initial data** (creates categories, sample users, and posts):
   ```bash
   python manage.py seed_data
   ```

6. **Create superuser** (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create an admin user. **Important**: Ensure `is_staff=True` is set.

7. **Run development server**:
   ```bash
   python manage.py runserver
   ```

8. **Access the application**:
   - Homepage: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/
   - Dashboard: http://localhost:8000/dashboard/ (admin only)
   - Submit post: http://localhost:8000/submit/ (contributors only)

### Sample Users

After running `seed_data`, you can log in with:

- **Admin**: username: `admin`, password: `admin123`
- **Contributor**: username: `contributor`, password: `contributor123`

## User Roles

- **Reader**: Can view approved posts, browse categories, and search
- **Contributor**: Can submit and edit posts (draft → pending workflow)
- **Admin**: Can approve/reject posts, access `/dashboard/` and `/admin/`

## URLs

- `/` - Home page (category hub + latest posts + search)
- `/c/<slug>/` - Category listing
- `/p/<slug>/` - Post detail
- `/submit/` - Submit new post (contributors only)
- `/submit/<post_id>/` - Edit post (contributors only)
- `/dashboard/` - Admin dashboard (admins only)
- `/dashboard/approve/<post_id>/` - Approve post
- `/dashboard/reject/<post_id>/` - Reject post
- `/admin/` - Django admin panel
- `/login/` - Login page
- `/logout/` - Logout

## Git & GitHub Setup

### Initialize Git Repository

1. **Initialize git** (if not already done):
   ```bash
   git init
   ```

2. **Add all files**:
   ```bash
   git add .
   ```

3. **Create initial commit**:
   ```bash
   git commit -m "Initial commit: Yale Newcomer Survival Guide MVP"
   ```

### Push to GitHub

1. **Create a new repository on GitHub** (do not initialize with README, .gitignore, or license)

2. **Add remote origin** (replace `<YOUR_USERNAME>` and `<REPO_NAME>`):
   ```bash
   git remote add origin https://github.com/<YOUR_USERNAME>/<REPO_NAME>.git
   ```

3. **Push to GitHub**:
   ```bash
   git branch -M main
   git push -u origin main
   ```

**Note**: You will be prompted to authenticate. Use your GitHub credentials or a personal access token.

## Render Deployment

### Prerequisites

- GitHub repository with the code
- Render account

### Step-by-Step Deployment

1. **Create a new Web Service on Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the repository containing this project

2. **Configure the service**:
   - **Name**: `yale-newcomer-survival-guide` (or your preferred name)
   - **Environment**: `Docker`
   - Render will auto-detect the `Dockerfile`

3. **Set environment variables** in Render dashboard:
   - `DJANGO_SECRET_KEY`: Click "Generate" to auto-generate
   - `DEBUG`: Set to `0` (False)
   - `DUCKDB_PATH`: Set to `/var/data/yale_newcomer.duckdb`
   - `ALLOWED_HOSTS`: Will be auto-set by Render (or set to your Render domain)

4. **Add persistent disk**:
   - In the Render dashboard, go to "Disks"
   - Click "Add Disk"
   - **Name**: `yale-guide-data`
   - **Mount Path**: `/var/data`
   - **Size**: 1 GB

5. **Deploy**:
   - Click "Create Web Service"
   - Render will build and deploy your application

6. **Run migrations** (after first deploy):
   - Go to "Shell" in Render dashboard
   - Run:
     ```bash
     python manage.py migrate
     python manage.py setup_groups
     python manage.py seed_data
     python manage.py createsuperuser
     ```

7. **Access your application**:
   - Your app will be available at: `https://<your-service-name>.onrender.com`
   - Admin panel: `https://<your-service-name>.onrender.com/admin/`
   - Dashboard: `https://<your-service-name>.onrender.com/dashboard/`

### Health Check

The health check is configured to use `/admin/login/` as the health check path in `render.yaml`.

## Troubleshooting

### Admin Login Issues

If you cannot log in to `/admin/`:

1. **Verify superuser exists**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Check `is_staff` flag**:
   - In Django shell: `python manage.py shell`
   - Run:
     ```python
     from django.contrib.auth.models import User
     user = User.objects.get(username='admin')
     user.is_staff = True
     user.is_superuser = True
     user.save()
     ```

3. **Check `ALLOWED_HOSTS`**:
   - In production, ensure `ALLOWED_HOSTS` includes your domain
   - In `settings.py`, it's configured via environment variable

### Database Issues

- If DuckDB backend is not available, the app will automatically fallback to SQLite
- Database files are stored in `app_data/` directory (local) or `/var/data/` (Render)

### Static Files

- Static files are served via WhiteNoise in production
- Run `python manage.py collectstatic` before deployment

## Management Commands

- `python manage.py setup_groups` - Create user groups
- `python manage.py seed_data` - Seed initial data
- `python manage.py migrate` - Run database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files

## Development Workflow

1. Make changes locally
2. Test with `python manage.py runserver`
3. Commit changes: `git add . && git commit -m "Description"`
4. Push to GitHub: `git push origin main`
5. Render will auto-deploy (if auto-deploy is enabled)

## License

This project is for educational purposes as part of the Management of Software Development course at Yale.

## Contact

For issues or questions, contact: chun-hung.yeh@yale.edu
