# Yale Newcomer Survival Guide

A community-driven web application developed as part of MGT656 - Management of Software Development, designed to help Yale newcomers navigate life in New Haven through curated content and community knowledge sharing.

**Team:** far-storm  
**Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)

---

## Problem Statement

New students and staff arriving at Yale face numerous challenges when transitioning to life in New Haven: finding suitable housing, discovering local restaurants and dining options, understanding public transportation systems, navigating academic resources, and identifying essential services. Existing information sources are scattered across multiple platforms (Facebook groups, university websites, word-of-mouth), making it difficult for newcomers to find reliable, up-to-date, and contextually relevant information in one place.

## MVP Scope

This minimum viable product (MVP) delivers a functional web application that enables:

1. **Community Content Creation:** Contributors can create and submit categorized posts about life in New Haven
2. **Content Moderation:** Admin users can review and approve submitted content to ensure quality
3. **Public Content Discovery:** Users can browse approved posts organized by categories
4. **User Authentication:** Secure registration and login with role-based access control
5. **A/B Testing Infrastructure:** Analytics endpoint for experimentation and data-driven decision making

The MVP focuses on core functionality required for community knowledge sharing while maintaining content quality through moderation workflows.

---

## Core Features

### 1. User Authentication & Role Management

Django's built-in authentication system extended with role-based access control using user groups. Three roles are supported:

- **Reader:** Default role assigned to new users upon registration; can browse approved content
- **Contributor:** Can create, edit, and manage posts through a submission interface
- **Admin:** Staff users who can moderate posts through an admin dashboard

Authentication uses Django's session-based authentication. New users are automatically assigned to the Reader group upon registration. Role-based permissions control access to contributor submission pages and admin moderation dashboards.

### 2. Content Management & Post Workflow

A three-stage moderation workflow ensures content quality:

- **Draft:** Contributors create and refine posts before submission
- **Pending Review:** Submitted posts await admin approval
- **Approved/Rejected:** Admin decisions determine post visibility

Contributors can create posts with titles, content, and category assignments. Posts support auto-generated unique slugs from titles. Approved posts automatically receive `published_at` timestamps and become publicly visible. The system includes draft functionality for iterative refinement before submission.

### 3. Category-Based Organization

Posts are organized into categories (Housing, Food, Transport, Academics, etc.) for intuitive navigation. Each category has:

- Dedicated listing pages with pagination support
- Category detail pages showing all posts in that category
- Search functionality to find posts across categories

Category organization reduces information overload and improves discoverability for newcomers seeking specific types of information.

### 4. Admin Moderation Dashboard

Admin users access a dedicated dashboard for reviewing pending posts. The moderation workflow includes:

- Queue view of all pending posts awaiting review
- Approve/reject actions with automatic status updates
- Automatic publication of approved posts with timestamp recording
- Contributor feedback on submission status

### 5. A/B Testing & Analytics Infrastructure

A publicly accessible A/B test endpoint at `/218b7ae/` (derived from first 7 characters of SHA1("far-storm")) enables experimentation with button label variants. The endpoint implements:

- Variant assignment (50/50 split between "kudos" and "thanks") persisted via session cookies
- Server-side event tracking via `ABTestEvent` database model
- Client-side Google Analytics 4 (GA4) integration for real-time monitoring
- Session-based deduplication to prevent double-counting exposures
- Bot traffic filtering to ensure data quality

The infrastructure supports data-driven decision making through conversion rate analysis.

---

## Technology Stack

### Backend
- **Framework:** Django 4.2.26
- **Database:** PostgreSQL (production) / SQLite (local development)
- **Authentication:** Django's built-in session-based authentication with user groups
- **ORM:** Django ORM for database operations

### Frontend
- **UI Framework:** Bootstrap 5 for responsive design
- **Templating:** Django templates with template inheritance
- **JavaScript:** Minimal client-side scripting for A/B test interactions and GA4 event tracking

### Infrastructure & Deployment
- **Hosting:** Render (staging and production environments)
- **Static Files:** WhiteNoise middleware for efficient static file serving
- **Process Management:** Gunicorn WSGI server
- **Configuration:** Infrastructure-as-code via `render.yaml`

### Analytics & Monitoring
- **Client-Side:** Google Analytics 4 (GA4) with measurement ID `G-9XJWT2P5LE`
- **Server-Side:** Django `ABTestEvent` model for reliable event tracking

### Development Tools
- **Version Control:** Git with GitHub
- **Linting:** Ruff (configured in `pyproject.toml`)
- **Testing:** Django Test Framework with 111+ test cases

