# Sprint 3 Planning  

**Project:** Yale Newcomer Survival Guide  

**Sprint Duration:** 1 week  

**Team Members:** Chun-Hung Yeh, Qijing (Celine) Li, Denise Wu  

---

## 🎯 Sprint Goal  

Build a working MVP with at least one complete **Contributor → Admin → Public** user journey, including authentication, CRUD operations, permissions, staging deployment, and automated tests.

---

## 📌 User Stories Selected for Sprint 3

### Authentication & Roles

- **US-101**: Signup → auto-assign Contributor role (3 pts)  

- **US-102**: Login / Logout flow (2 pts)

### Contributor CRUD

- **US-201**: Create Post (5 pts)  

- **US-202**: Edit Own Posts (3 pts)  

- **US-203**: Delete Own Posts (3 pts)  

- **US-204**: Bookmark Posts (3 pts)

### Admin Workflow

- **US-301**: Approve/Reject Posts (5 pts)  

- **US-302**: Admin dashboard view (3 pts)

### Public User Journey

- **US-401**: Public sees approved posts (3 pts)  

- **US-402**: Public views post detail page (2 pts)

### Testing

- **US-501**: Unit tests for models (5 pts)  

- **US-502**: Integration tests for signup/login/CRUD/admin flow (5 pts)

### Staging & Deployment

- **US-601**: Configure PostgreSQL using DATABASE_URL (3 pts)  

- **US-602**: Add healthcheck endpoint (2 pts)

---

## 🧮 Story Points Committed  

**44 points**

---

## 👥 Team Assignments  

| Team Member | Responsibilities in Sprint 3 |
|-------------|------------------------------|
| **Chun-Hung Yeh** | Full-stack development (Django models, views, templates), PostgreSQL integration, staging deployment, authentication, CRUD, test suite, documentation |
| **Qijing (Celine) Li** | UX flow validation, content review, backlog refinement, user experience feedback |
| **Denise Wu** | Acceptance testing, UX critique, contributor-side workflow testing, feature prioritization |

---

## ⚠️ Dependencies & Risks  

| Risk | Impact | Mitigation |
|------|--------|------------|
| Incorrect Postgres settings | High | Use internal DB URL + healthcheck |
| Permission logic complexity | Medium | Write integration tests early |
| Staging deployment issues | Medium | Clear build cache when config changes |
| Time constraints | Medium | Focus on end-to-end journey only |

---

# Sprint 3 Review

## 🎯 Sprint Goal  

Deliver a functioning MVP with a complete Contributor → Admin → Public journey.

**Goal Achieved:** ✅ YES

---

## ✅ Completed User Stories

### Authentication & Roles

- Auto-assign Contributor role on signup  

- Full login/logout flow working  

### Contributor CRUD

- Create post  

- Edit own posts  

- Delete own posts  

- Bookmark posts  

### Admin Workflow

- Admin dashboard  

- Approve/reject posts  

- Approved posts become visible publicly  

### Public User Journey

- Public can browse approved posts  

- Public can view approved post details  

### Testing

- **51 total passing tests:**  

  - 30 unit tests  

  - 21 integration tests  

### Staging

- Postgres connected via `DATABASE_URL`  

- Healthcheck endpoint added  

- App deploys using psycopg 3  

- Ready for production

---

## ❌ Incomplete User Stories  

None — all Sprint 3 stories completed successfully.

---

## 🧪 Demo Summary  

A full working MVP journey:

1. User signs up → Contributor  

2. User logs in  

3. User creates post → pending  

4. Admin approves  

5. Post becomes public  

6. Public user can browse approved posts  

---

## 📊 Metrics  

Sprint 2 Velocity: 20  

Sprint 3 Velocity: 44  

Average Velocity: 32  

---

## 🎤 Stakeholder Feedback  

- Instructor emphasized importance of a complete user journey → fully accomplished  

- TA guidance on permissions & testing helped shape integration tests  

- Positive feedback on completeness of CRUD flow and clear permission boundaries

---

## 🔄 Backlog Refinements  

- Add analytics/events tracking  

- Implement search + filters  

- Improve contributor dashboard UI  

- Add content moderation flags  

- Add error pages and UX improvements  

- Implement A/B test endpoint for Sprint 4

---

# Sprint 3 Retrospective

## 👍 What Went Well

1. **MVP User Journey Fully Completed**  

   Authentication, Contributor CRUD, Admin workflow all working end-to-end.

2. **Comprehensive Test Suite Added**  

   51 passing tests give confidence in stability.

3. **Staging Environment Successfully Configured**  

   Postgres + WhiteNoise + healthcheck all deployed cleanly.

