# Sprint 4 Report – far-storm

**Project:** Yale Newcomer Survival Guide  
**Team:** far-storm (Chun-Hung Yeh, Celine (Qijing) Li, Denise Wu)  
**Sprint Duration:** 2 weeks (November 18 – December 2, 2024)

---

## 1. Sprint Goal & Achievement

**Sprint Goal:** Deploy to production, finalize the A/B endpoint and analytics, complete the MVP user journeys, and prepare the codebase and documentation for final submission.

**Achievement:** ✅ **Fully Achieved**

The team successfully delivered all Sprint 4 objectives. The MVP is now live in production with a fully functional A/B test endpoint, integrated Google Analytics tracking, comprehensive test coverage (69% overall, 100% on critical models), and production-ready deployment configuration. All 26 committed story points were completed, and the codebase is ready for final submission.

---

## 2. Production Deployment

### Production URL
**https://yale-newcomer-survival-guide.onrender.com**

### What Works in Production

The following features are fully operational:

- **Authentication:** User signup (auto-assigned Contributor role), login, logout
- **Contributor Functionality:** Create, edit, delete own posts; "My Posts" view; bookmark posts
- **Post Workflow:** Draft → Pending → Admin approval → Public visibility (automatic `published_at` setting)
- **Admin Dashboard:** Review pending posts, approve/reject posts, manage content
- **Public View:** Browse approved posts by category, view post details
- **A/B Test Endpoint:** Publicly accessible at `/218b7ae/` with variant logic

### How Deployment Works

Deployment follows a streamlined process:

- **Code pushed to GitHub** on the `main` branch
- **Render service** connected to repository with auto-deploy enabled
- **Build steps** execute automatically:
  - Install dependencies from `requirements.txt`
  - Run `python manage.py collectstatic --noinput` (WhiteNoise)
  - Run `python manage.py migrate` (database migrations)
- **Application starts** with Gunicorn, binding to `$PORT`
- **Health check** at `/admin/login/` verifies deployment success

### Infrastructure Details

- **Database:** PostgreSQL via `DATABASE_URL` environment variable (configured via `dj-database-url`)
- **Static Files:** WhiteNoise middleware serves compressed static files
- **Configuration:** 12-factor compliant, all secrets via environment variables
- **Migrations:** Run automatically on every deployment

---

## 3. A/B Test Endpoint & Analytics

### Endpoint URL
**https://yale-newcomer-survival-guide.onrender.com/218b7ae/**

### Page Description

The A/B test endpoint is publicly accessible (no login required) and displays:

- Team nickname: **"far-storm"**
- Team members:
  - Chun-Hung Yeh
  - Celine (Qijing) Li
  - Denise Wu
- Button with `id="abtest"` that displays either **"kudos"** or **"thanks"**

The variant is chosen via 50/50 random logic and persisted via a cookie with 30-day expiration, ensuring consistent experience for returning visitors.

### Analytics Implementation

**Google Analytics 4 Configuration:**
- Measurement ID: `G-9XJWT2P5LE` (via `GA_MEASUREMENT_ID` environment variable)
- GA tag injected through `base.html` template via context processor
- Single GA tag (no duplicates), conditionally rendered

**Event Tracking:**
- **`ab_variant_shown`:** Fired on page load with variant information
  - Event parameters: `variant` (kudos/thanks), `page_path`, `event_category`
- **`ab_variant_clicked`:** Fired when button is clicked
  - Event parameters: `variant`, `page_path`, `event_category`

These events will be used to analyze traffic patterns and user preference between "kudos" and "thanks" variants during the final submission period.

---

## 4. Completed Work & Velocity Summary

### Main Sprint 4 Stories Completed

| Story | Description | Points |
|-------|-------------|--------|
| S4-1 | A/B test endpoint at `/218b7ae/` | 5 |
| S4-2 | GA4 integration with event tracking | 3 |
| S4-3 | Production deployment verification | 3 |
| S4-4 | 12-factor configuration compliance | 2 |
| S4-5 | Coverage tooling setup | 3 |
| S4-6 | Linter (Ruff) configuration | 2 |
| S4-7 | README and documentation updates | 2 |
| S4-8 | Auto-generate post slugs | 3 |
| S4-9 | Sprint 4 documentation creation | 3 |

**Total Completed: 26 points**

### Velocity Tracking

- **Sprint 2 Velocity:** 26 points
- **Sprint 3 Velocity:** 44 points
- **Sprint 4 Velocity:** 26 points
- **Cumulative Velocity (Sprints 2-4):** 96 points
- **Average Velocity:** 32 points

**Velocity Analysis:** Sprint 4's velocity of 26 points reflects focused work on production readiness, A/B testing infrastructure, and documentation. While lower than Sprint 3's 44 points (which included extensive feature development), Sprint 4's work was equally valuable in ensuring production stability and code quality. The velocity tracking helped the team plan Sprint 4 realistically, allocating appropriate time for infrastructure and polish work alongside new features.

