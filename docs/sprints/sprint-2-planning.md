# Sprint 2 Planning

**Team:** far-storm  
**Sprint Duration:** 2 weeks  
**Dates:** [TBD: dates]  
**Team Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)

## Sprint Goal

Build the public-facing user interface and content discovery features. Implement home page, category listings, post detail pages, and search functionality to enable newcomers to browse and find relevant information.

## User Stories

### Story 1: Home Page and Category Hub
- **As a** newcomer  
- **I want** to see a home page with category navigation and latest posts  
- **So that** I can quickly discover relevant information

**Acceptance Criteria:**
- Home page displays all available categories with links
- Latest approved posts shown on home page (limited number)
- Clean, responsive design using Bootstrap 5
- Category icons and descriptions visible

**Story Points:** 5  
**Owner:** adorable-crow

### Story 2: Category Listing Pages
- **As a** user  
- **I want** to browse posts by category  
- **So that** I can find relevant information quickly

**Acceptance Criteria:**
- Category detail page shows all approved posts in that category
- Pagination implemented for categories with many posts
- Posts displayed with title, summary, and publication date
- Only approved posts visible to non-authenticated users

**Story Points:** 5  
**Owner:** super-giraffe

### Story 3: Post Detail Pages
- **As a** user  
- **I want** to view full post content  
- **So that** I can read complete information about a topic

**Acceptance Criteria:**
- Post detail page displays full content
- Post metadata shown (author, category, published date)
- Navigation back to category or home
- Status-based access control (only approved posts public)
- Responsive layout for different screen sizes

**Story Points:** 5  
**Owner:** super-giraffe

### Story 4: Search Functionality
- **As a** user  
- **I want** to search across all posts  
- **So that** I can find information by keywords

**Acceptance Criteria:**
- Search form on home page and navigation
- Search queries post titles and content
- Results page displays matching posts
- Search results show category and summary
- Only approved posts included in search

**Story Points:** 5  
**Owner:** stormy-deer

### Story 5: Template Architecture and Bootstrap Integration
- **As a** developer  
- **I want** a consistent template structure with Bootstrap styling  
- **So that** the UI is responsive and maintainable

**Acceptance Criteria:**
- Base template with navigation and footer
- Bootstrap 5 integrated and configured
- Responsive navigation menu
- Consistent styling across all pages
- Custom CSS for project-specific styling

**Story Points:** 2  
**Owner:** adorable-crow

## Tasks Breakdown

1. **Home Page View and Template** (adorable-crow)
   - Create home view that queries categories and latest posts
   - Design home page template with category grid
   - Display latest approved posts section
   - Add Bootstrap styling and responsive layout

2. **Category Listing Views** (super-giraffe)
   - Create category detail view with post listing
   - Implement pagination for post lists
   - Create category template with post cards
   - Filter to show only approved posts

3. **Post Detail View** (super-giraffe)
   - Create post detail view with proper access control
   - Design post detail template
   - Add navigation breadcrumbs
   - Implement status-based visibility logic

4. **Search Implementation** (stormy-deer)
   - Create search view with query processing
   - Implement search across post titles and content
   - Create search results template
   - Add search form to navigation

5. **Template Architecture** (adorable-crow)
   - Create base.html with Bootstrap navigation
   - Set up template inheritance structure
   - Add custom CSS file
   - Ensure responsive design principles

6. **Testing** (all)
   - Write tests for home page view
   - Write tests for category listing
   - Write tests for post detail access control
   - Write tests for search functionality

## Sprint Capacity

- **Total Story Points:** 22
- **Team Velocity (estimated):** 20 points (based on Sprint 1)
- **Sprint Commitment:** 20 points

## Dependencies

- Sprint 1 foundation complete (models, authentication)
- Bootstrap 5 CSS framework
- Template inheritance structure

## Risks and Mitigation

- **Risk:** UI/UX design inconsistencies  
  **Mitigation:** Establish base template early, review designs together

- **Risk:** Performance issues with large post lists  
  **Mitigation:** Implement pagination from the start, optimize queries

- **Risk:** Search implementation complexity  
  **Mitigation:** Start with simple Django ORM search, can enhance later

- **Risk:** Access control bugs exposing draft posts  
  **Mitigation:** Comprehensive testing of status-based filtering

## Definition of Done

- [ ] Code reviewed by at least one team member
- [ ] All tests passing (`python manage.py test`)
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Responsive design tested on multiple screen sizes
- [ ] Access control verified (no draft posts visible publicly)
- [ ] Documentation updated
- [ ] Changes merged to main branch
