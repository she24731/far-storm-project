# Yale Newcomer Survival Guide

A Django 5 web application that helps Yale newcomers find categorized tips and resources for life in New Haven.

## Features

- **Role-Based Access Control**: Reader, Contributor, and Admin roles
- **Category-Based Content**: Browse posts organized by categories
- **Post Workflow**: Draft → Pending → Approved/Rejected
- **Admin Dashboard**: Custom dashboard at `/dashboard/` for reviewing pending posts
- **Contributor Submission**: Contributors can submit posts for review
- **Search**: Simple keyword search on home page
- **Bootstrap UI**: Modern, responsive interface

## Tech Stack

- **Backend**: Django 4.2 (Python 3.9+)
- **Database**: PostgreSQL (production via Render), SQLite (local development)
- **Frontend**: Django Templates + Bootstrap 5
- **Static Files**: WhiteNoise
- **Production Server**: Gunicorn
- **Deployment**: Render

## Local Development Setup

### Prerequisites

- Python 3.11+ (Django 5 requires Python 3.10+)
- pip

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
   Follow the prompts. Example: username `admin`, password `admin19891217`

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

## Git & GitHub Setup

### Push to GitHub

1. **Create a new repository on GitHub**:
   - Go to https://github.com/new
   - Repository name: `yale-newcomer-survival-guide`
   - **Do NOT** initialize with README, .gitignore, or license (we already have these)

2. **Add remote and push** (run these commands):
   ```bash
   git remote add origin https://github.com/she24731/yale-newcomer-survival-guide.git
   git branch -M main
   git push -u origin main
   ```

   You will be prompted to authenticate. Use your GitHub credentials or a personal access token.

## Deployment

### Environments

#### Production

- **URL**: https://yale-newcomer-survival-guide.onrender.com
- **Platform**: Render Web Service
- **Branch**: `main` (auto-deploy enabled)
- **Database**: Render PostgreSQL via `DATABASE_URL` environment variable
- **DEBUG**: `False` (production mode)

**Production Environment Variables** (set in Render dashboard):

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key for security | Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `DATABASE_URL` | Yes | PostgreSQL connection string | Auto-provided by Render PostgreSQL service |
| `DEBUG` | No | Debug mode | `False` (set in render.yaml) |
| `RENDER_EXTERNAL_HOSTNAME` | Auto | Render hostname | Auto-set by Render, added to `ALLOWED_HOSTS` |
| `DJANGO_ADMIN_INITIAL_PASSWORD` | Optional | Initial admin password | (if using auto-admin setup) |

**Note**: Google Analytics measurement ID (`G-9XJWT2P5LE`) is currently hardcoded in `templates/base.html`. This is acceptable as GA IDs are not sensitive.

#### Staging

- **URL**: https://`<your-staging-service>`.onrender.com *(placeholder - create a separate Render service)*
- **Current Status**: Currently, staging and production share the same Render service. For the course, we conceptually treat this as production. A separate staging service can be added later following these steps.

**Recommended Staging Setup** (for future):

1. Create a second Render Web Service from the same GitHub repository
2. Configure with separate environment variables:
   - Same `DJANGO_SECRET_KEY` approach (generate a different key for staging)
   - Point to the same `DATABASE_URL` or a separate PostgreSQL instance depending on your needs
   - Set `DEBUG=False` for staging (or `True` for testing, then switch to `False`)
   - Configure `RENDER_EXTERNAL_HOSTNAME` to the staging service URL
3. Optionally configure a different branch (e.g., `develop`) for staging deployments
4. Use staging to test deployments before promoting to production

**Note**: If a separate staging service is not created, the single service at `yale-newcomer-survival-guide.onrender.com` serves as the production deployment.

### Deployment Procedure

#### Initial Setup

1. **Push code to GitHub** on the `main` branch
2. **Create Web Service on Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect GitHub account if not already connected
   - Select repository: `she24731/yale-newcomer-survival-guide`
   - Render will auto-detect `render.yaml`

