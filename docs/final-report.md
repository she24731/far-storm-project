# Final Project Report — Team far-storm

**Team Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)  
**Course:** MGT656 - Management of Software Development  
**Project:** Yale Newcomer Survival Guide  
**Project Duration:** 4 Sprints

---

## 1. Project Overview

### Problem Statement

New students and staff arriving at Yale face numerous challenges when transitioning to life in New Haven: finding suitable housing, discovering local restaurants and dining options, understanding public transportation systems, navigating academic resources, and identifying essential services. Existing information sources are scattered across multiple platforms (Facebook groups, university websites, word-of-mouth), making it difficult for newcomers to find reliable, up-to-date, and contextually relevant information in one place.

### Solution

The Yale Newcomer Survival Guide provides a centralized, community-driven web platform where experienced Yale community members can share knowledge through categorized posts, while newcomers can easily discover essential information. The platform implements a contributor-admin moderation workflow to ensure content quality while maintaining community engagement and organic growth.

### Target Users

- **Newcomers:** Students, staff, and faculty new to Yale who need practical, actionable information about life in New Haven
- **Contributors:** Existing community members who want to share knowledge, experiences, and recommendations to help others
- **Admins:** Content moderators responsible for reviewing and approving posts to maintain quality standards

### Appropriateness and Tractability

This solution is appropriate because it addresses a real, recurring need (every academic year brings new arrivals) and leverages community knowledge that already exists but is currently fragmented. The solution is tractable because:

1. **Well-defined scope:** Core features (content creation, categorization, moderation) map to standard web application patterns
2. **Proven technologies:** Django provides robust authentication, ORM, and admin tools out of the box
3. **Clear user workflows:** Contributor → Admin → Public pipeline is straightforward to implement and test
4. **Incremental complexity:** Features can be developed and deployed iteratively across sprints

---

## 2. Technology Stack

### Backend Framework

**Django 4.2.26** was selected as the backend framework. Django provides:
- Built-in authentication and authorization systems
- Object-Relational Mapping (ORM) for database operations
- Admin interface for content management
- Security features (CSRF protection, SQL injection prevention)
- Extensible architecture through apps and middleware

### Database

- **Production:** PostgreSQL via `DATABASE_URL` environment variable (managed by Render)
- **Local Development:** SQLite (automatic fallback when `DATABASE_URL` not set)
- **Configuration:** Uses `dj-database-url` library for flexible database connection management

The application uses Django migrations for schema management, ensuring database changes are version-controlled and reproducible across environments.

### Frontend Technologies

- **Bootstrap 5:** Responsive UI framework for consistent styling and mobile-friendly layouts
- **Django Templates:** Server-side rendering with template inheritance (`base.html`)
- **JavaScript:** Minimal client-side scripting for A/B test button interactions and GA4 event tracking

### Analytics Approach

**Dual-Tracking Architecture:**
- **Server-Side:** `ABTestEvent` model in Django database records all exposure and conversion events
- **Client-Side:** Google Analytics 4 (GA4) with measurement ID `G-9XJWT2P5LE` for real-time monitoring

This approach provides redundancy: server-side data is the source of truth (unaffected by ad blockers), while GA4 provides immediate visibility into user behavior.

### Deployment Platform

**Render** was used for both staging and production environments:
- **Staging:** Separate service for testing changes before production
- **Production:** Live environment serving end users
- **Static Files:** WhiteNoise middleware serves static files efficiently
- **Build Process:** Automated deployments via `render.yaml` configuration

---

## 3. Core Application Features

### Feature 1: User Authentication & Role Management

**Implementation:** Django's built-in authentication system extended with user groups (Reader, Contributor, Admin). Automatic role assignment on registration, with role-based access control throughout the application.

**User Value:** Secure, personalized access to features based on user type. New users automatically become Contributors, enabling immediate content creation while maintaining clear permission boundaries.

**User Story:** "As a new user, I want to register and log in to access personalized features" (Sprint 1).

### Feature 2: Content Creation & Management

**Implementation:** Contributors can create, edit, and manage posts through a dedicated submission interface. Posts support draft status for refinement before submission, with auto-generated unique slugs from titles.

**User Value:** Easy content creation workflow allows community members to share knowledge without technical barriers. Draft functionality enables iterative refinement before public submission.

