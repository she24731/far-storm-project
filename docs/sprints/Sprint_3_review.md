# Sprint 3 Planning  

**Project:** Yale Newcomer Survival Guide  

**Sprint Duration:** 1 week  

**Team Size:** Solo Developer (Yang)  

---

## 🎯 Sprint Goal  

Build a working MVP with at least one **complete contributor → admin → public** user journey, including authentication, CRUD operations, role permissions, and staging readiness.

---

## 📌 User Stories Selected for Sprint 3

### Authentication & Roles

- **US-101**: As a user, I can sign up and automatically be assigned the *Contributor* role. (3 pts)

- **US-102**: As a user, I can log in and log out. (2 pts)

### Contributor CRUD

- **US-201**: As a Contributor, I can create a post. (5 pts)  

- **US-202**: As a Contributor, I can edit my own posts. (3 pts)  

- **US-203**: As a Contributor, I can delete my own posts. (3 pts)  

- **US-204**: As a Contributor, I can bookmark posts. (3 pts)

### Admin Workflow

- **US-301**: As an Admin, I can approve or reject pending posts. (5 pts)  

- **US-302**: As an Admin, I can see all submissions in a dashboard. (3 pts)

### Public User Journey

- **US-401**: As a public user, I can browse approved posts. (3 pts)  

- **US-402**: As a public user, I can open a post detail page. (2 pts)

### Testing

- **US-501**: Add unit tests for Post, Category, ExternalLink, Bookmark models. (5 pts)  

- **US-502**: Add integration tests for signup/login/CRUD/admin flow. (5 pts)

### Staging Environment

- **US-601**: Configure PostgreSQL using `DATABASE_URL` for staging. (3 pts)  

- **US-602**: Add healthcheck endpoint. (2 pts)

---

## 🧮 Story Points Committed  

Total committed: **44 points**

---

## 👥 Team Assignments  

- **Yang Zhao** — All design, development, testing, documentation

---

## ⚠️ Dependencies & Risks  

| Risk | Impact | Mitigation |
|------|--------|------------|
| Render PostgreSQL misconfiguration | High | Use internal DB URL; add healthcheck endpoint |
| Django permissions complexity | Medium | Write integration tests early |
| Staging deployment errors | Medium | Use "Clear build cache & deploy" when configs change |
| Time constraints | Medium | Focus on one complete user journey |

---

---

# Sprint 3 Review  

**Project:** Yale Newcomer Survival Guide  

**Sprint:** 3  

---

## 🎯 Sprint Goal  

Implement a fully functional MVP with:  

- complete contributor → admin → public user journey  

- CRUD operations  

- role permissions  

- user authentication  

- working tests  

- staging environment readiness  

### ✅ Goal Achieved — **YES**

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

**Full user journey demonstrated:**

1. User signs up → assigned Contributor  

2. User logs in  

3. User creates a post → post enters *Pending Review*  

4. Admin logs in → approves the post  

5. Public visitor can now see the approved post  

This meets the Sprint 3 requirement of at least *one complete end-to-end workflow*.

---

## 📊 Metrics  

**Sprint 2 Velocity:** 20 points  

**Sprint 3 Velocity:** 44 points *(solo developer – increased velocity due to clarity + automation)*  

**Average Velocity:**  

(20 + 44) / 2 = **32 points**

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

**Project:** Yale Newcomer Survival Guide  

---

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

   - Owner: Yang  

   - Due: Early Sprint 4  

2. **Better Automated Deployment Pipeline**  

   - Action: Add staging smoke-tests before deployment  

   - Owner: Yang  

   - Due: Sprint 4  

---

## 🧑‍🤝‍🧑 Team Dynamics Reflection  

Solo developer sprint → advantages:  

- Fast decision-making  

- Rapid iteration  

- Tight integration between code + testing + deployment  

Challenges:  

- No second reviewer for code  

- All tasks require context-switching  

Overall team health: **Strong**, but Sprint 4 should incorporate peer review where possible.

---

## ⭐ Action Items  

| Action Item | Owner | Deadline |
|------------|--------|----------|
| Document all env vars | Yang | Sprint 4 start |
| Add automated staging smoke tests | Yang | Sprint 4 |
| UI improvement tasks | Yang | Sprint 4 |
| Implement A/B test endpoint | Yang | Sprint 4 |

---

# Sprint 3 Report  

**Course:** MGT 656 – Sprint Development  

**Project:** Yale Newcomer Survival Guide  

**Sprint:** 3  

---

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

- Need A/B testing endpoint (`/{7-char-sha1-hash}`)  

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

- **Sprint Planning / Review / Retrospective Doc:** `docs/sprints/Sprint_3_review.md`  

- **GitHub Project Board:** https://github.com/users/she24731/projects/6  

---

**Sprint 3 successfully delivered a working MVP with complete user value, strong code quality, and staging readiness.**

---