---

## Authentication Approach

The application uses Django's built-in authentication system with the following implementation:

**User Registration:**
- Custom registration form extends Django's `UserCreationForm`
- New users are automatically assigned to the "Reader" group upon registration
- Users are automatically logged in after successful registration

**Login/Logout:**
- Custom login view extends Django's `LoginView` with role-based redirects
- Session-based authentication stores user session data
- Logout uses Django's `LogoutView` with success messages

**Role-Based Access Control:**
- Three user groups: "Readers", "Contributors", "Admins"
- Permissions enforced via decorators: `@login_required` and `@user_passes_test`
- Contributor submission pages require `is_contributor()` check
- Admin dashboard requires `is_staff` flag or `is_admin()` check
- Public content (approved posts) accessible without authentication

**Session Management:**
- Django sessions stored in database (configured via `SESSION_ENGINE`)
- Session cookies used for authentication persistence
- Session data used for A/B test variant assignment and deduplication

---

## Database Models Overview

The application uses the following primary models:

### Category
- **Purpose:** Organize posts by topic (Housing, Food, Transport, Academics, etc.)
- **Key Fields:** `name` (unique), `slug` (unique, indexed), `description`, `created_at`
- **Relationships:** One-to-many with Post model

### Post
- **Purpose:** Store user-generated content with moderation workflow
- **Key Fields:** 
  - Content: `title`, `slug` (unique, auto-generated), `content`, `category` (ForeignKey)
  - Metadata: `author` (ForeignKey to User), `status` (draft/pending/approved/rejected)
  - Timestamps: `created_at`, `updated_at`, `published_at` (auto-set on approval)
- **Indexes:** `status`, `category_id`, `updated_at` for query performance
- **Workflow:** Status transitions from draft → pending → approved/rejected

### Bookmark
- **Purpose:** Allow users to save posts for later reference
- **Key Fields:** `user` (ForeignKey), `post` (ForeignKey), `created_at`
- **Constraints:** Unique together on `(user, post)` to prevent duplicates

### ExternalLink
- **Purpose:** Store curated external resources related to categories
- **Key Fields:** `title`, `url`, `category` (ForeignKey, optional), `created_at`, `updated_at`

### ABTestEvent
- **Purpose:** Server-side tracking of A/B test exposures and conversions
- **Key Fields:**
  - Experiment: `experiment_name`, `variant`, `event_type` (exposure/conversion)
  - Metadata: `endpoint`, `session_id`, `ip_address`, `user_agent`
  - User: `user` (ForeignKey, optional for anonymous users), `created_at`
- **Indexes:** Composite indexes on `(experiment_name, variant, event_type)` and `(experiment_name, created_at)` for efficient querying

All models use Django migrations for schema management, ensuring version-controlled and reproducible database changes across environments.

---

## Deployment Environments

### Staging Environment
- **Purpose:** Testing changes before production deployment
- **URL:** [TBD: staging URL on Render]
- **Configuration:** Same codebase as production, separate database instance
- **Usage:** QA testing, integration verification, safe experimentation with new features

### Production Environment
- **Purpose:** Live application serving end users
- **URL:** [TBD: production URL on Render]
- **Configuration:** Stable, tested code only, production PostgreSQL database
- **Monitoring:** Application logs via Render's logging infrastructure, error tracking

Environment separation enables safe testing of database migrations, configuration changes, and new features without impacting production users.

### Render Deployment

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Configuration managed via `render.yaml` for infrastructure-as-code deployment. Render automatically provides:
- PostgreSQL database with `DATABASE_URL` environment variable
- `RENDER_EXTERNAL_HOSTNAME` for service URL
- Port binding via `$PORT` environment variable

---

## CI/CD Pipeline

### Continuous Integration (GitHub Actions)

Automated CI pipeline implemented via `.github/workflows/ci.yml` that runs on:
- Push events to `main` branch
- Pull request events targeting `main` branch

**Pipeline Steps:**
1. **Checkout:** Retrieve code from GitHub repository
2. **Python Setup:** Configure Python 3.9 environment
3. **Dependencies:** Install all packages from `requirements.txt` with pinned versions
4. **Linting:** Run `ruff check .` to enforce code quality standards
5. **Testing:** Execute `python manage.py test` using SQLite database

**CI Configuration:**
- Uses test-safe environment variables (`DEBUG=1`, dummy `SECRET_KEY`)
- SQLite database for fast, reliable test execution without external dependencies
- Prevents broken code from being merged to main branch
- Catches linting errors and test failures before code integration

