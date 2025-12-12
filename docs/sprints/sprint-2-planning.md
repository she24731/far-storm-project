# Sprint 2 Planning

**Team:** far-storm  
**Sprint Duration:** [TBD: dates]  
**Team Members:** stormy-deer, adorable-crow, super-giraffe

## Sprint Goal

Build the public-facing user interface for the Yale Newcomer Survival Guide. Implement home page, category listings, post detail pages, and contributor dashboard for managing posts.

## User Stories

### Story 1: Public Home Page
- **As a** visitor  
- **I want** to see a welcoming home page with featured content  
- **So that** I can quickly understand what the site offers

**Acceptance Criteria:**
- Home page displays recent approved posts
- Category navigation visible
- Search functionality accessible
- Responsive design using Bootstrap

**Story Points:** 5  
**Owner:** adorable-crow

### Story 2: Category Listing Pages
- **As a** user  
- **I want** to browse posts by category  
- **So that** I can find relevant information quickly

**Acceptance Criteria:**
- Category list page shows all categories
- Category detail page shows posts in that category
- Posts filtered by status (only approved)
- Pagination for large lists

**Story Points:** 5  
**Owner:** super-giraffe

### Story 3: Post Detail Pages
- **As a** reader  
- **I want** to view full post content  
- **So that** I can read complete articles

**Acceptance Criteria:**
- Post detail page displays full content
- Shows author, publication date, category
- Related posts suggested
- Bookmark functionality available

**Story Points:** 8  
**Owner:** stormy-deer

### Story 4: Contributor Dashboard
- **As a** contributor  
- **I want** a dashboard to manage my posts  
- **So that** I can track and edit my submissions

**Acceptance Criteria:**
- Dashboard shows user's posts by status
- Can create new posts
- Can edit draft/pending posts
- Can view post status and feedback

**Story Points:** 8  
**Owner:** adorable-crow

## Tasks Breakdown

1. **Home Page Template** (adorable-crow)
   - Create home.html template
   - Implement recent posts query
   - Add Bootstrap styling
   - Add search form

2. **Category Views** (super-giraffe)
   - Create category_list view
   - Create category_detail view
   - Implement post filtering
   - Add pagination

3. **Post Detail View** (stormy-deer)
   - Create post_detail view
   - Implement related posts logic
   - Add bookmark button
   - Style with Bootstrap

4. **Contributor Dashboard** (adorable-crow)
   - Create dashboard view
   - Filter posts by user and status
   - Add create/edit post links
   - Display status badges

5. **URL Routing** (super-giraffe)
   - Configure URL patterns
   - Add URL names for reverse lookup
   - Test all routes

6. **Testing** (all)
   - Write view tests
   - Test template rendering
   - Test user permissions

## Sprint Capacity

- **Total Story Points:** 26
- **Team Velocity (estimated):** 22 points (based on Sprint 1)
- **Sprint Commitment:** 26 points (stretch goal)

## Dependencies

- Sprint 1 models and authentication complete
- Bootstrap CSS framework
- Template inheritance structure

## Risks and Mitigation

- **Risk:** Complex template inheritance  
  **Mitigation:** Establish base template early, document structure

- **Risk:** Pagination performance  
  **Mitigation:** Use Django's built-in pagination, test with large datasets

## Definition of Done

- [ ] Code reviewed by at least one team member
- [ ] All tests passing (`python manage.py test`)
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Templates render correctly
- [ ] No critical bugs
- [ ] Documentation updated

