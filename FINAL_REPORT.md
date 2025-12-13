# Final Project Report — Team far-storm

**Team Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)  
**Course:** MGT656 - Management of Software Development  
**Project:** Yale Newcomer Survival Guide  
**Project Duration:** 4 Sprints

---

## 1. Project Overview

### Problem Statement

New students and staff arriving at Yale face numerous challenges when transitioning to life in New Haven: finding suitable housing, discovering local restaurants, understanding public transportation, navigating academic resources, and identifying essential services. Existing information sources are scattered across multiple platforms (Facebook groups, university websites, word-of-mouth), making it difficult for newcomers to find reliable, up-to-date information in one place.

### Solution

The Yale Newcomer Survival Guide provides a centralized, community-driven web platform where experienced Yale community members can share knowledge through categorized posts, while newcomers can easily discover essential information. The platform implements a contributor-admin moderation workflow to ensure content quality while maintaining community engagement.

### Target Users

- **Newcomers:** Students, staff, and faculty new to Yale who need practical, actionable information
- **Contributors:** Existing community members who want to share knowledge and recommendations
- **Admins:** Content moderators responsible for reviewing and approving posts to maintain quality standards

### Technology Stack

The application is built using Django 4.2.26 with PostgreSQL (production) and SQLite (local development). The frontend uses Bootstrap 5 for responsive design. Deployment is handled via Render with separate staging and production environments. Continuous integration is implemented through GitHub Actions, running automated tests and linting on every push. Google Analytics 4 is integrated for real-time monitoring, while server-side event tracking via the `ABTestEvent` model provides the primary source of truth for analytics.

### Core Features

1. **User Authentication & Role Management:** Django's built-in authentication extended with role-based access control (Reader, Contributor, Admin)
2. **Content Creation & Moderation:** Three-stage workflow (draft → pending → approved/rejected) with admin review
3. **Category-Based Organization:** Posts organized by categories with pagination and search functionality
4. **Contributor & Admin Dashboards:** Personal dashboards for managing posts and moderation workflows
5. **A/B Testing Infrastructure:** Analytics endpoint at `/218b7ae/` for experimentation with button label variants

---

## 2. Burndown & Velocity Analysis

### Agile Process & Scrum Execution

Team far-storm followed Scrum methodology with four 2-week sprints. Each sprint included planning sessions, daily standups, sprint reviews, and retrospectives. User stories were estimated using a modified Fibonacci scale (1, 2, 3, 5, 8, 13 story points) and organized by dependencies and priority.

### Sprint Velocity Tracking

Velocity was tracked by comparing planned vs completed story points per sprint. The team maintained consistent delivery throughout the project:

| Sprint | Planned Points | Completed Points | Velocity | Completion Rate |
|--------|----------------|------------------|----------|-----------------|
| Sprint 1 | 20 | 18 | 18 | 90.0% |
| Sprint 2 | 22 | 20 | 20 | 90.9% |
| Sprint 3 | 25 | 23 | 23 | 92.0% |
| Sprint 4 | 24 | 24 | 24 | 100.0% |

**Average Velocity:** 21.25 points per sprint

### Velocity Chart

The following chart visualizes planned vs completed story points across all four sprints:

![Sprint Velocity Chart](velocity.png)

*Chart generated using `scripts/velocity_chart.py`. See `docs/final-report.md` for regeneration instructions.*

### Velocity Analysis

The team demonstrated strong estimation accuracy and consistent delivery. Sprint 1 established a baseline velocity of 18 points, which increased to 20 points in Sprint 2 as the team gained familiarity with the codebase and improved coordination. Sprint 3 saw further improvement to 23 points, and Sprint 4 achieved perfect completion (100%) with 24 points, demonstrating the team's maturing Agile practices and refined estimation process.

The upward trend in velocity reflects several factors: improved task breakdown, better parallel work coordination, reduced migration conflicts through established workflows, and increased familiarity with Django and the project architecture. The consistent completion rates (90%+) indicate realistic planning and effective sprint commitment practices.

### Burndown Tracking

Sprint reviews documented progress toward sprint goals throughout the project. The velocity chart above and velocity data table show consistent delivery patterns across all sprints, with each sprint completing the majority of committed work. Sprint 4's 100% completion rate demonstrates the team's ability to accurately estimate capacity and deliver on commitments.

### Process Improvements

Throughout the sprints, the team implemented several process improvements based on retrospectives:
- Established migration workflow to prevent conflicts
- Improved template organization and architecture
- Enhanced access control testing procedures
- Documented deployment and environment configuration processes

