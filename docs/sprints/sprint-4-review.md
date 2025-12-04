# Sprint 4 Review – far-storm

**Project:** Yale Newcomer Survival Guide  
**Sprint Duration:** 2 weeks  
**Dates:** November 18, 2024 – December 2, 2024  
**Team Members:** Chun-Hung Yeh, Celine (Qijing) Li, Denise Wu

---

## 🎯 Sprint Goal

Deploy to production, finalize the A/B endpoint and analytics, complete the MVP user journeys, and prepare the codebase and documentation for final submission.

**Goal Achievement:** ✅ **YES** – Fully achieved

The team successfully implemented the A/B test endpoint, integrated Google Analytics, verified production deployment with PostgreSQL, configured coverage and linting tooling, and completed all documentation. The MVP is production-ready with comprehensive testing, code quality checks, and analytics tracking in place.

---

## ✅ Completed User Stories

### A/B Testing & Analytics

- **S4-1**: Implement A/B test endpoint at `/218b7ae/` (5 pts) ✅  
  - **Completed:** Endpoint created at `/218b7ae/` (first 7 chars of SHA1("far-storm")), publicly accessible, displays team nickname "far-storm" and all three team members. Button with `id="abtest"` shows "kudos" or "thanks" based on 50/50 random logic, persisted via cookie (30-day expiration).  
  - **Key commits:** "Implement A/B endpoint and analytics for /218b7ae/"

- **S4-2**: Wire Google Analytics (GA4) with events for A/B page (3 pts) ✅  
  - **Completed:** GA4 (G-9XJWT2P5LE) integrated via context processor, single GA tag in base.html (no duplicates). Events `ab_variant_shown` (page load) and `ab_variant_clicked` (button click) implemented with variant information for later analysis.  
  - **Key commits:** "Add Google Analytics tracking (G-9XJWT2P5LE)", updates to context processor

### Production Deployment & Infrastructure

- **S4-3**: Ensure production deployment on Render using PostgreSQL via `DATABASE_URL` (3 pts) ✅  
  - **Completed:** PostgreSQL configured via `dj_database_url.config()` with SQLite fallback for local dev. ALLOWED_HOSTS includes Render URL and localhost, automatically adds RENDER_EXTERNAL_HOSTNAME. WhiteNoise configured for static files. Production URL: https://yale-newcomer-survival-guide.onrender.com  
  - **Key commits:** "Use Render Postgres via DATABASE_URL (dj-database-url)"

- **S4-4**: Ensure 12-factor configuration compliance (2 pts) ✅  
  - **Completed:** All secrets read from environment variables (SECRET_KEY, DATABASE_URL, DEBUG, ALLOWED_HOSTS, GA_MEASUREMENT_ID). No hardcoded secrets. Configuration follows 12-factor principles.  
  - **Key commits:** Settings refactoring throughout Sprint 4

### Code Quality & Testing

- **S4-5**: Ensure tests are passing and add coverage tooling (3 pts) ✅  
  - **Completed:** All 61 tests passing. Coverage configured in pyproject.toml, overall coverage 69%, critical modules all above 50% (models: 100%, views: 68%, settings: 95%). Coverage report generated and documented.  
  - **Key commits:** "Add coverage configuration and GA README clarification for Sprint 4"

- **S4-6**: Ensure linter (ruff) is configured and passes (2 pts) ✅  
  - **Completed:** Ruff configured in pyproject.toml, all checks passing. Code quality maintained with E (errors) and F (pyflakes) rules enabled.  
  - **Key commits:** Ruff configuration added in Sprint 3, verified in Sprint 4

### Documentation & Polish

- **S4-7**: Update README and documentation for deployment and analytics (2 pts) ✅  
  - **Completed:** README.md updated with accurate GA configuration description (uses GA_MEASUREMENT_ID env var, not hardcoded). Deployment section comprehensive with staging vs production explanation.  
  - **Key commits:** "Add coverage configuration and GA README clarification for Sprint 4"

- **S4-8**: Auto-generate unique post slugs from title (3 pts) ✅  
  - **Completed:** Slug field removed from contributor forms, auto-generation implemented in Post model with uniqueness checks. Contributors no longer need to manually enter slugs.  
  - **Key commits:** "Auto-generate unique post slugs from title"

