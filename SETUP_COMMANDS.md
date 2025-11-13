# Setup Commands - Quick Reference

## Local Development

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py migrate

# 4. Set up user groups
python manage.py setup_groups

# 5. Seed initial data
python manage.py seed_data

# 6. Create superuser (for admin access)
python manage.py createsuperuser
# Follow prompts - IMPORTANT: Ensure is_staff=True

# 7. Run development server
python manage.py runserver
```

## Git & GitHub

```bash
# Initialize (already done)
git init

# Add files (already done)
git add .

# Commit (already done)
git commit -m "Initial commit: Yale Newcomer Survival Guide MVP"

# Add remote (replace YOUR_USERNAME and REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## Render Deployment

1. Create new Web Service on Render
2. Connect GitHub repository
3. Auto-detect Docker
4. Set environment variables:
   - `DJANGO_SECRET_KEY` (generate)
   - `DEBUG=0`
   - `DUCKDB_PATH=/var/data/yale_newcomer.duckdb`
5. Add persistent disk: `/var/data`, 1GB
6. Deploy
7. Run migrations in Render Shell:
   ```bash
   python manage.py migrate
   python manage.py setup_groups
   python manage.py seed_data
   python manage.py createsuperuser
   ```

## Verify Admin Login

After creating superuser, verify:
- Can access `/admin/`
- Can access `/dashboard/`
- `is_staff=True` is set

If login fails:
```bash
python manage.py shell
```
Then:
```python
from django.contrib.auth.models import User
user = User.objects.get(username='admin')
user.is_staff = True
user.is_superuser = True
user.save()
```

