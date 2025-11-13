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

- **Backend**: Django 5 (Python 3.11+)
- **Database**: SQLite (for MVP deployment)
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

## Render Deployment

### Prerequisites

- GitHub repository with the code pushed
- Render account (sign up at https://render.com)

### Step-by-Step Deployment

1. **Create a new Web Service on Render**:
   - Go to https://dashboard.render.com
   - Click "New +" → "Web Service"
   - Connect your GitHub account if not already connected
   - Select the repository: `she24731/yale-newcomer-survival-guide`

2. **Render will auto-detect `render.yaml`**:
   - Render will automatically detect the `render.yaml` file in your repo
   - It will use the build and start commands defined there

3. **Set environment variables** in Render dashboard:
   
   **Required variables:**
   
   - `DJANGO_SECRET_KEY`: 
     - Generate a secure key by running locally:
       ```bash
       python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
       ```
     - Copy the output and paste it as the value
   
   - `ALLOWED_HOSTS`: 
     - After Render creates your service, you'll get a URL like: `https://yale-newcomer-survival-guide.onrender.com`
     - Set this to: `yale-newcomer-survival-guide.onrender.com` (or whatever your service name is)
     - You can also add multiple hosts separated by commas if needed
   
   **Optional variables (already set in render.yaml):**
   
   - `DEBUG`: Already set to `False` in render.yaml (production mode)
   - Other variables are handled automatically

4. **Deploy**:
   - Click "Create Web Service"
   - Render will:
     - Install dependencies from `requirements.txt`
     - Collect static files (WhiteNoise)
     - Run database migrations
     - Start the app with Gunicorn

5. **After first deployment, set up the database**:
   - Go to Render dashboard → Your service → "Shell"
   - Run these commands:
     ```bash
     python manage.py setup_groups
     python manage.py seed_data
     python manage.py createsuperuser
     ```
   - Follow prompts to create your admin user

6. **Access your application**:
   - Your app will be available at: `https://<your-service-name>.onrender.com`
   - Admin panel: `https://<your-service-name>.onrender.com/admin/`
   - Dashboard: `https://<your-service-name>.onrender.com/dashboard/`

### Environment Variables Summary

| Variable | Required | Description | Example Value |
|----------|----------|-------------|---------------|
| `DJANGO_SECRET_KEY` | Yes | Django secret key for security | (generated string) |
| `ALLOWED_HOSTS` | Yes | Your Render service URL | `yale-newcomer-survival-guide.onrender.com` |
| `DEBUG` | No | Debug mode (set in render.yaml) | `False` |

### Important Notes

- **SQLite Database**: The database file will be stored in the Render filesystem. Note that Render's filesystem is ephemeral, so data may be lost on redeployments. For production, consider using a persistent database service later.
- **Static Files**: WhiteNoise serves static files automatically - no additional configuration needed.
- **Auto-Deploy**: The `render.yaml` is configured to auto-deploy from the `main` branch.

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
