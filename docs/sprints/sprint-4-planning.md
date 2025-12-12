# Sprint 4 Planning

**Team:** far-storm  
**Sprint Duration:** 2 weeks  
**Dates:** [TBD: dates]  
**Team Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)

## Sprint Goal

Complete MVP with A/B testing endpoint, analytics integration, production deployment, and final polish. Ensure 12-factor compliance, comprehensive testing, and complete documentation for final submission.

## User Stories

### Story 1: A/B Test Endpoint Implementation
- **As a** developer  
- **I want** an A/B test endpoint at `/218b7ae/`  
- **So that** we can test button label variants

**Acceptance Criteria:**
- Endpoint at first 7 characters of SHA1("far-storm") = `/218b7ae/`
- Displays team nickname "far-storm" and all team members
- Button with `id="abtest"` showing either "kudos" or "thanks"
- 50/50 random variant assignment persisted via session cookie
- Publicly accessible (no authentication required)

**Story Points:** 5  
**Owner:** stormy-deer

### Story 2: Server-Side A/B Test Event Tracking
- **As a** developer  
- **I want** server-side event tracking for A/B test  
- **So that** we have reliable analytics data

**Acceptance Criteria:**
- `ABTestEvent` model created with exposure and conversion event types
- Exposure logged on first page load per session
- Conversion logged on button click
- Session-based deduplication prevents double-counting
- Bot filtering implemented

**Story Points:** 5  
**Owner:** stormy-deer

### Story 3: Google Analytics 4 Integration
- **As a** developer  
- **I want** GA4 integration for A/B test events  
- **So that** we have real-time analytics visibility

**Acceptance Criteria:**
- GA4 measurement ID (G-9XJWT2P5LE) configured
- Context processor for GA4 in templates
- `ab_exposure` event fired on first exposure
- `ab_button_click` event fired on button click
- Single GA tag in base.html, no duplicates

**Story Points:** 3  
**Owner:** stormy-deer

### Story 4: Production Deployment on Render
- **As a** developer  
- **I want** production deployment on Render  
- **So that** the application is publicly accessible

**Acceptance Criteria:**
- Render service configured with PostgreSQL
- `DATABASE_URL` environment variable working
- WhiteNoise serving static files correctly
- `ALLOWED_HOSTS` includes Render URL
- Build and start commands working
- Health checks passing

**Story Points:** 5  
**Owner:** stormy-deer

### Story 5: 12-Factor Compliance Audit
- **As a** developer  
- **I want** 12-factor app compliance verified  
- **So that** the application follows best practices

**Acceptance Criteria:**
- All configuration via environment variables
- No hardcoded secrets
- Logging to stdout
- Database as attached resource
- Static files served correctly
- Documentation updated

**Story Points:** 3  
**Owner:** stormy-deer

### Story 6: Comprehensive Testing and CI/CD
- **As a** developer  
- **I want** comprehensive tests and CI/CD pipeline  
- **So that** code quality is maintained

**Acceptance Criteria:**
- Test coverage >75% overall
- GitHub Actions CI configured
- Tests run on push and pull requests
- Ruff linting in CI pipeline
- All tests passing

**Story Points:** 3  
**Owner:** stormy-deer

## Tasks Breakdown

1. **A/B Test Endpoint** (stormy-deer)
   - Create view for `/218b7ae/` endpoint
   - Implement variant assignment logic (50/50 split)
   - Session persistence for variant
   - Create template with team info and button
   - Test variant consistency

2. **ABTestEvent Model** (stormy-deer)
   - Design and create ABTestEvent model
   - Implement exposure logging logic
   - Implement conversion logging logic
   - Session-based deduplication
   - Bot filtering implementation

3. **GA4 Integration** (stormy-deer)
   - Configure GA4 measurement ID in settings
   - Create context processor for GA4
   - Add GA tag to base.html
   - Implement ab_exposure event
   - Implement ab_button_click event

4. **Render Deployment** (stormy-deer)
   - Configure Render service
   - Set up PostgreSQL database
   - Configure environment variables
   - Set build and start commands
   - Test deployment

5. **12-Factor Audit** (stormy-deer)
   - Audit settings.py for environment variables
   - Verify no hardcoded secrets
   - Configure logging to stdout
   - Verify static files configuration
   - Update documentation

6. **CI/CD Setup** (stormy-deer)
   - Configure GitHub Actions workflow
   - Set up test execution in CI
   - Add linting to CI pipeline
   - Test CI pipeline
   - Document CI process

7. **Testing** (all)
   - Write tests for A/B test endpoint
   - Write tests for event tracking
   - Write tests for GA4 integration
   - Verify test coverage
   - Write deployment tests

8. **Documentation** (all)
   - Update README with deployment info
   - Document A/B test endpoint
   - Document analytics setup
   - Complete final report
   - Ensure all documentation current

## Sprint Capacity

- **Total Story Points:** 24
- **Team Velocity (estimated):** 24 points (based on Sprint 3)
- **Sprint Commitment:** 24 points

## Dependencies

- All previous sprint features complete
- Render account setup
- GA4 account with measurement ID
- GitHub repository ready for CI

## Risks and Mitigation

- **Risk:** A/B test event tracking complexity  
  **Mitigation:** Start with simple implementation, iterate based on testing

- **Risk:** Deployment configuration issues  
  **Mitigation:** Test deployment early, have staging environment ready

- **Risk:** GA4 integration complexity  
  **Mitigation:** Use standard GA4 implementation patterns

- **Risk:** Time pressure for final submission  
  **Mitigation:** Prioritize critical features, defer non-essential polish

## Definition of Done

- [ ] Code reviewed by at least one team member
- [ ] All tests passing (`python manage.py test`)
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Test coverage >75%
- [ ] CI/CD pipeline working
- [ ] Production deployment successful
- [ ] 12-factor compliance verified
- [ ] Documentation complete
- [ ] Changes merged to main branch
