## ***1\. Sprint Summary***

***Sprint Goal:***  
 *Deliver a working staging deployment of the Yale Newcomer Survival Guide with core user flows functional—login, browse, submit posts, and basic admin review. The sprint focused on stabilizing the MVP skeleton built in Sprint 1, ensuring every essential component runs reliably in a shared environment.*

***Achievement:***  
 *Yes. The team successfully deployed the MVP to staging, verified working authentication, category browsing, and post submission with role-based access. Minor stretch items (UI refinements, early search) were moved to Sprint 3\.*

***Why this sprint matters:***  
 *This sprint delivered the first fully functional staging environment, enabling real testing, contributor workflows, and laying the foundation for site-wide search and content publishing in Sprint 3\.*

## ***2\. Deployment***

***Staging Link:***

* Yale Newcomer Survival Guide *[https://yale-newcomer-survival-guide.onrender.com/](https://yale-newcomer-survival-guide.onrender.com/)*   
* Repository  *[https://github.com/she24731/far-storm-project](https://github.com/she24731/far-storm-project)*   
* Github Project *[https://github.com/users/she24731/projects/6](https://github.com/users/she24731/projects/6)* 

***What’s working on staging:***

* *Login/logout with role-based permissions (Reader / Contributor / Admin)*

* *Category Hub displaying seeded content*

* *Post model and basic creation flow*

* *Admin dashboard functional for reviewing submissions*  
  * Account: admin  
  * Password: admin123456

* *Deployment verified by all team members*

* *Auto-deploy pipeline stable after configuration fixes*

*Screenshot: Staging home page (insert screenshot)*

## ***3\. Completed Work***

### ***Auth & Roles***

* *Verified Django roles and permissions*

* *Login/logout views functioning on staging*

* *Role-based access mapped properly*

  ### ***Categories***

* *Category Hub fully functional*

* *Seeded posts display by category*

  ### ***Content***

* *Post model stable with status field*

* *Submission flow confirmed on staging*

  ### ***Deployment Work***

* *Environment configuration corrected*

* *Database seed validated*

* *Full team testing conducted*

***All planned Sprint 2 user stories for MVP readiness were completed.***

***4\. Metrics***

| *Metric* | *Value* |
| :---- | ----- |
| ***Planned Story Points*** | *26* |
| ***Completed Story Points*** | *26* |
| ***Velocity*** | *26 SP* |
| ***Completion Rate*** | *100%* |

## ***5\. Sprint Retrospective Highlights***

### ***What Went Well***

1. ***Deployment Pipeline Stabilized***

   * *Resolved blockers; staging environment reliable*

   * *Configurations clarified across team*

2. ***Core MVP Functional on Staging***

   * *Auth, categories, and content all behave as expected*

   * *Role-based access validated*

3. ***Improved Team Coordination***

   * *Clear responsibility split*

   * *Faster decision-making despite short sprint*  
4. ***Code quality***  
   * Leveraging version control practices \- Render is configured to deploy automatically from GitHub.  
     * Every code update → pushed to GitHub  
     * Render detects new commit → deploys automatically  
     * My production server always matches my GitHub codebase

   ### ***What Didn’t Go Well***

1. ***Initial Deployment Delays***

   * *Required multiple rounds of debugging*

   * *Environment inconsistencies caused slowdowns*

2. ***Database Stability Issues***

   * *Seeded data required cleanup*

   * *Time spent validating model behaviors*

3. ***Limited Capacity for Stretch Items***

   * *UI refinements postponed*

   * *Search prototype moved to Sprint 3*

   ### ***What to Improve***

1. ***Standardize Deployment Workflow***

   * *Action: Document setup, deployment, rollback commands*

   * *Assignee: Denise*

   * *Due Date: Nov 18, 2025*

2. ***Increase Pre-Deployment Testing***

   * *Action: Introduce verification checklist (DB seed, admin panel, model checks)*

   * *Assignee: Celine*

   * *Due Date: Nov 18, 2025*

3. ***Improve Environment Consistency***

   * *Action: Align local and staging settings*

   * *Assignee: Yay*

   * *Due Date: Nov 19, 2025*

   ## ***6\. Sprint 3 Preview***

*Sprint 3 will deliver the **fully interactive MVP**, including:*

* *Site-wide search endpoint \+ template*

* *External links support*

* *Contributor submit/edit form with Markdown/TinyMCE*

* *Admin pending queue \+ audit trail*

* *Email/flash notifications*

* *Styling consistency via Bootstrap*

* ***27 committed story points***

*By the end of Sprint 3, users should be able to:*  
 *✓ Log in*  
 *✓ Create and edit posts*  
 *✓ Submit for review*  
 *✓ See approved content*  
 *✓ Search across categories, titles, and keywords*