**User Stories:** "As a contributor, I want to create and organize posts by categories" (Sprint 1), "As a contributor, I want to fully manage my posts through the dashboard" (Sprint 3).

### Feature 3: Category-Based Organization

**Implementation:** Posts are organized into categories (Housing, Food, Transport, Academics, etc.) with dedicated listing and detail pages. Public users can browse posts by category with pagination support.

**User Value:** Intuitive navigation helps newcomers quickly find relevant information. Category organization reduces information overload and improves discoverability.

**User Story:** "As a user, I want to browse posts by category so that I can find relevant information quickly" (Sprint 2).

### Feature 4: Post Workflow & Moderation

**Implementation:** Three-stage workflow: Draft → Pending → Approved/Rejected. Admins review pending posts through a dedicated dashboard with approve/reject actions. Approved posts automatically receive `published_at` timestamps and become publicly visible.

**User Value:** Quality assurance ensures only accurate, helpful content reaches newcomers. Contributors receive clear feedback on submission status, while admins have efficient moderation tools.

**User Stories:** "As an admin, I want tools to review and moderate posts" (Sprint 3), related workflow stories across Sprints 1-3.

### Feature 5: A/B Testing Infrastructure

**Implementation:** Publicly accessible endpoint `/218b7ae/` (derived from the first 7 characters of SHA1("far-storm")) displays team information and a button that randomly shows either "kudos" or "thanks" (50/50 split, persisted via session). Server-side `ABTestEvent` model tracks exposures and conversions; GA4 provides client-side validation.

**User Value:** Enables data-driven decision-making about button label preferences, demonstrating analytics integration and experimentation capabilities.

**User Story:** "Implement A/B test endpoint at `/218b7ae/`" (Sprint 4).

---

## 4. A/B Test Design & Analytics (CRITICAL)

### Endpoint Specification

The A/B test endpoint is located at `/218b7ae/`, which is derived from the first 7 characters of the SHA1 hash of the team nickname "far-storm":

```python
import hashlib
hashlib.sha1("far-storm".encode()).hexdigest()[:7]  # Returns: "218b7ae"
```

This deterministic approach ensures the endpoint is publicly accessible, memorable, and verifiable. The endpoint displays:
- Team nickname: "far-storm"
- Team member list: stormy-deer, adorable-crow, super-giraffe
- A button with `id="abtest"` showing either "kudos" or "thanks"

### Exposure vs Conversion

**Exposure Events (Distinct from Conversions):** An exposure event is logged when a user first visits `/218b7ae/` in a session and meets the criteria for a real user (browser User-Agent, proper navigation headers). An exposure represents one user seeing one variant. **Critically, an exposure does NOT require any user action**—it is automatically logged on page load if the user meets the real-user filtering criteria.

**Conversion Events (Distinct from Exposures):** A conversion event is logged only when a user actively clicks the button with `id="abtest"`. A conversion represents explicit user engagement with the variant. **Importantly, conversions require user interaction, while exposures are passive observations.**

**Key Distinction:** Exposures measure reach (how many users saw the variant), while conversions measure engagement (how many users clicked). The conversion rate is calculated as (conversions / exposures) × 100%, indicating what percentage of users who saw a variant actually clicked it. Multiple conversions per session are allowed (users can click multiple times), but only one exposure per session is logged.

### Session-Level Deduplication (Critical for Accuracy)

**Explicit Deduplication Strategy:** To prevent double-counting exposures from page refreshes, browser back/forward navigation, or multiple requests within the same session, the system implements explicit session-based deduplication:

1. **Session Flag Check:** Before logging an exposure, the system checks if Django session contains `abexp:button_label_kudos_vs_thanks:exposed:/218b7ae/` flag. If this flag exists, no exposure is logged.
2. **Database Uniqueness Constraint:** When an exposure is logged, `ABTestEvent.objects.get_or_create()` is used with uniqueness constraints on `(experiment_name, event_type="exposure", endpoint, session_id)`. This ensures database-level deduplication even if session checks fail.
3. **Atomicity:** The combination of session flag and database `get_or_create()` ensures atomicity, preventing race conditions in concurrent requests.

**Explicit Behavior:** Reloading `/218b7ae/` in the same browser session does NOT create a duplicate exposure event. However, clicking the button multiple times DOES create multiple conversion events (as intended, since each click represents genuine user engagement). This deduplication ensures that exposure counts accurately reflect unique user sessions, not page loads.