- **S4-9**: Create Sprint 4 documentation (3 pts) ✅  
  - **Completed:** Sprint 4 planning, review, retrospective, and report documents created following format of previous sprints.  
  - **Key commits:** "Add Sprint 4 planning, review, retrospective, and report"

**Total Completed:** **26 points**

---

## ❌ Incomplete User Stories

None – all Sprint 4 user stories completed successfully.

---

## 🎬 Demo Summary

The following features are now **working in production** at https://yale-newcomer-survival-guide.onrender.com:

### Authentication
- ✅ User signup → automatically assigned Contributor role
- ✅ Login/logout functionality
- ✅ Role-based access control (Reader, Contributor, Admin)

### Contributor Flow
- ✅ Signup → auto-assigned Contributor → create post → see "My Posts" → bookmark posts
- ✅ Create, edit, delete own posts
- ✅ Post workflow: Draft → Pending → Admin approval → Public visibility
- ✅ Auto-generated slugs (no manual input required)

### Admin Capabilities
- ✅ Admin dashboard at `/dashboard/`
- ✅ Approve/reject posts
- ✅ View pending posts queue
- ✅ Posts automatically get `published_at` when approved

### Public User Experience
- ✅ See only approved posts on homepage
- ✅ Browse posts by category
- ✅ View post detail pages

### A/B Test Endpoint
- ✅ **URL:** https://yale-newcomer-survival-guide.onrender.com/218b7ae/
- ✅ Publicly accessible (no login required)
- ✅ Displays team nickname "far-storm"
- ✅ Lists all three team members:
  - Chun-Hung Yeh
  - Celine (Qijing) Li
  - Denise Wu
- ✅ Button with `id="abtest"` shows either "kudos" or "thanks"
- ✅ 50/50 variant distribution via random logic
- ✅ Variant persisted via cookie (30-day expiration)

### Analytics (GA4)
- ✅ GA4 measurement ID: G-9XJWT2P5LE (via GA_MEASUREMENT_ID env var)
- ✅ GA tag injected through `base.html` + context processor
- ✅ Events tracked:
  - `ab_variant_shown`: Fired on A/B page load with variant info
  - `ab_variant_clicked`: Fired when button is clicked
- ✅ Events include variant parameter for comparison analysis

---

## 📊 Metrics

### Velocity Tracking

- **Sprint 2 Velocity:** 26 points
- **Sprint 3 Velocity:** 44 points  
- **Sprint 4 Velocity:** 26 points
- **Cumulative Velocity (Sprints 2-4):** 96 points
- **Average Velocity:** 32 points

**Note on Sprint 4 velocity:** While Sprint 4 completed 26 points, this represents focused work on production readiness, A/B testing, analytics, and documentation. The lower point count compared to Sprint 3 reflects more polish and verification work rather than new feature development.

---

## 🚀 Production Deployment Status

### Environments

- **Staging (Render):** https://yale-newcomer-survival-guide-staging.onrender.com/
- **Production (Render):** https://yale-newcomer-survival-guide.onrender.com/

### Production Environment
- **URL:** https://yale-newcomer-survival-guide.onrender.com
- **Platform:** Render Web Service
- **Database:** PostgreSQL via `DATABASE_URL` environment variable (not SQLite)
- **Static Files:** Served via WhiteNoise
- **DEBUG:** `False` in production

### Staging Environment Verification

- **Staging URL:** https://yale-newcomer-survival-guide-staging.onrender.com/
- **Verified flows on staging:**
  - User signup, login, logout
  - Contributor creates a post → pending → admin approves → visible publicly
  - Bookmarking flow
  - A/B test endpoint at `/218b7ae/` (variants "kudos"/"thanks")
- Staging uses the same Postgres schema as production (via DATABASE_URL), but with separate database instance or config.

