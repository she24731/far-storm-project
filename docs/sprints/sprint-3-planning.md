# Sprint 3 Planning

**Team:** far-storm  
**Sprint Duration:** 2 weeks  
**Dates:** [TBD: dates]  
**Team Members:** stormy-deer (Chun-Hung Yeh), adorable-crow (Celine Li), super-giraffe (Denise Wu)

## Sprint Goal

Implement contributor workflows for post creation and management, and build admin moderation tools. Enable contributors to submit and edit posts, and provide admins with efficient content review and approval workflows.

## User Stories

### Story 1: Contributor Post Submission
- **As a** contributor  
- **I want** to create and submit posts for review  
- **So that** I can share knowledge with the community

**Acceptance Criteria:**
- Post creation form with title, content, category selection
- Save as draft functionality
- Submit for review (status → pending)
- Auto-generated slugs from titles
- Validation and error handling
- Accessible only to contributors

**Story Points:** 5  
**Owner:** adorable-crow

### Story 2: Contributor Post Management Dashboard
- **As a** contributor  
- **I want** to view and manage my posts  
- **So that** I can track their status and edit them

**Acceptance Criteria:**
- Contributor dashboard showing all user's posts
- Post list filtered by status (draft, pending, approved, rejected)
- Edit functionality for draft and rejected posts
- View read-only details for pending and approved posts
- Status indicators and timestamps visible

**Story Points:** 5  
**Owner:** adorable-crow

### Story 3: Admin Moderation Dashboard
- **As an** admin  
- **I want** a dashboard to review pending posts  
- **So that** I can efficiently moderate content

**Acceptance Criteria:**
- Admin dashboard showing all pending posts
- Post details displayed (title, content, author, category)
- Approve action sets status to approved and sets published_at
- Reject action sets status to rejected
- Clear indication of moderation queue status

**Story Points:** 8  
**Owner:** super-giraffe

### Story 4: Post Editing Workflow
- **As a** contributor  
- **I want** to edit my draft and rejected posts  
- **So that** I can improve content before resubmission

**Acceptance Criteria:**
- Edit view for posts owned by contributor
- Only draft and rejected posts editable
- Pending and approved posts read-only
- Form pre-populated with existing data
- Slug regeneration on title change if needed

**Story Points:** 5  
**Owner:** adorable-crow

### Story 5: Template Organization Refactoring
- **As a** developer  
- **I want** better organized templates  
- **So that** maintenance is easier

**Acceptance Criteria:**
- Extract reusable template components
- Reduce duplication in templates
- Better organization of template files
- Maintained functionality after refactoring

**Story Points:** 2  
**Owner:** adorable-crow

## Tasks Breakdown

1. **Post Submission Form and View** (adorable-crow)
   - Create post submission form with all required fields
   - Implement save as draft functionality
   - Implement submit for review functionality
   - Add form validation and error handling
   - Create submission template

2. **Contributor Dashboard** (adorable-crow)
   - Create contributor dashboard view
   - Query user's posts filtered by status
   - Create dashboard template with post list
   - Add status indicators and navigation

3. **Admin Moderation Dashboard** (super-giraffe)
   - Create admin dashboard view
   - Query all pending posts
   - Create moderation template
   - Display post details for review

4. **Approve/Reject Actions** (super-giraffe)
   - Implement approve action (sets status, published_at)
   - Implement reject action (sets status)
   - Add confirmation messages
   - Update post workflow logic

5. **Post Editing** (adorable-crow)
   - Create post edit view with access control
   - Pre-populate form with existing data
   - Handle slug regeneration on title changes
   - Ensure only editable posts can be edited

6. **Template Refactoring** (adorable-crow)
   - Extract common template components
   - Organize template files better
   - Reduce duplication
   - Test all templates still work

7. **Testing** (all)
   - Write tests for post submission
   - Write tests for contributor dashboard
   - Write tests for admin moderation
   - Write tests for access control

## Sprint Capacity

- **Total Story Points:** 25
- **Team Velocity (estimated):** 22 points (based on Sprint 2)
- **Sprint Commitment:** 23 points

## Dependencies

- Sprint 2 public UI complete
- User authentication and roles working
- Post model with status workflow in place

## Risks and Mitigation

- **Risk:** Complex workflow logic for post status transitions  
  **Mitigation:** Document workflow states clearly, test thoroughly

- **Risk:** Access control complexity in editing  
  **Mitigation:** Use decorators consistently, comprehensive testing

- **Risk:** Template refactoring breaking existing pages  
  **Mitigation:** Refactor incrementally, test each change

- **Risk:** Admin dashboard performance with many pending posts  
  **Mitigation:** Implement pagination if needed, optimize queries

## Definition of Done

- [ ] Code reviewed by at least one team member
- [ ] All tests passing (`python manage.py test`)
- [ ] Ruff linting passes (`ruff check .`)
- [ ] Access control verified for all views
- [ ] Workflow logic tested (all status transitions)
- [ ] Documentation updated
- [ ] Changes merged to main branch