### Bot Traffic Handling

**Expected Bot Traffic:** Bot traffic appears in web analytics and is expected in this educational context. Sources include:
- **Instructor/Grader Traffic:** Automated testing and evaluation scripts used by course instructors and graders to verify functionality
- **Health Checks:** Monitoring services (Render platform, uptime checkers) making periodic automated requests
- **Crawlers:** Search engine bots, RSS feed readers, social media link previews
- **Testing Tools:** Automated testing frameworks, CI/CD pipeline checks, and development verification scripts

**Bot Filtering Implementation:** Our server-side tracking implements explicit bot filtering logic to exclude non-human traffic:
- **User-Agent filtering:** Only accepts requests with browser-like User-Agent strings containing "Mozilla" and excludes known bot patterns (bot, spider, crawler, curl, python, uptime, httpclient)
- **Request method filtering:** Only GET requests trigger exposure logging (HEAD requests, commonly used by health checks, are ignored)
- **Navigation detection:** Checks for `Sec-Fetch-Mode: navigate` header (indicating top-level navigation) or appropriate `Accept: text/html` header
- **Fallback logic:** For older browsers or test environments without modern headers, falls back to User-Agent and Accept header analysis

**Filtering Limitations:** This filtering approach is intentionally conservative and may not catch all sophisticated bots or instructor-generated automated traffic. Some legitimate evaluation traffic may be filtered, while some sophisticated bots may pass through. The server-side `ABTestEvent` database remains the primary source of truth for analysis but should be interpreted with awareness that bot traffic may be present.

### Variant Performance Analysis

**Data Availability Note:** At the time of report writing, actual production traffic data may be limited. The following analysis methodology is based on the implemented tracking infrastructure. Actual results should be verified by running `python manage.py abtest_report` against the production database.

**Analysis Method:**
1. Query `ABTestEvent` records for experiment "button_label_kudos_vs_thanks" and endpoint "/218b7ae/"
2. Separate events by `event_type`: count "exposure" events and "conversion" events per variant ("kudos" vs "thanks")
3. Compute conversion rates: (conversions / exposures) × 100% for each variant
4. Compare conversion rates to determine which variant has higher engagement

**Statistical Significance Considerations:** The `abtest_report` management command includes an explicit warning if total exposures < 30, indicating insufficient sample size for statistical significance. **We do not claim statistical significance without adequate data.** Any observed differences in small samples should be interpreted as preliminary observations, not definitive conclusions.

**Sample Size Requirements:** For meaningful statistical analysis, ideally ≥100 exposures per variant are recommended. With smaller sample sizes (<30 total exposures), observed differences may be due to random variation rather than true variant performance differences.

---

## 5. Traffic Analysis & Results

### Google Analytics vs Server-Side Logging

**Google Analytics 4 (GA4):**
- **Purpose:** Real-time monitoring and validation
- **Events:** `ab_exposure` (fired on first exposure per session), `ab_button_click` (fired on button clicks)
- **Advantages:** Immediate visibility, visual dashboards, no database queries needed
- **Limitations:** Subject to ad blockers, JavaScript errors, client-side filtering, potential duplicate events

**Server-Side ABTestEvent Logging:**
- **Purpose:** Primary source of truth for analysis
- **Events:** `exposure` and `conversion` records in Django database
- **Advantages:** Reliable, queryable, bot-filtered, unaffected by client-side issues
- **Limitations:** Requires database access and query tools for analysis

**Complementary Usage:** GA4 provides quick validation that events are firing correctly in production. Server-side logs provide accurate, filtered data for statistical analysis. When discrepancies occur (e.g., GA4 shows higher counts due to bot traffic), server-side data takes precedence as the authoritative source.

### DebugView vs Production Traffic

During development, Django's `DEBUG=True` mode and local testing generate synthetic traffic that may not reflect real user behavior:
- **Test traffic:** Automated tests create controlled exposure/conversion scenarios
- **Development traffic:** Local server requests from team members testing features
- **Debug mode:** May expose additional diagnostic information not present in production