---

## 3. Traffic & A/B Test Analysis

### A/B Test Design

The A/B test endpoint at `/218b7ae/` (derived from first 7 characters of SHA1("far-storm")) tests button label variants "kudos" and "thanks" to measure user engagement. The experiment implements a 50/50 random split with variant assignment persisted via Django session cookies. Server-side event tracking via the `ABTestEvent` model records exposures (first page load per session, deduplicated) and conversions (button clicks).

### Data Collection Methodology

Event tracking implements session-based deduplication to prevent double-counting from page reloads. Bot filtering excludes non-human traffic through User-Agent analysis, header validation (`Sec-Fetch-Mode: navigate`), and request method checks. Analysis was performed using the `python manage.py abtest_report` management command, which queries the `ABTestEvent` table for experiment `button_label_kudos_vs_thanks` and calculates conversion rates per variant.

### Analytics Results

**Performance Metrics:**
- **"kudos" variant:** 50 exposures, 10 conversions = **20.00% conversion rate**
- **"thanks" variant:** 60 exposures, 18 conversions = **30.00% conversion rate**

The "thanks" variant demonstrates superior engagement with a conversion rate 10 percentage points higher than "kudos" (50% relative improvement). Total sample size of 110 exposures exceeds the minimum threshold of 30 exposures recommended for basic analysis.

**Data Quality:**
Bot traffic was filtered to ensure data reliability. Session-based deduplication prevents inflation of exposure counts. Server-side tracking provides authoritative data source unaffected by client-side blockers or ad blockers. Google Analytics 4 integration provides real-time monitoring for validation, but server-side `ABTestEvent` records serve as the primary source of truth.

### Preferred Variant Determination

**Winner: "thanks"**

The "thanks" variant is the preferred button label based on its superior conversion performance. With a 30.00% conversion rate compared to 20.00% for "kudos", the "thanks" variant achieved a 50% relative improvement in user engagement.

**Rationale:**
1. **Higher Conversion Rate:** 30.00% vs 20.00% (10 percentage point absolute difference)
2. **Larger Sample Size:** 60 exposures vs 50 exposures provides additional statistical confidence
3. **Relative Performance:** 50% improvement indicates substantial difference in user response
4. **Clear Pattern:** The performance gap suggests genuine user preference rather than random variation

The total sample size of 110 exposures meets the minimum threshold for basic analysis (≥30 exposures). While larger samples (ideally ≥100 per variant) would provide stronger statistical significance, the current data demonstrates a clear performance difference that supports the selection of "thanks" as the preferred variant.

---

## 4. Project Retrospective

### What Went Well

1. **Consistent Agile Execution:** The team maintained strong Scrum practices throughout all four sprints. Daily standups, sprint planning, reviews, and retrospectives were conducted regularly, enabling effective coordination and continuous improvement. Velocity tracking showed consistent delivery (average 21.25 points per sprint) with improving accuracy over time.

2. **Solid Technical Foundation:** Django project structure was established correctly from the start, with well-designed database schema requiring minimal refactoring. Early investment in testing infrastructure (111+ tests, >75% coverage) paid dividends throughout development, catching issues early and preventing regressions.

3. **Successful Production Deployment:** Smooth deployment to Render with PostgreSQL, WhiteNoise for static files, and proper environment variable configuration. Separate staging and production environments enabled safe testing before production exposure. CI/CD pipeline via GitHub Actions automated quality checks and deployment processes.

4. **A/B Testing Implementation:** The `/218b7ae/` endpoint was implemented correctly with proper variant assignment, session-based deduplication, and dual-tracking (server-side + GA4). Event tracking infrastructure provides reliable data for analysis, with comprehensive bot filtering ensuring data quality.

5. **Team Collaboration:** Clear communication, effective task distribution, and constructive code reviews enabled parallel development with minimal conflicts. All team members contributed across backend, frontend, deployment, and documentation areas.

### Challenges

1. **Migration Conflicts:** Multiple developers creating migrations simultaneously caused conflicts requiring careful resolution. **Resolution:** Established migration workflow requiring team members to pull before creating new migrations and communicate before migration creation.

2. **A/B Test Event Deduplication:** Initial implementation logged duplicate exposures from page reloads. **Resolution:** Implemented session flags combined with database `get_or_create()` with uniqueness constraints, ensuring atomicity and preventing double-counting.

3. **Cache Control for A/B Tests:** Variant assignment getting cached by browsers/CDNs, causing users to see same variant repeatedly. **Resolution:** Added `@never_cache` decorator and explicit cache-control headers to prevent caching.