4. **Improved Development Speed**  

   Clear requirements and prompts significantly increased story throughput.

---

## 👎 What Didn't Go Well

1. **PostgreSQL Setup Confusion**  

   Render dashboard vs. projects vs. services caused unnecessary complexity.

2. **Role Permissions Initially Inconsistent**  

   Contributors could view others' draft/pending posts; fixed via integration tests.

---

## 🔧 What to Improve (Actionable)

1. **Simplify Environment Variable Workflow**  

   - Action: Centralize all env variable documentation  

   - Owner: Chun-Hung Yeh  

   - Due: Early Sprint 4  

2. **Better Automated Deployment Pipeline**  

   - Action: Add staging smoke-tests before deployment  

   - Owner: Chun-Hung Yeh  

   - Due: Sprint 4  

---

## 🧑‍🤝‍🧑 Team Dynamics Reflection  

Sprint 3 was a collaborative effort:  

- Chun-Hung built nearly all technical components  

- Celine validated UX flows and improved navigability  

- Denise performed acceptance testing and improved feature clarity  

Overall team collaboration is strong.

---

## ⭐ Action Items  

| Action Item | Owner | Deadline |
|------------|--------|----------|
| Document all env vars | Chun-Hung Yeh | Sprint 4 start |
| Add automated staging smoke tests | Chun-Hung Yeh | Sprint 4 |
| UI improvement tasks | Celine Li | Sprint 4 |
| Implement A/B test endpoint | Chun-Hung Yeh | Sprint 4 |

---

# Sprint 3 Report (for grading)

## 1. Sprint Goal & Achievement

**Goal:** Develop a working MVP featuring a complete Contributor → Admin → Public user journey, with authentication, CRUD operations, permissions, and staging deployment.

**Result:**  

The goal was fully achieved. The core user journey now works end-to-end, the database schema is complete, permissions are correct, and the staging environment is ready using Render PostgreSQL.

---

## 2. User Journey Demonstration (MVP)

The MVP implements the required complete workflow:

1. **User signs up** → automatically assigned Contributor role  

2. **User logs in**  

3. **User creates a post** → stored as Draft or Pending  

4. **Admin logs in** via admin dashboard  

5. **Admin approves the post** → published_at set automatically  

6. **Post becomes publicly visible**  

7. **Public user can browse and read the approved post**  

This satisfies the Sprint 3 requirement of user-value delivery.

---

## 3. Completed Work (with Story Points)

| User Story | Description | Points |
|------------|-------------|--------|
| US-101 | Signup w/ Contributor role auto-assignment | 3 |
| US-102 | Login/logout flow | 2 |
| US-201–204 | Contributor CRUD + bookmarks | 14 |
| US-301–302 | Admin approval workflow | 8 |
| US-401–402 | Public browsing | 5 |
| US-501–502 | 51 automated tests | 10 |
| US-601–602 | Staging setup + healthcheck | 2 |

**Total Completed:** **44 points**

---

## 4. Velocity Tracking

- **Sprint 2 Velocity:** 20 pts  

- **Sprint 3 Velocity:** 44 pts  

- **Average Velocity:** 32 pts  

The increase reflects both growing clarity and larger technical tasks in Sprint 3.

---

## 5. Technical Progress

### What's Working Well

- Authentication system is stable  

- Contributor role fully operational  

- Admin approval dashboard functioning  

- Public-facing content works  

- All 51 tests pass, ensuring reliability  

- Staging configured with proper DB + healthcheck  

### Remaining Technical Challenges

- Need analytics tracking for Sprint 4  

- Need UI enhancements for contributor dashboard  

- Need A/B testing endpoint (`/218b7ae/` for team far-storm)  

- Need more robust error handling before final submission  

---

## 6. Sprint Retrospective Highlights

### What Went Well  

- Full user journey completed  

- Tests greatly increased confidence  

- Staging environment reliably deploys

### What Didn't Go Well  

- Render PostgreSQL setup was confusing  

- Initial permissions logic required fixes  

### What to Improve  

- Better documentation of environment variables  

- Add automated staging smoke tests  

- Improve UI polish for contributors  

---

## 7. Sprint 4 Preview

Sprint 4 will focus on:

- Completing remaining MVP polish  

- Implementing the required A/B test endpoint  

- Adding analytics tracking  

- Enhancing UI consistency  

- Further expanding test coverage  

- Preparing final documentation and demo  

---

## 8. Links

- GitHub Project Board: https://github.com/users/she24731/projects/6  

- This document: docs/sprints/Sprint_3_review.md

---

**Sprint 3 successfully delivered a working MVP with complete user value, strong code quality, and staging readiness.**

---