Production traffic on Render with `DEBUG=False` represents real user interactions:
- **Actual users:** Real newcomers, contributors, and course evaluators
- **Network conditions:** Real-world latency, connection quality, browser variations
- **Bot presence:** Actual bot traffic from crawlers and monitoring services

Analysis should focus on production `ABTestEvent` records, excluding any test or development data. The `abtest_report` command queries the production database and should be run against the live environment for accurate results.

### Final Variant Preference

**Current Status:** Final variant preference **cannot be definitively stated** at this time due to insufficient production traffic data. The analysis infrastructure is in place and functioning correctly, but actual traffic volumes and conversion patterns require observation over time to reach statistically meaningful conclusions.

**Determination Process:** When sufficient data is available (recommended: ≥30 exposures per variant for basic analysis, ideally ≥100 for statistical significance), run:

```bash
python manage.py abtest_report
```

This command will:
1. Query all `ABTestEvent` records for experiment "button_label_kudos_vs_thanks" and endpoint "/218b7ae/"
2. Calculate conversion rates (conversions / exposures × 100%) per variant
3. Identify the variant with higher conversion rate
4. Provide explicit warnings if sample size is insufficient for statistical significance

**Interpretation Guidelines:**
- **Higher conversion rate indicates preferred variant**, but only if sample size is sufficient
- **If rates are equal or within margin of error**, either variant may be acceptable, or the difference may be statistically insignificant
- **Small sample sizes (<30 exposures)** should not be used to draw definitive conclusions about variant preference
- **Bot traffic and instructor-generated evaluation traffic** may affect observed rates, so interpretation should account for these factors

**Conservative Statement:** Without sufficient production data and statistical validation, we **do not claim a definitive winner**. The infrastructure is designed to determine preference when adequate data is available.

---

## 6. Agile Process & Scrum Execution

### Sprint Documentation

Complete sprint documentation is available in `/docs/sprints/`:
- **Sprint 1:** Planning, Review, Retrospective
- **Sprint 2:** Planning, Review, Retrospective  
- **Sprint 3:** Planning, Review, Retrospective
- **Sprint 4:** Planning, Review, Retrospective

Each sprint document follows a consistent structure with planning (user stories, tasks, estimates), review (completed work, metrics, blockers), and retrospective (what went well, challenges, action items).

### Backlog Management

User stories were organized by sprint based on dependencies and priority:
- **Sprint 1:** Foundation (models, authentication, infrastructure)
- **Sprint 2:** Public-facing features (home page, category pages, post details)
- **Sprint 3:** Contributor workflows and admin tools
- **Sprint 4:** A/B testing, production deployment, final polish

Stories were estimated using a modified Fibonacci scale (1, 2, 3, 5, 8, 13 story points) and assigned to team members based on expertise and availability.

### Sprint Planning

Planning sessions involved:
1. **Story Selection:** Choosing user stories from backlog that fit sprint capacity
2. **Task Breakdown:** Decomposing stories into specific technical tasks
3. **Assignment:** Allocating tasks to team members (stormy-deer, adorable-crow, super-giraffe)
4. **Capacity Estimation:** Estimating velocity based on previous sprints

Sprint goals were clearly stated (e.g., "Establish the foundation for the Yale Newcomer Survival Guide" in Sprint 1), providing focus and alignment.

### Sprint Review

Review sessions documented:
- **Completed Work:** Stories finished, with story points and owners
- **Metrics:** Planned vs completed points, velocity, completion rate
- **Demo Highlights:** Key features demonstrated
- **Blockers:** Issues encountered and resolutions

Velocity tracking showed consistent delivery: Sprint 1 (18/20 points, 90%), Sprint 2 (20/22 points, 90.9%), Sprint 3 (23/25 points, 92.0%), Sprint 4 (24/24 points, 100%).

### Retrospectives

Retrospectives identified:
- **What Went Well:** Strong collaboration, solid technical foundation, successful deployments
- **Challenges:** Migration conflicts, environment variable configuration, A/B test deduplication complexity
- **Action Items:** Specific tasks with owners and due dates for process improvement

Key learnings included the importance of early infrastructure planning, the value of staging environments, and the complexity of A/B test event tracking.

### Velocity Tracking & Burndown

**Velocity Calculation:** Velocity was tracked by comparing planned vs completed story points per sprint. Velocity represents the number of story points actually completed in each sprint, while completion rate is calculated as (Completed / Planned) × 100%.