4. **Environment Variable Configuration:** Initial confusion about which variables needed for staging vs production and where to set them in Render. **Resolution:** Created environment variable checklist and documentation, ensuring 12-factor compliance.

5. **Template Organization:** Template files grew large with some duplication emerging. **Resolution:** Extracted reusable components and improved template architecture, though full refactoring was deferred to maintain sprint velocity.

### Lessons Learned

1. **12-Factor Principles:** Environment-based configuration makes deployment significantly easier and more secure. No secrets in code improves security posture and simplifies environment management. Explicitly following all 12 principles from the start would have prevented configuration confusion later.

2. **Dual-Tracking Analytics:** Server-side tracking provides reliable data unaffected by ad blockers, while client-side GA4 provides immediate visibility. Both approaches have value and complement each other. Relying on server-side data as source of truth while using GA4 for validation is an effective pattern.

3. **Staging Environments:** Separate staging environment is invaluable for testing database migrations, configuration changes, and new features before production exposure. Staging catches issues that would otherwise impact production users.

4. **Session-Based State Management:** Django sessions provide reliable mechanism for user state management, but require careful consideration of caching and deduplication for analytics use cases. Session flags combined with database uniqueness constraints ensure accurate event tracking.

5. **A/B Test Complexity:** Implementing accurate exposure deduplication requires both session-level and database-level checks. The combination of session flags and `get_or_create()` with uniqueness constraints provides atomicity and prevents race conditions. Cache control is critical for valid A/B test results.

### What Would Be Done Differently

1. **Start Deployment Planning Earlier:** Begin planning deployment infrastructure and 12-factor compliance in Sprint 1-2 instead of Sprint 4, preventing configuration confusion that occurred later and allowing more time for refinement.

2. **Establish Infrastructure Checklists Earlier:** Create deployment and environment variable checklists in Sprint 1, preventing configuration confusion and establishing best practices from the start.

3. **Account for Refactoring Time:** Allocate more realistic time estimates for refactoring tasks (e.g., template organization). Refactoring often takes longer than estimated and requires comprehensive testing afterward.

4. **Improve Test Coverage Earlier:** Aim for 80%+ coverage from Sprint 1, writing tests alongside features rather than after. Higher early coverage would have caught edge cases sooner, particularly in access control and workflow logic.

5. **Document State Machine Designs Upfront:** Document post status workflow states and transitions clearly in Sprint 1, preventing complexity underestimation and ensuring consistent implementation.

### Team Contributions

**stormy-deer (Chun-Hung Yeh):** Backend architecture, A/B testing implementation, analytics integration, production deployment, CI/CD configuration, 12-factor compliance, comprehensive testing infrastructure, management commands.

**adorable-crow (Celine Li):** Frontend development, template architecture, Bootstrap integration, user authentication, contributor features, UI/UX design, user experience testing, code reviews.

**super-giraffe (Denise Wu):** Database design, admin tools, moderation workflows, category organization, URL routing, view implementation, A/B testing planning, production testing, sprint documentation.

Per course policy, all team members share equal responsibility for project outcomes and grading. The project represents a collaborative effort with code reviews, pair programming, and shared decision-making throughout all four sprints.

---

## Project Management & Agile Artifacts

Project management, sprint planning, user stories, tasks, and spikes were tracked using GitHub Projects.

The full project board (including Product Backlog, Sprint Backlog, and Task Board views) is available at:

**https://github.com/users/she24731/projects/6/**

---

## Conclusion

The Yale Newcomer Survival Guide successfully delivers a functional MVP that addresses a real need within the Yale community. The application demonstrates solid software engineering practices: comprehensive testing, 12-factor app compliance, proper deployment procedures, and data-driven experimentation via A/B testing.

The project highlights the importance of infrastructure planning, the value of staging environments, and the complexity of accurate analytics tracking. While challenges were encountered (migration conflicts, event deduplication, configuration management), they were resolved through systematic problem-solving and team collaboration.

The A/B testing infrastructure is fully functional, with results indicating that the "thanks" variant outperforms "kudos" with a 30.00% conversion rate versus 20.00%. The dual-tracking approach (server-side + GA4) provides both reliability and real-time visibility.

**Team far-storm (stormy-deer, adorable-crow, super-giraffe) - Project Complete.**

---

*Report generated: December 2024*  
*Sprint documentation available in `/docs/sprints/`*  
*Velocity chart: `/docs/velocity.png`*  
*A/B test analysis: `python manage.py abtest_report`*

