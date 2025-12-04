# Sprint 4 Retrospective – far-storm

**Project:** Yale Newcomer Survival Guide  
**Sprint Duration:** 2 weeks  
**Dates:** November 18, 2024 – December 2, 2024  
**Team Members:** Chun-Hung Yeh, Celine (Qijing) Li, Denise Wu

---

## 👍 What Went Well

### 1. **Stabilized Production Deployment**
   - Successfully migrated from SQLite to PostgreSQL on Render
   - Configured `DATABASE_URL` via `dj_database_url` for seamless local/production switching
   - WhiteNoise static file serving working reliably
   - Auto-deploy pipeline stable and predictable

### 2. **End-to-End MVP User Journey Working Flawlessly**
   - Complete Contributor → Admin → Public workflow functional in production
   - Permission boundaries clear and tested
   - Post workflow (draft → pending → approved) working as designed
   - All 61 tests passing gives high confidence in stability

### 3. **Successfully Implemented A/B Endpoint and GA Tracking**
   - A/B endpoint at `/218b7ae/` implemented correctly (verified SHA1 hash)
   - Cookie-based variant persistence working as intended
   - GA4 integration clean with single tag, no duplicates
   - Event tracking for variant shown and button clicks functional

### 4. **Improved Use of AI Tools (Cursor/LLM)**
   - Significantly accelerated repetitive coding tasks (boilerplate, test generation)
   - Helped with Django configuration and best practices
   - Useful for documentation generation and formatting
   - Enabled faster iteration on features while maintaining quality

### 5. **Effective Environment Separation**
   - Having both a dedicated staging service on Render and a production service made it safer to test migrations, the A/B endpoint, and GA integration before exposing changes to real users.
   - Clear separation between staging and production reduced risk when changing database config, auth, and A/B test behavior.

### 5. **Code Quality Infrastructure Established**
   - Coverage tooling configured and generating useful reports (69% overall, 100% on models)
   - Ruff linting catching issues early
   - Test suite comprehensive and reliable
   - 12-factor configuration principles followed throughout

---

## 👎 What Didn't Go Well

### 1. **Hash Mismatch for A/B Endpoint Initially**
   - Initially confused EN dash (Unicode) vs ASCII hyphen in team nickname
   - SHA1("far–storm") ≠ SHA1("far-storm") caused endpoint mismatch
   - Required careful audit to ensure consistency across all files
   - **Lesson learned:** Always verify exact string matching when using hashes for deterministic paths

### 2. **Environment Variable Configuration Confusion**
   - Uncertainty around where to set `DATABASE_URL` (Render dashboard vs project vs service)
   - Initial confusion between `DJANGO_ALLOWED_HOSTS` and hardcoded list
   - Time lost debugging infrastructure instead of focusing on features
   - **Lesson learned:** Document environment variable requirements clearly upfront

### 3. **GA Verification Challenges**
   - Initial confusion between view-source inspection vs browser devtools
   - Uncertainty about staging vs production GA event visibility
   - Time spent verifying analytics instead of building features
   - **Lesson learned:** Set up analytics verification checklist earlier in sprint

### 4. **Time Spent on Configuration Rather Than Features**
   - More time allocated to deployment and infrastructure setup than originally planned
   - Coverage and linting setup took longer than expected
   - Would have preferred more time for UX polish and content

---

## 🔧 What to Improve for Final Submission Period

### 1. **Establish Clear Infrastructure Change Checklist**
   - **Action:** Create a checklist for any changes to environment variables, database settings, or deployment configuration
   - **Include:** Verify locally first, document changes, test in staging before production
   - **Owner:** Chun-Hung Yeh
   - **Target:** Final submission period

### 2. **Prioritize Earlier Analytics Verification**
   - **Action:** Test GA events immediately after implementation, verify in production within 24 hours
   - **Include:** Use browser devtools Network tab and GA Real-Time view for immediate feedback
   - **Owner:** Team (all members verify)
   - **Target:** Before final submission

### 3. **Smaller, More Frequent Commits with Clear Descriptions**
   - **Action:** Break larger changes into smaller commits with descriptive messages
   - **Include:** Reference issue/story IDs when possible, ensure tests pass before committing
   - **Owner:** Chun-Hung Yeh
   - **Target:** Ongoing practice

### 4. **Documentation as We Go**
   - **Action:** Update README and docs immediately when making configuration changes
   - **Include:** Don't wait until end of sprint to document changes
   - **Owner:** Chun-Hung Yeh
   - **Target:** Final submission period