### Configuration Verified
- ✅ PostgreSQL connection via `dj_database_url.config()`
- ✅ `ALLOWED_HOSTS` includes:
  - `127.0.0.1`
  - `localhost`
  - `yale-newcomer-survival-guide.onrender.com`
  - `yale-newcomer-survival-guide-staging.onrender.com`
  - Auto-adds `RENDER_EXTERNAL_HOSTNAME` if provided
- ✅ Environment variables configured:
  - `DJANGO_SECRET_KEY`
  - `DATABASE_URL` (auto-provided by Render PostgreSQL)
  - `GA_MEASUREMENT_ID` (default: G-9XJWT2P5LE)
  - `DEBUG` (set to False)
- ✅ Migrations auto-run on deployment

### Deployment Process
1. Code pushed to GitHub `main` branch
2. Render auto-detects changes (auto-deploy enabled)
3. Build steps execute:
   - Install dependencies from `requirements.txt`
   - Run `python manage.py collectstatic --noinput`
   - Run `python manage.py migrate`
4. Application starts with Gunicorn
5. Health check at `/admin/login/`

---

## 📈 Code Quality Metrics

### Testing
- **Total Tests:** 61
- **Status:** All passing ✅
- **Test Breakdown:**
  - Unit tests: 36 (Post, Category, Bookmark, ExternalLink models)
  - Integration tests: 15 (signup, login, CRUD, workflows)
  - A/B test tests: 6 (endpoint, variants, cookies, analytics)

### Coverage
- **Overall Coverage:** 69%
- **Critical Modules:**
  - `core/models.py`: 100%
  - `core/forms.py`: 100%
  - `core/context_processors.py`: 100%
  - `config/settings.py`: 95%
  - `core/admin.py`: 93%
  - `config/urls.py`: 88%
  - `core/views.py`: 68%
- **Coverage Config:** `pyproject.toml`

### Linting
- **Tool:** Ruff
- **Status:** All checks passing ✅
- **Config:** `pyproject.toml`
- **Rules:** E (errors), F (pyflakes)

---

## ✅ Readiness for Final Submission

### What's Complete
- ✅ **MVP Functionality:** Complete Contributor → Admin → Public user journey
- ✅ **A/B Test Endpoint:** Publicly accessible at `/218b7ae/` with variant logic
- ✅ **Analytics:** GA4 integrated with event tracking for A/B analysis
- ✅ **Production Deployment:** Live on Render with PostgreSQL
- ✅ **Tests:** 61 passing tests covering all critical paths
- ✅ **Coverage:** 69% overall, all critical modules above 50%
- ✅ **Linting:** Ruff configured and passing
- ✅ **Documentation:** README updated, Sprint 4 docs created
- ✅ **Code Quality:** No hardcoded secrets, 12-factor compliant

### What Remains (Final 9 Days)
- **Traffic / A/B Results Analysis:**
  - Collect GA4 data on variant distribution
  - Analyze button click rates by variant
  - Prepare findings for final report

- **Final Course Report:**
  - Complete comprehensive project report
  - Include velocity charts (burndown/burnup)
  - Document all Sprint 2-4 achievements

- **Charts & Visualizations:**
  - Create velocity chart (Sprints 2-4)
  - Generate burndown/burnup charts if applicable

- **Minor UX and Content Polish:**
  - Review production site for any UI inconsistencies
  - Verify all links and navigation work correctly
  - Check mobile responsiveness

- **Non-Critical Enhancements:**
  - Add any missing error pages
  - Improve contributor dashboard UI (if time permits)

---

## 🔗 Links

- **Production URL:** https://yale-newcomer-survival-guide.onrender.com
- **A/B Test Endpoint:** https://yale-newcomer-survival-guide.onrender.com/218b7ae/
- **GitHub Repository:** https://github.com/she24731/far-storm-project
- **GitHub Project Board:** https://github.com/users/she24731/projects/6
- **Sprint 4 Planning:** `/docs/sprints/sprint-4-planning.md`
- **Sprint 4 Retrospective:** `/docs/sprints/sprint-4-retrospective.md`
- **Sprint 4 Report:** `/docs/sprints/sprint-4-report.md`

---

**Sprint 4 successfully completed all goals. The MVP is production-ready with A/B testing, analytics, comprehensive testing, and full documentation.**