### Continuous Deployment (Render)

Render automatically deploys from GitHub on commits to `main` branch:
- Build process installs dependencies and runs database migrations
- Start command launches Gunicorn WSGI server
- Health checks ensure service availability
- Environment variables configured via Render dashboard

This CI/CD approach maintains code quality and enables rapid, reliable deployments.

---

## 12-Factor App Compliance

The application explicitly follows all 12-factor app methodology principles:

1. **Codebase:** Single Git repository deployed to multiple environments without divergence
2. **Dependencies:** Explicitly declared in `requirements.txt` with pinned versions
3. **Config:** All configuration via environment variables (no hardcoded secrets)
4. **Backing Services:** Database treated as attached resource via `DATABASE_URL`
5. **Build/Release/Run:** Strict separation via Render's build and start commands
6. **Processes:** Stateless application processes with no shared filesystem state
7. **Port Binding:** Application binds to port provided by `$PORT` environment variable
8. **Concurrency:** Stateless process model supports horizontal scaling
9. **Disposability:** Fast startup and graceful shutdown
10. **Dev/Prod Parity:** Same codebase, different configuration via environment variables
11. **Logs:** All logging configured to write to stdout (captured by Render)
12. **Admin Processes:** Management commands run as one-off processes

**Implementation:**
- `config/settings.py` loads all configuration from environment variables
- `.gitignore` excludes `.env` files
- No secrets committed to repository
- Logging configuration uses `StreamHandler` for stdout output
- Environment variables: `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `DJANGO_ALLOWED_HOSTS`, `GA_MEASUREMENT_ID`

This approach ensures portability, scalability, and maintainability across deployment environments.

---

## Testing Strategy

### Test Coverage

The codebase includes comprehensive automated tests using Django's test framework:

- **Total Tests:** 111+ tests across multiple test files
- **Coverage:** >75% overall, 100% on critical models
- **Test Files:**
  - `test_abtest.py`: A/B test endpoint and variant assignment
  - `test_abtest_session_dedupe.py`: Session-based deduplication logic
  - `test_abtest_report_command.py`: Management command functionality
  - `test_url_routing.py`: URL resolution and routing correctness
  - `test_post_model.py`: Post model functionality and workflow
  - `test_category_model.py`: Category model functionality
  - `test_bookmark_model.py`: Bookmark functionality
  - `test_integration.py`: End-to-end user workflows
  - Additional tests for forms, admin, and views

### Test Execution

**Local Testing:**
```bash
python manage.py test
```

**CI Testing:**
- Automated test execution via GitHub Actions on every push and pull request
- SQLite database for fast, reliable test execution
- All tests must pass before code can be merged

### Linting

Ruff is used for code linting, configured in `pyproject.toml`:
- Rules: E (errors), F (pyflakes)
- Catches unused imports, undefined names, and code quality issues
- Auto-fixable issues addressed via `ruff check . --fix`
- All files pass linting checks

---

## A/B Test Endpoint & Analytics

### Endpoint Specification

The A/B test endpoint is located at `/218b7ae/`, derived from the first 7 characters of SHA1("far-storm"):

```python
import hashlib
hashlib.sha1("far-storm".encode()).hexdigest()[:7]  # Returns: "218b7ae"
```

**Endpoint URL:** [TBD: production URL]/218b7ae/

### A/B Test Logic

**Variant Assignment:**
- 50/50 random split between "kudos" and "thanks" variants
- Assignment persisted via Django session cookie (`abexp:button_label_kudos_vs_thanks:variant`)
- Consistent variant per session (users see same variant across page reloads)

**Event Tracking:**

1. **Exposure Events:**
   - Logged when user first visits `/218b7ae/` in a session
   - Only counted for real browser navigation (filters bots via User-Agent and headers)
   - Session-based deduplication prevents double-counting from page reloads
   - Server-side: `ABTestEvent` record with `event_type="exposure"`
   - Client-side: GA4 `ab_exposure` event fired once per session

2. **Conversion Events:**
   - Logged when user clicks button with `id="abtest"`
   - Multiple conversions allowed per session (users can click multiple times)
   - Server-side: `ABTestEvent` record with `event_type="conversion"`
   - Client-side: GA4 `ab_button_click` event fired on each click

**Bot Filtering:**
- User-Agent filtering (requires "Mozilla", excludes known bot patterns)
- Request method filtering (only GET requests for exposure)
- Navigation header detection (`Sec-Fetch-Mode: navigate` or `Accept: text/html`)
- Fallback logic for older browsers and test environments

**Deduplication Strategy:**
- Session flag check before logging exposure (`abexp:button_label_kudos_vs_thanks:exposed:/218b7ae/`)
- Database uniqueness constraint on `(experiment_name, event_type="exposure", endpoint, session_id)`
- Atomic `get_or_create()` prevents race conditions

### Analytics Analysis

To compute A/B test results and determine the winning variant:

```bash
python manage.py abtest_report
```

This management command:
- Queries `ABTestEvent` records for experiment "button_label_kudos_vs_thanks" and endpoint "/218b7ae/"
- Calculates exposures and conversions per variant ("kudos" vs "thanks")
- Computes conversion rates: (conversions / exposures) × 100%
- Identifies winner based on higher conversion rate
- Provides warnings if sample size < 30 (insufficient for statistical significance)

**Dual-Tracking Architecture:**
- **Server-Side (`ABTestEvent`):** Primary source of truth, bot-filtered, reliable
- **Client-Side (GA4):** Real-time monitoring, visual dashboards, immediate validation

---

## Environment Variables

All configuration follows 12-factor app principles using environment variables. **Never commit secrets to the repository.**

### Required Variables

| Variable | Description | Default (Local) | Production |
|----------|-------------|-----------------|------------|
| `DJANGO_SECRET_KEY` | Cryptographic signing key | `django-insecure-dev-key-change-in-production` | **Must be set** |
| `DEBUG` | Enable debug mode | `False` | `False` |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `127.0.0.1,localhost` (if DEBUG) | **Must be set** |
| `DATABASE_URL` | Database connection string | `sqlite:///db.sqlite3` | PostgreSQL URL from Render |
| `GA_MEASUREMENT_ID` | Google Analytics 4 measurement ID | `G-9XJWT2P5LE` | Can use default or override |