---

## 📋 Action Items

| Task | Owner | Target Deadline |
|------|-------|----------------|
| Collect and analyze GA4 A/B test data (variant distribution, click rates) | Celine Li | December 5, 2024 |
| Create velocity and burndown charts for Sprints 2-4 | Denise Wu | December 6, 2024 |
| Prepare final course report with all sprint summaries | Chun-Hung Yeh | December 8, 2024 |
| Review production site for final UX polish | Celine Li, Denise Wu | December 7, 2024 |
| Verify all links and navigation work correctly in production | Denise Wu | December 7, 2024 |

---

## 💭 Project Reflection

### Learning to Build and Deploy Django on Render

This project provided hands-on experience with modern Django deployment practices. We learned the importance of 12-factor app principles—configuring everything through environment variables, using `dj_database_url` for flexible database connections, and ensuring static files are served efficiently via WhiteNoise. The transition from local SQLite development to production PostgreSQL required careful attention to connection pooling and migration strategies. Render's platform simplified deployment, but understanding the build process, health checks, and environment variable management was crucial for reliable production operation.

### Working with A/B Testing and Analytics

Implementing the A/B test endpoint taught us about deterministic routing (using SHA1 hashes), cookie-based state persistence, and the importance of exact string matching. Integrating Google Analytics 4 required understanding event tracking, measurement IDs, and ensuring no duplicate tags. We learned that analytics verification requires patience—events don't always appear immediately, and browser devtools are essential for debugging. The event structure we implemented (`ab_variant_shown`, `ab_variant_clicked`) provides a foundation for analyzing user preferences between "kudos" and "thanks" variants.

### Balancing Feature Work and Infrastructure

Sprint 4 highlighted the reality that production readiness requires significant infrastructure investment. While we delivered all planned features (A/B endpoint, analytics, coverage, linting), we spent substantial time on deployment configuration, environment variable management, and code quality tooling. This is a valuable lesson: infrastructure work is not "less important" than features—it's essential for maintainability and scalability. However, in future projects, we'd allocate more explicit time for infrastructure tasks in sprint planning.

### The Role of AI Tools (Cursor + LLM)

AI-assisted development was a game-changer for this project. Cursor's LLM integration accelerated boilerplate code generation, Django configuration, test writing, and documentation creation. It was particularly helpful for:
- Generating comprehensive test cases
- Writing Django views and forms following best practices
- Creating documentation that matches existing formats
- Debugging configuration issues with quick explanations

However, we learned that AI tools require careful human oversight:
- **DATABASE_URL configuration:** AI suggested various approaches, but we needed to verify Render-specific requirements
- **SHA1 hash verification:** AI didn't catch the Unicode vs ASCII dash difference initially—human verification was essential
- **GA verification:** AI provided guidance, but actual browser testing was required to confirm events were firing

The key lesson: AI tools are powerful accelerators, but critical decisions (like production configuration, hash verification, and analytics validation) require human judgment and testing. We developed a workflow where AI generates initial code and documentation, then we verify, test, and refine.

---

## 🎯 Key Takeaways for Future Sprints

1. **Infrastructure work deserves explicit story points** – Don't underestimate configuration and deployment time
2. **Verify string matching carefully when using hashes** – Unicode vs ASCII matters
3. **Test analytics immediately** – Don't wait until end of sprint to verify GA events
4. **Document as you go** – Prevents last-minute documentation rushes
5. **AI tools are accelerators, not replacements** – Human verification remains critical for production code

---

## 🙏 Team Appreciation

Sprint 4 required focused effort from all team members:
- **Chun-Hung** handled the bulk of technical implementation and documentation
- **Celine** provided valuable testing and UX feedback on the A/B endpoint
- **Denise** verified production deployment and provided critical QA

The team's collaborative approach and shared commitment to quality made Sprint 4 a success. Ready for final submission!

---

### Environment Setup Reflection

Staging on Render (https://yale-newcomer-survival-guide-staging.onrender.com/) was used for integration testing and QA. Production on Render (https://yale-newcomer-survival-guide.onrender.com/) is used for course traffic and final submission. Local development (`python manage.py runserver` at http://127.0.0.1:8000) was used for rapid iteration before pushing to staging. This separation helped reduce risk when changing database config, auth, and A/B test behavior. Having distinct environments allowed us to verify migrations, test A/B endpoint variants, and validate GA integration safely before promoting changes to production.

---

**Sprint 4 Retrospective Complete**