3. **Set Environment Variables** in Render dashboard:
   - Go to your service → "Environment" tab
   - Add all required variables (see Production Environment Variables above)
   - `DATABASE_URL` is automatically provided if you've linked a PostgreSQL database

4. **Create PostgreSQL Database** (if not already created):
   - In Render dashboard, create a new PostgreSQL database
   - Render will automatically set the `DATABASE_URL` environment variable
   - The database connection is configured via `dj-database-url` in `config/settings.py`

5. **Deploy**:
   - Click "Create Web Service" or enable auto-deploy
   - Render will:
     - Install dependencies from `requirements.txt`
     - Run `python manage.py collectstatic --noinput`
     - Run `python manage.py migrate` (migrations run automatically)
     - Start app with Gunicorn: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

6. **After first deployment, set up database**:
   - Go to Render dashboard → Your service → "Shell"
   - Run these commands:
     ```bash
     python manage.py setup_groups
     python manage.py seed_data
     python manage.py createsuperuser
     ```
   - Follow prompts to create your admin user

#### Ongoing Deployments

**For Production**:
- **Option A (Auto-deploy)**: Push to `main` branch → Render automatically deploys
- **Option B (Manual)**: In Render dashboard, click "Deploy latest commit"

**For Staging** (once created):
- Same process, but deploy to the staging service dashboard
- Can point to a different branch if configured

### Migrations

Migrations are handled automatically:
- **Build command**: Includes `python manage.py migrate` (see `render.yaml`)
- Migrations run on every deployment
- No manual migration steps required after initial setup

### Logs

- View deployment logs in Render dashboard → Your service → "Logs" tab
- Application logs (stdout/stderr) are available in real-time
- Use logs to troubleshoot deployment issues

### 12-Factor Configuration

This project follows 12-factor principles:

- ✅ **Config via environment variables**: All sensitive settings (SECRET_KEY, DATABASE_URL, DEBUG) come from environment variables
- ✅ **Database configured via DATABASE_URL**: Uses `dj-database_url` with SQLite fallback for local development
- ✅ **No secrets in code**: All secrets are read from environment variables
- ✅ **ALLOWED_HOSTS dynamically configured**: Automatically includes `RENDER_EXTERNAL_HOSTNAME`
- ✅ **Static files via WhiteNoise**: Served automatically, no additional configuration needed
- ✅ **Port binding**: Gunicorn binds to `$PORT` (provided by Render)

**Local Development**: Uses SQLite and defaults to `DEBUG=True` via environment variable  
**Production**: Uses PostgreSQL via `DATABASE_URL` and `DEBUG=False`

### Important Notes

- **PostgreSQL Database**: Production uses Render PostgreSQL, configured via `DATABASE_URL`. The database connection string is automatically provided by Render when you link a PostgreSQL service.
- **Static Files**: WhiteNoise serves static files automatically - no additional configuration needed.
- **Auto-Deploy**: The `render.yaml` is configured to auto-deploy from the `main` branch.
- **Health Check**: Configured at `/admin/login/` (see `render.yaml`)

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

## Management Commands

- `python manage.py setup_groups` - Create user groups
- `python manage.py seed_data` - Seed initial data
- `python manage.py migrate` - Run database migrations
- `python manage.py createsuperuser` - Create admin user
- `python manage.py collectstatic` - Collect static files (for production)

## Troubleshooting

### Admin Login Issues

If you cannot log in to `/admin/`:

1. **Verify superuser exists**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Check `is_staff` flag** (in Django shell):
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

### Render Deployment Issues

- **Build fails**: Check that all dependencies are in `requirements.txt`
- **Static files not loading**: Ensure `collectstatic` runs in build command (already in render.yaml)
- **Database errors**: Run migrations in Render Shell after first deploy
- **500 errors**: Check Render logs and ensure `ALLOWED_HOSTS` includes your Render URL

## License

This project is for educational purposes as part of the Management of Software Development course at Yale.