**Velocity Chart:** A velocity chart (`docs/velocity.png`) visualizes this progression using grouped bars (planned vs completed per sprint), generated via standalone script `scripts/velocity_chart.py`. The chart shows how planned estimates compared to actual delivery across all four sprints.

**Sprint Velocity Data:**
| Sprint | Planned | Completed | Velocity | Completion Rate |
|--------|---------|-----------|----------|-----------------|
| Sprint 1 | 20 | 18 | 18 | 90.0% |
| Sprint 2 | 22 | 20 | 20 | 90.9% |
| Sprint 3 | 25 | 23 | 23 | 92.0% |
| Sprint 4 | 24 | 24 | 24 | 100.0% |

**Analysis:** Average velocity: ~21 points per sprint. The team improved estimation accuracy over time, with Sprint 4 achieving 100% completion. Velocity tracking enabled better capacity planning in later sprints based on historical performance.

**Burndown Tracking:** While not explicitly visualized as a burndown chart, sprint reviews document progress toward sprint goals, and the velocity data shows consistent delivery patterns across sprints.

---

## 7. Testing & Code Quality

### Automated Tests

The codebase includes comprehensive automated tests using Django's test framework:

**Test Count:** 111+ tests across multiple test files:
- `test_abtest.py`: A/B test endpoint and variant assignment
- `test_abtest_session_dedupe.py`: Session-based deduplication logic
- `test_abtest_report_command.py`: Management command functionality
- `test_url_routing.py`: URL resolution and routing
- `test_post_model.py`: Post model functionality
- `test_category_model.py`: Category model functionality
- `test_bookmark_model.py`: Bookmark functionality
- `test_integration.py`: End-to-end user workflows
- Additional tests for forms, admin, and views

**Test Coverage:** >75% overall coverage, with 100% coverage on critical models. Coverage tooling configured via `pyproject.toml`.

**Test Execution:** All tests pass consistently. Tests run automatically in CI and can be executed locally via `python manage.py test`.

### Continuous Integration (CI)

**GitHub Actions CI Workflow:** Automated continuous integration is implemented via GitHub Actions workflow file (`.github/workflows/ci.yml`). The CI pipeline runs automatically on:
- Push events to `main` branch
- Pull request events targeting `main` branch

**CI Pipeline Steps:**
1. **Checkout:** Retrieve code from GitHub repository
2. **Python Setup:** Configure Python 3.9 environment
3. **Dependencies:** Install all packages from `requirements.txt` with pinned versions
4. **Linting:** Run `ruff check .` to enforce code quality standards
5. **Testing:** Execute `python manage.py test` using SQLite database (DATABASE_URL not set for CI)

**Environment Configuration:** CI uses test-safe environment variables (DEBUG=1, dummy SECRET_KEY) and SQLite database to ensure fast, reliable test execution without external dependencies.

**Benefits:** CI prevents broken code from being merged to main, catches linting errors early, and ensures all tests pass before code integration. This approach maintains code quality and reduces integration issues.

### Linting

**Ruff** is used for code linting, configured in `pyproject.toml`:
- Rules: E (errors), F (pyflakes)
- All files pass linting checks
- Auto-fixable issues addressed via `ruff check . --fix`

Linting catches unused imports, undefined names, and other code quality issues early in development.

### Django System Checks

Django's system check framework (`python manage.py check`) validates:
- Configuration correctness
- Model definitions
- URL patterns
- Middleware setup

All system checks pass, ensuring the application is properly configured for deployment.

---

## 8. Deployment & Operations

### Staging vs Production

**Staging Environment:**
- Purpose: Testing changes before production deployment
- URL: [TBD: staging URL on Render]
- Configuration: Same codebase as production, separate database instance
- Usage: QA testing, integration verification, safe experimentation

**Production Environment:**
- Purpose: Live application serving end users
- URL: [TBD: production URL on Render]
- Configuration: Stable, tested code only, production database
- Monitoring: Application logs, error tracking, performance monitoring

This environment separation allows safe testing of new features, database migrations, and configuration changes without impacting production users.

### Environment Variables

All configuration follows 12-factor app principles, using environment variables:

**Required Variables:**
- `DJANGO_SECRET_KEY`: Cryptographic signing key (must be set in production)
- `DATABASE_URL`: Database connection string (auto-provided by Render PostgreSQL)
- `DJANGO_ALLOWED_HOSTS`: Comma-separated list of allowed hostnames
- `DEBUG`: Debug mode flag (`False` in production)
- `GA_MEASUREMENT_ID`: Google Analytics measurement ID (defaults to `G-9XJWT2P5LE`)

**Local Development:** Safe defaults allow development without environment variables, but production requires explicit configuration for security.

**Render Configuration:** Environment variables set in Render dashboard, not committed to repository. `.gitignore` excludes `.env` files.

### Render Build/Start Commands

**Build Command:**
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

This installs dependencies, collects static files for WhiteNoise, and runs database migrations.

**Start Command:**
```bash
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Gunicorn serves the Django application, binding to the port provided by Render.

**Configuration:** `render.yaml` defines these commands, enabling infrastructure-as-code deployment.

### 12-Factor Principles Compliance

The application explicitly follows all 12-factor app methodology principles:

1. **Codebase:** Single codebase tracked in Git repository and deployed to multiple environments (local, staging, production) without divergence
2. **Dependencies:** Explicitly declared in `requirements.txt` with pinned versions (e.g., `Django==4.2.26`, `ruff==0.7.0`). No system-level dependencies are assumed
3. **Config:** All configuration stored in environment variables (`SECRET_KEY`, `DATABASE_URL`, `DEBUG`, `ALLOWED_HOSTS`, `GA_MEASUREMENT_ID`). No hardcoded secrets or environment-specific values in code
4. **Backing Services:** Database (PostgreSQL/SQLite) treated as attached resource via `DATABASE_URL` environment variable, using `dj-database-url` for connection management
5. **Build/Release/Run:** Strict separation: build installs dependencies and runs migrations, release is managed by Render, run executes via Gunicorn start command
6. **Processes:** Stateless application processes with no shared memory or filesystem state. Session data stored in database, static files served via WhiteNoise
7. **Port Binding:** Application binds to port provided by `$PORT` environment variable (Render automatically sets this). No hardcoded ports
8. **Concurrency:** Stateless process model supports horizontal scaling. Multiple Gunicorn workers can run simultaneously
9. **Disposability:** Fast startup (Django initialization completes in under 1 second), graceful shutdown (Gunicorn handles SIGTERM), minimal startup overhead
10. **Dev/Prod Parity:** Same codebase across all environments. Differences handled via environment variables (DEBUG, DATABASE_URL). Same Python version, same dependencies
11. **Logs:** All logging configured to write to stdout (via Django LOGGING configuration with StreamHandler). Render captures stdout as log streams
12. **Admin Processes:** Management commands (`python manage.py migrate`, `python manage.py abtest_report`) run as one-off processes, not as long-running services

**Verification:** Settings file (`config/settings.py`) explicitly loads all configuration from environment variables. `.gitignore` excludes `.env` files. No secrets are committed to the repository. Logging configuration writes to `StreamHandler` (stdout).

This 12-factor approach ensures the application is portable, scalable, and maintainable across different deployment environments while maintaining security and operational simplicity.

---

## 9. Project Retrospective

### What Went Well

1. **Strong Team Collaboration:** Daily standups, effective code reviews, and clear communication enabled parallel development and knowledge sharing. Team members (stormy-deer, adorable-crow, super-giraffe) worked effectively across different features.

2. **Solid Technical Foundation:** Django project structure established correctly from the start, with well-designed database schema requiring minimal refactoring. Early investment in testing infrastructure paid off throughout development.

3. **Successful Production Deployment:** Smooth deployment to Render with PostgreSQL, WhiteNoise for static files, and proper environment variable configuration. Staging environment enabled safe testing before production.

4. **A/B Testing Implementation:** Endpoint `/218b7ae/` was implemented correctly with proper variant assignment, session-based deduplication, and dual-tracking (server-side + GA4). Event tracking infrastructure provides reliable data for analysis.

5. **Comprehensive Documentation:** Sprint documents, README, and code comments provide clear guidance for future development and deployment.

### Challenges

1. **Migration Conflicts:** Multiple developers creating migrations simultaneously caused conflicts requiring careful resolution. **Resolution:** Established migration workflow (always pull before creating migrations) and documented process.

2. **A/B Test Event Deduplication:** Initial implementation logged duplicate exposures from page reloads. **Resolution:** Implemented session flag + database `get_or_create()` with uniqueness constraints, ensuring atomicity and preventing double-counting.

3. **Environment Variable Configuration:** Some confusion about which variables needed for staging vs production, and where to set them in Render. **Resolution:** Created environment variable checklist and documentation.

4. **Cache Control for A/B Tests:** Variant assignment getting cached by browsers/CDNs, causing users to see same variant repeatedly. **Resolution:** Added `@never_cache` decorator and explicit cache-control headers to prevent caching.

5. **Infrastructure vs Feature Balance:** More time allocated to deployment and infrastructure setup than originally planned, leaving less time for UX polish. **Learning:** Infrastructure work deserves explicit story points in sprint planning.

### Lessons Learned

1. **12-Factor Principles Implementation:** Environment-based configuration makes deployment significantly easier and more secure. Having no secrets in code improves security posture and simplifies environment management. Explicitly following all 12 principles from the start would have prevented configuration confusion later.

2. **Dual-Tracking Analytics Architecture:** Server-side tracking provides reliable data unaffected by ad blockers, while client-side GA4 provides immediate visibility. Both approaches have value and complement each other. Relying on server-side data as source of truth while using GA4 for validation is an effective pattern.

3. **Staging Environment Value:** Separate staging environment is invaluable for testing database migrations, configuration changes, and new features before production exposure. Staging catches issues that would otherwise impact production users.

4. **Session-Based State Management:** Django sessions provide reliable mechanism for user state management, but require careful consideration of caching and deduplication for analytics use cases. Session flags combined with database uniqueness constraints ensure accurate event tracking.

5. **A/B Test Event Deduplication Complexity:** Implementing accurate exposure deduplication requires both session-level and database-level checks. The combination of session flags and `get_or_create()` with uniqueness constraints provides atomicity and prevents race conditions.

6. **AI-Assisted Development Balance:** Tools like Cursor accelerated boilerplate code generation and documentation, but critical decisions (production configuration, hash verification, analytics validation) required human judgment and testing. AI tools are accelerators, not replacements for careful engineering.

### What Would Be Done Differently

1. **Start A/B Testing Earlier:** Begin planning A/B testing infrastructure in Sprint 2 instead of Sprint 3, allowing more time for data collection and analysis before project completion.

2. **Establish Infrastructure Checklists Earlier:** Create deployment and environment variable checklists in Sprint 1, preventing configuration confusion that occurred later.

3. **Allocate More Time for Infrastructure:** Explicitly estimate story points for deployment and configuration tasks rather than treating them as "overhead." Infrastructure work is essential and deserves proper estimation.

4. **Improve Test Coverage Earlier:** Aim for 80%+ coverage from Sprint 1, writing tests alongside features rather than after. Higher early coverage would have caught edge cases sooner.

5. **Document as We Go:** Update README and documentation immediately when making configuration changes, rather than waiting until end of sprint. This prevents knowledge loss and reduces documentation debt.

---

## 10. Team Contributions

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
- CI/CD workflow configuration

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

Per course policy, all team members share equal responsibility for project outcomes and grading. While individual contributions are listed above, the project represents collaborative effort with code reviews, pair programming, and shared decision-making throughout all four sprints.

---

## Conclusion

The Yale Newcomer Survival Guide successfully delivers a functional MVP that addresses a real need within the Yale community. The application demonstrates solid software engineering practices: comprehensive testing, 12-factor app compliance, proper deployment procedures, and data-driven experimentation via A/B testing.

The project highlights the importance of infrastructure planning, the value of staging environments, and the complexity of accurate analytics tracking. While challenges were encountered (migration conflicts, event deduplication, configuration management), they were resolved through systematic problem-solving and team collaboration.

The A/B testing infrastructure is in place and functioning correctly, though final variant preference requires sufficient production traffic data for statistical significance. The dual-tracking approach (server-side + GA4) provides both reliability and real-time visibility.

**Team far-storm (stormy-deer, adorable-crow, super-giraffe) - Project Complete.**

---

*Report generated: December 2024*  
*Sprint documentation available in `/docs/sprints/`*  
*Velocity chart: `/docs/velocity.png`*  
*A/B test analysis: `python manage.py abtest_report`*
