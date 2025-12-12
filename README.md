# Yale Newcomer Survival Guide

A community-driven web application helping Yale newcomers navigate life in New Haven. Contributors share posts about housing, food, transportation, academics, and more, while admins moderate content to ensure quality.

**Team:** far-storm (stormy-deer, adorable-crow, super-giraffe)

---

## Project Overview

### Problem Statement

New students and staff arriving at Yale face numerous challenges: finding housing, discovering local restaurants, understanding transportation options, and navigating academic resources. Existing resources are scattered across multiple platforms, making it difficult to find reliable, up-to-date information.

### Solution

The Yale Newcomer Survival Guide provides a centralized, community-driven platform where experienced Yale community members can share knowledge and newcomers can easily discover essential information. The platform uses a contributor-admin workflow to ensure content quality while maintaining community engagement.

### Target Users

- **Newcomers:** Students, staff, and faculty new to Yale who need practical information
- **Contributors:** Community members who want to share knowledge and help others
- **Admins:** Content moderators who review and approve posts to maintain quality

---

## Core Features

### 1. User Authentication & Role Management
- User registration with automatic role assignment (Reader, Contributor, Admin)
- Secure login/logout functionality
- Role-based access control throughout the application

### 2. Content Management System
- **Contributors:** Create, edit, and manage posts with draft → pending → approved workflow
- **Admins:** Review and moderate posts through admin dashboard
- **Public:** Browse approved posts by category

### 3. Category-Based Organization
- Posts organized by categories (Housing, Food, Transport, Academics, etc.)
- Category listing and detail pages
- Easy navigation and discovery

### 4. Post Workflow & Moderation
- Draft posts for contributors to refine before submission
- Pending review queue for admins
- Approve/reject workflow with automatic publication
- Auto-generated unique slugs from post titles

### 5. A/B Testing & Analytics
- A/B test endpoint at `/218b7ae/` for button label experiment
- Server-side event tracking via `ABTestEvent` model
- Google Analytics 4 integration for real-time monitoring
- Management command to analyze results and determine winner

---

## Tech Stack

- **Backend Framework:** Django 4.2.26
- **Database:** PostgreSQL (production) / SQLite (local development)
- **Frontend:** Bootstrap 5 for responsive UI
- **Static Files:** WhiteNoise for production serving
- **Deployment:** Render (staging + production environments)
- **Analytics:** Google Analytics 4 (GA4)
- **Version Control:** GitHub
- **Linting:** Ruff
- **Testing:** Django Test Framework

---

## Local Setup

### Prerequisites

- Python 3.9+
- pip
- virtualenv (or venv)

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone [TBD: repository URL]
   cd yale-newcomer-survival-guide
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create user groups (optional)**
   ```bash
   python manage.py setup_groups
   ```

6. **Seed initial data (optional)**
   ```bash
   python manage.py seed_data
   ```

7. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server**
   ```bash
   python manage.py runserver
   ```

9. **Access the application**
   - Open http://127.0.0.1:8000 in your browser
   - Admin interface: http://127.0.0.1:8000/admin/

---

## Environment Variables

**Important:** Never commit secrets to the repository. All sensitive configuration is loaded from environment variables.

### Required Environment Variables

| Variable | Description | Default (Local) | Production |
|----------|-------------|-----------------|------------|
| `DJANGO_SECRET_KEY` | Django secret key for cryptographic signing | `django-insecure-dev-key-change-in-production` | **Must be set** |
| `DEBUG` | Enable debug mode | `False` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `127.0.0.1,localhost` | **Must be set** |
| `DATABASE_URL` | Database connection URL | `sqlite:///db.sqlite3` | PostgreSQL URL from Render |
| `GA_MEASUREMENT_ID` | Google Analytics 4 measurement ID | `G-9XJWT2P5LE` | Can use default or override |

### Local Development

For local development, create a `.env` file in the project root (this file is gitignored):

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
GA_MEASUREMENT_ID=G-9XJWT2P5LE
```

### Production (Render)

Set environment variables in the Render dashboard:
- Go to your service → Environment
- Add each variable with its production value
- Render automatically provides `DATABASE_URL` for PostgreSQL services
- `RENDER_EXTERNAL_HOSTNAME` is automatically set by Render

---

## Deployment

### Staging vs Production

We maintain two separate environments on Render:

- **Staging:** Used for testing changes before production deployment
  - URL: [TBD: staging URL]
  - Same codebase as production
  - Separate database instance
  - Used for QA and integration testing

- **Production:** Live environment serving real users
  - URL: [TBD: production URL]
  - Stable, tested code only
  - Production database
  - Monitored for performance and errors

### Deploying on Render

#### Option 1: Using render.yaml (Recommended)

The project includes a `render.yaml` file for infrastructure-as-code deployment:

```yaml
services:
  - type: web
    name: yale-newcomer-survival-guide
    env: python
    buildCommand: pip install -r requirements.txt && python manage.py collectstatic --noinput
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: DJANGO_SECRET_KEY
        sync: false
      - key: DATABASE_URL
        fromDatabase:
          name: yale-newcomer-db
          property: connectionString