### Local Development

Create a `.env` file in the project root (gitignored):

```bash
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
DATABASE_URL=sqlite:///db.sqlite3
GA_MEASUREMENT_ID=G-9XJWT2P5LE
```

### Production (Render)

Set environment variables in Render dashboard:
- Go to service → Environment
- Add each variable with production value
- Render automatically provides `DATABASE_URL` for PostgreSQL
- `RENDER_EXTERNAL_HOSTNAME` automatically set by Render

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

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Application: http://127.0.0.1:8000
   - Admin interface: http://127.0.0.1:8000/admin/
   - A/B test endpoint: http://127.0.0.1:8000/218b7ae/

---

## Team Members & Contributions

### stormy-deer (Chun-Hung Yeh)

**Primary Contributions:**
- Project architecture and Django setup
- A/B testing implementation (`/218b7ae/` endpoint, `ABTestEvent` model, variant assignment logic)
- Analytics integration (GA4 context processor, event tracking)
- Production deployment and infrastructure configuration (Render, PostgreSQL, environment variables)
- Server-side event tracking and deduplication logic
- Management commands (`abtest_report`, infrastructure commands)
- 12-factor app compliance and environment variable management
- Comprehensive test suite and coverage tooling
- CI/CD workflow configuration (GitHub Actions)

### adorable-crow (Celine Li)

**Primary Contributions:**
- User authentication system and role management
- Contributor dashboard and post management workflows
- Public-facing UI design and Bootstrap integration
- Template architecture and frontend development
- User experience testing and validation
- A/B test endpoint testing and analytics verification
- Code reviews and quality assurance

### super-giraffe (Denise Wu)

**Primary Contributions:**
- Database models and schema design (Category, Post, Bookmark, `ABTestEvent`)
- Admin moderation tools and workflows
- Category and post management features
- URL routing and view implementation
- A/B testing infrastructure planning and design
- Production deployment testing and QA
- Sprint documentation and process improvement

### Shared Responsibility

Per course policy, all team members share equal responsibility for project outcomes and grading. While individual contributions are listed above, the project represents a collaborative effort with code reviews, pair programming, and shared decision-making throughout all four sprints.

---

## Additional Resources

- **Sprint Documentation:** `/docs/sprints/` (planning, review, retrospective for all 4 sprints)
- **Final Report:** `/docs/final-report.md` (comprehensive project documentation)
- **Velocity Chart:** `/docs/velocity.png` (generated via `scripts/velocity_chart.py`)
- **A/B Test Analysis:** Run `python manage.py abtest_report`

---

**Built by Team far-storm (stormy-deer, adorable-crow, super-giraffe) for MGT656 - Management of Software Development**
