# Sprint 4 Planning – far-storm

**Project:** Yale Newcomer Survival Guide  
**Sprint Duration:** 2 weeks  
**Dates:** November 18, 2024 – December 2, 2024  
**Team Members:** Chun-Hung Yeh, Celine (Qijing) Li, Denise Wu

---

## 🎯 Sprint Goal

Deploy to production, finalize the A/B endpoint and analytics, complete the MVP user journeys, and prepare the codebase and documentation for final submission.

---

## 📌 User Stories Selected for Sprint 4

### A/B Testing & Analytics

- **S4-1**: Implement A/B test endpoint at `/218b7ae/` (publicly accessible)  
  - **Description:** Create endpoint at first 7 characters of SHA1("far-storm"), display team nickname and members, show button with id="abtest" that toggles between "kudos" and "thanks" using 50/50 random logic persisted via cookie.  
  - **Story Points:** 5  
  - **Owner:** Chun-Hung Yeh

- **S4-2**: Wire Google Analytics (GA4) with events for A/B page  
  - **Description:** Integrate GA4 (G-9XJWT2P5LE) via context processor, add `ab_variant_shown` event on page load and `ab_variant_clicked` event on button click. Ensure single GA tag in base.html, no duplicates.  
  - **Story Points:** 3  
  - **Owner:** Chun-Hung Yeh

### Production Deployment & Infrastructure

- **S4-3**: Ensure production deployment on Render using PostgreSQL via `DATABASE_URL`  
  - **Description:** Verify PostgreSQL configuration via `dj_database_url`, confirm `ALLOWED_HOSTS` includes Render URL and localhost, ensure WhiteNoise serves static files, verify no hardcoded secrets.  
  - **Story Points:** 3  
  - **Owner:** Chun-Hung Yeh

- **S4-4**: Ensure 12-factor configuration compliance  
  - **Description:** Audit settings.py for environment variable usage (SECRET_KEY, DATABASE_URL, DEBUG, ALLOWED_HOSTS, GA_MEASUREMENT_ID). Document environment variable requirements.  
  - **Story Points:** 2  
  - **Owner:** Chun-Hung Yeh

### Code Quality & Testing

- **S4-5**: Ensure tests are passing and add coverage tooling  
  - **Description:** Run full test suite, configure coverage.py with pyproject.toml, verify >50% coverage on critical paths (models, views, core flows), generate coverage report.  
  - **Story Points:** 3  
  - **Owner:** Chun-Hung Yeh

- **S4-6**: Ensure linter (ruff) is configured and passes  
  - **Description:** Configure ruff in pyproject.toml, run linting checks, fix meaningful issues (unused imports, undefined names), ensure clean ruff run with no errors.  
  - **Story Points:** 2  
  - **Owner:** Chun-Hung Yeh

### Documentation & Polish

- **S4-7**: Update README and documentation for deployment and analytics  
  - **Description:** Update README.md with accurate GA configuration description, document deployment procedure, clarify staging vs production environments, fix any inaccurate statements.  
  - **Story Points:** 2  
  - **Owner:** Chun-Hung Yeh

- **S4-8**: Auto-generate unique post slugs from title  
  - **Description:** Remove manual slug input from contributor forms, implement auto-generation in Post model save() method with uniqueness checks, update tests to verify slug generation.  
  - **Story Points:** 3  
  - **Owner:** Chun-Hung Yeh

- **S4-9**: Create Sprint 4 documentation (planning, review, retrospective, report)  
  - **Description:** Create comprehensive Sprint 4 documentation following format of previous sprints, including velocity tracking, completed work, demo notes, and retrospective insights.  
  - **Story Points:** 3  
  - **Owner:** Chun-Hung Yeh, with input from Celine and Denise

---

## 🧮 Story Points Committed

**Total: 26 points**

---

## 👥 Team Assignments

| Team Member | Responsibilities in Sprint 4 |
|-------------|------------------------------|
| **Chun-Hung Yeh** | A/B endpoint implementation, GA4 integration, production deployment verification, coverage setup, linting configuration, documentation updates, Sprint 4 docs creation |
| **Celine (Qijing) Li** | A/B endpoint testing, analytics verification, documentation review, UX validation |
| **Denise Wu** | Production deployment testing, A/B endpoint validation, documentation review, final polish feedback |

---

## ⚠️ Dependencies & Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Render infrastructure issues** | High | Monitor Render dashboard, have rollback plan, document deployment steps |
| **Misconfigured environment variables** | High | Create env var checklist, verify DATABASE_URL, GA_MEASUREMENT_ID in production |
| **A/B endpoint hash mismatch** | Medium | Double-check SHA1("far-storm") = 218b7ae, verify ASCII hyphen vs Unicode dash |
| **Time constraints for analytics verification** | Medium | Test GA events early in staging, verify in production ASAP |
| **Coverage tooling setup complexity** | Low | Use pyproject.toml for simple config, focus on critical paths only |
| **Documentation completeness** | Low | Follow Sprint 2/3 format, iterate with team feedback |

---

## 📋 Acceptance Criteria

### A/B Endpoint (S4-1)
- ✅ Endpoint accessible at `/218b7ae/` without authentication
- ✅ Displays team nickname "far-storm"
- ✅ Lists all three team members
- ✅ Button has `id="abtest"` and shows either "kudos" or "thanks"
- ✅ 50/50 variant distribution, persisted via cookie (30-day expiration)

### Analytics (S4-2)
- ✅ Single GA4 tag in base.html (no duplicates)
- ✅ GA_MEASUREMENT_ID from environment variable
- ✅ Events fired: `ab_variant_shown` (page load), `ab_variant_clicked` (button click)

### Production (S4-3, S4-4)
- ✅ PostgreSQL via DATABASE_URL (not SQLite)
- ✅ ALLOWED_HOSTS includes Render URL
- ✅ No hardcoded secrets
- ✅ Environment variables documented

### Code Quality (S4-5, S4-6)
- ✅ All tests passing (61+ tests)
- ✅ Coverage configured, >50% on critical paths
- ✅ Ruff configured and passing

### Documentation (S4-7, S4-9)
- ✅ README.md accurate and complete
- ✅ Sprint 4 planning, review, retrospective, report created

---

## 📅 Sprint Timeline

- **Week 1 (Nov 18-25):** A/B endpoint, GA integration, production verification
- **Week 2 (Nov 26-Dec 2):** Coverage, linting, documentation, final polish

---

## 🎯 Definition of Done

- All user stories completed and tested
- A/B endpoint publicly accessible and functional
- GA4 events tracking correctly
- Production deployment verified
- Coverage >50% on critical paths
- Linting passes cleanly
- Documentation updated and complete
- Sprint 4 docs (planning, review, retrospective, report) created