---

## 5. Readiness for Final Submission

### What Is Complete

✅ **MVP Functionality:** Complete Contributor → Admin → Public user journey working in production  
✅ **A/B Test Endpoint:** Publicly accessible at `/218b7ae/` with variant logic and cookie persistence  
✅ **Analytics Tracking:** GA4 integrated with event tracking for variant analysis  
✅ **Production Deployment:** Live on Render with PostgreSQL, WhiteNoise, environment variables configured  
✅ **Testing:** 61 passing tests covering models, views, workflows, and A/B endpoint  
✅ **Coverage:** 69% overall coverage, 100% on critical models (`core/models.py`, `core/forms.py`)  
✅ **Linting:** Ruff configured and passing, code quality maintained  
✅ **Documentation:** README updated, Sprint 4 planning/review/retrospective/report created  
✅ **Code Quality:** No hardcoded secrets, 12-factor compliant, production-ready

### What Remains (Final 9 Days)

- **GA4 Data Analysis:** Collect and analyze A/B test data (variant distribution, click rates) for final report
- **Final Course Report:** Prepare comprehensive project report documenting all Sprint 2-4 achievements
- **Charts & Visualizations:** Create velocity chart and burndown/burnup charts for Sprints 2-4
- **Minor UX Polish:** Final review of production site for any UI inconsistencies or missing error pages
- **Content Verification:** Ensure all links and navigation work correctly, verify mobile responsiveness

### Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| **Insufficient A/B test traffic** | Deploy early, share link with classmates for traffic generation |
| **GA4 data not available in time** | Use GA Real-Time view for immediate verification, export historical data early |
| **Documentation time constraints** | Sprint 4 docs created proactively; final report can reference existing documentation |
| **Production deployment issues** | Maintain local and staging environments for testing; have rollback plan |

---

## 6. Sprint Retrospective Highlights

### Technical Learning

1. **Production Deployment Best Practices:** Learned the importance of 12-factor configuration, environment variable management, and database connection pooling. The transition from SQLite to PostgreSQL required careful attention to migration strategies and connection health checks.

2. **A/B Testing Implementation:** Gained experience with deterministic routing (SHA1 hashes), cookie-based state persistence, and the critical importance of exact string matching (Unicode vs ASCII).

3. **Analytics Integration:** Understood GA4 event tracking, measurement IDs, and the necessity of immediate verification through browser devtools rather than waiting for delayed reporting.

### Process Learning

1. **Infrastructure Work Deserves Explicit Planning:** Learned that deployment configuration and code quality tooling require dedicated story points and time allocation, not just "background work."

2. **Documentation as You Go:** Found that updating documentation immediately when making changes prevents last-minute rushes and ensures accuracy.

3. **Verification Checklists:** Established that critical configurations (hashes, environment variables, analytics) need explicit verification steps before considering work complete.

### Team Collaboration & AI Tools

The team effectively leveraged AI-assisted development (Cursor + LLM) to accelerate boilerplate code generation, test writing, and documentation creation. However, we learned that AI tools require careful human oversight:
- **Configuration decisions** (DATABASE_URL, environment variables) needed human verification
- **Hash verification** required manual string matching checks
- **Analytics testing** needed actual browser verification, not just AI-generated code

The workflow that emerged: AI generates initial code and documentation, then the team verifies, tests, and refines. This balance between AI acceleration and human judgment was key to Sprint 4's success.

---

## 7. Links

### Documentation
- Sprint 4 Planning: `/docs/sprints/sprint-4-planning.md`
- Sprint 4 Review: `/docs/sprints/sprint-4-review.md`
- Sprint 4 Retrospective: `/docs/sprints/sprint-4-retrospective.md`
- Sprint 4 Report: `/docs/sprints/sprint-4-report.md` (this document)

### Project Resources
- **GitHub Project Board:** https://github.com/users/she24731/projects/6
- **Production URL:** https://yale-newcomer-survival-guide.onrender.com
- **A/B Test Endpoint:** https://yale-newcomer-survival-guide.onrender.com/218b7ae/

### Staging Environment

For local development/staging, run:
```bash
python manage.py runserver
```

Configure `.env` file with:
- `DJANGO_SECRET_KEY` (development key)
- `DATABASE_URL` (SQLite default: `sqlite:///db.sqlite3`)
- `GA_MEASUREMENT_ID` (optional, defaults to `G-9XJWT2P5LE`)

See `README.md` for complete local setup instructions.

---

**Sprint 4 successfully delivered all objectives. The MVP is production-ready, fully tested, and documented for final submission.**

---

*Report prepared by: far-storm team (Chun-Hung Yeh, Celine (Qijing) Li, Denise Wu)*  
*Date: December 2, 2024*