```

#### Option 2: Manual Configuration

1. **Create a new Web Service** on Render
2. **Connect your GitHub repository**
3. **Configure build settings:**
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - **Start Command:** `gunicorn config.wsgi:application`
4. **Add PostgreSQL database:**
   - Create a new PostgreSQL database
   - Render automatically provides `DATABASE_URL`
5. **Set environment variables:**
   - `DJANGO_SECRET_KEY`: Generate a secure secret key
   - `DEBUG`: `False`
   - `DJANGO_ALLOWED_HOSTS`: Your Render service URL
   - `GA_MEASUREMENT_ID`: Your GA4 measurement ID (optional)
6. **Deploy**

### Post-Deployment

After deployment, run migrations if needed:

```bash
# In Render Shell or via SSH
python manage.py migrate
python manage.py setup_groups
```

---

## A/B Test Endpoint

### Endpoint Details

The A/B test endpoint is located at `/218b7ae/`, derived from the first 7 characters of SHA1("far-storm"):

```python
import hashlib
hashlib.sha1("far-storm".encode()).hexdigest()[:7]  # Returns: "218b7ae"
```

**Endpoint URL:** [TBD: production URL]/218b7ae/

### Features

- **Publicly Accessible:** No authentication required
- **Team Information:** Displays team nickname "far-storm" and all team members
- **A/B Test Button:** Button with `id="abtest"` showing either "kudos" or "thanks"
- **Variant Assignment:** 50/50 random split, persisted via session cookie
- **Analytics Tracking:**
  - Server-side: `ABTestEvent` model records exposure and conversion events
  - Client-side: GA4 events `ab_exposure` and `ab_button_click`

### Computing the Winner

To analyze A/B test results and determine the winning variant:

```bash
python manage.py abtest_report
```

This command:
- Queries `ABTestEvent` for experiment "button_label_kudos_vs_thanks"
- Calculates exposures and conversions per variant
- Computes conversion rates
- Identifies the winner based on higher conversion rate
- Provides statistical warnings if sample size is insufficient

**Example Output:**
```
=== A/B Test Summary Report ===
Variant          Exposures       Conversions      Conversion Rate
kudos            50              10               20.00%
thanks           60              18               30.00%

Winner: "thanks" (conversion rate: 30.00% vs 20.00%)
```

### Analytics Integration

- **Server-Side:** `ABTestEvent` model provides reliable, queryable data
- **Client-Side:** GA4 Realtime dashboard for immediate monitoring
- **Bot Filtering:** Server-side logic filters out non-human traffic
- **Deduplication:** Session-based deduplication prevents double-counting

---

## Testing & Linting

### Running Tests

Run the full test suite:

```bash
python manage.py test
```

Run tests for a specific app:

```bash
python manage.py test core
```

Run a specific test:

```bash
python manage.py test core.tests.test_abtest
```

**Test Coverage:**
- Total tests: 111+
- Coverage: >75% overall, 100% on critical models
- All tests passing ✅

### Linting

Check code quality with Ruff:

```bash
ruff check .
```

Fix auto-fixable issues:

```bash
ruff check . --fix
```

**Configuration:** `pyproject.toml`

**Status:** All files pass linting checks ✅

---

## Team Members & Contributions

### stormy-deer (Chun-Hung Yeh)
- **Primary Contributions:**
  - Project architecture and Django setup
  - A/B testing implementation and analytics integration
  - Production deployment and infrastructure configuration
  - Server-side event tracking (`ABTestEvent` model)
  - Management commands (`abtest_report`)
  - 12-factor app compliance and environment variable management
  - Comprehensive test suite and coverage tooling

### adorable-crow (Celine Li)
- **Primary Contributions:**
  - User authentication system and role management
  - Contributor dashboard and post management workflows
  - Public-facing UI design and Bootstrap integration
  - Template architecture and frontend development
  - User experience testing and validation
  - A/B test endpoint testing and analytics verification

### super-giraffe (Denise Wu)
- **Primary Contributions:**
  - Database models and schema design
  - Category and post management features
  - Admin moderation tools and workflows
  - URL routing and view implementation
  - A/B testing infrastructure planning
  - Production deployment testing and QA

---

## Additional Resources

- **Sprint Documentation:** `/docs/sprints/` (planning, review, retrospective for all 4 sprints)
- **Final Report:** `/docs/final-report.md`
- **Velocity Chart:** `/docs/velocity.png` (generated via `scripts/velocity_chart.py`)
- **A/B Test Analysis:** Run `python manage.py abtest_report`

---

## License

[TBD: Add license information]

---

## Support

For questions or issues, please refer to:
- Sprint documentation in `/docs/sprints/`
- Final project report in `/docs/final-report.md`
- GitHub issues (if repository is public)

---

**Built with ❤️ by Team far-storm (stormy-deer, adorable-crow, super-giraffe)**
