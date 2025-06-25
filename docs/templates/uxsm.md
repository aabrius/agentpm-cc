Perfeito. Vou criar um template estático em Markdown para o documento de Mapa do Site (UX Site Map Document), com conteúdo de exemplo em cada seção para ilustrar como preenchê-lo. Será voltado para equipes internas de produto, engenharia e UX trabalhando em ferramentas internas, como dashboards administrativos ou portais internos. Já volto com o documento pronto.


# Employee Performance Dashboard – UX Site Map Document

## Title Page

*Project/Tool name, version, date, author, department.*

* **Project/Tool Name:** Employee Performance Dashboard
* **Version:** 1.0
* **Date:** June 23, 2025
* **Author:** Jane Doe (UX Designer)
* **Department:** Human Resources (HR) & Internal Tools Team

## Document Purpose

*What is the purpose of this site map? What internal tool, dashboard, or workflow does it represent?*

This document provides a comprehensive UX site map for the **Employee Performance Dashboard**, an internal web tool used by the company’s HR team and people managers to track, evaluate, and improve employee performance. The site map outlines the structure of the dashboard – detailing its sections, pages, and navigation flows – to serve as a blueprint for design and development. By clearly mapping out the tool’s information architecture, this document ensures that all stakeholders have a shared understanding of how the dashboard is organized and how it supports key HR workflows (like performance reviews, goal tracking, and feedback collection).

## Stakeholders & Internal Users

*Who are the main user groups? What are their roles, needs, and key tasks?*

The primary users of the Employee Performance Dashboard are internal stakeholders with distinct roles and needs:

* **HR Administrators (People Operations Team):** Responsible for overseeing company-wide performance management. They need to configure review cycles, monitor completion of performance reviews across departments, and access high-level reports. Key tasks include setting up performance review templates, checking that managers complete reviews on time, and analyzing overall performance metrics.
* **Team Managers (Department Heads & Line Managers):** Responsible for managing the performance of their direct reports. They need to review individual employee goals, provide feedback, and complete performance evaluations. Key tasks include initiating and writing performance reviews, approving employee-set goals, and monitoring team performance dashboards to identify high and low performers.
* **Individual Employees:** All staff members who receive performance evaluations. They need to track their own goals, review feedback from managers, and view their performance review results. Key tasks include updating personal goals, requesting feedback or one-on-one meetings, and reviewing their performance review summaries or scores.
* **Executives (Optional, Read-only):** Senior leaders who might not input data but need insight into performance trends. They require access to summary dashboards or reports to inform strategic decisions. Key tasks include viewing company-wide performance dashboards and drilling down into departmental performance data if needed.

*(Each user group above will use the site map differently: for example, HR admins navigate across all sections, whereas an individual employee will primarily use their own performance pages.)*

## Scope & Context

*What features, pages, or processes are included in this site map? What is out of scope?*

This site map focuses on the **Employee Performance Dashboard** web application and covers all major features related to performance management within the organization. It defines the content structure and navigation for the tool’s key components. The scope includes:

* **Goal Management:** Pages for employees to set personal goals and for managers to review/approve those goals.
* **Performance Reviews:** Screens for the annual/semi-annual review process, including self-reviews, manager reviews, and HR final approvals.
* **Feedback & Coaching:** Sections where managers and peers can give ongoing feedback, and employees can view or request feedback.
* **Team Overview & Reports:** Manager-facing pages that summarize team performance metrics, and an HR analytics section for organization-wide reporting.
* **Administrative Settings:** HR admin pages to configure performance cycles, manage evaluation forms, and adjust user permissions.

**Out of Scope:** This site map does *not* cover unrelated HR systems or features outside performance management. For example, it does not include pages for payroll, recruiting, or training & development (those are handled by separate internal tools). Additionally, any external mobile app interface is out of scope – the focus here is solely on the internal web dashboard. Integration points to other systems (e.g., HRIS data feeds) are noted, but the detailed functionality of external systems is not depicted in this site map.

## Site Map Overview

*Provide a high-level summary of the site map and how it supports user workflows.*

At a high level, the Employee Performance Dashboard is organized into three main areas to support different user workflows: **Personal Performance** (for individual employees), **Team Management** (for managers), and **HR Administration** (for HR staff). Upon logging in, users land on a customizable **Dashboard Home** that provides a summary of relevant information (e.g., pending tasks like “Complete your self-review” for employees or “3 reviews awaiting your approval” for managers).

The site map is designed to mirror the typical workflow of performance management:

* An **employee** can navigate from their Dashboard to update **Goals**, review their **Feedback**, and check their **Performance Review** results.
* A **manager** can move from the Dashboard into **Team Performance** pages – first seeing a **Team Overview** and then drilling down into individual **Employee Profile** pages to record feedback or start a review.
* **HR administrators** have access to an **Admin** section where they can manage the overall process (like setting up review cycles and viewing company-wide metrics).

This structure ensures each user easily finds the tools they need: employees focus on their own performance, managers handle their team’s evaluations, and HR oversees the entire program. The clear separation of sections prevents confusion while still allowing quick cross-navigation (e.g., a manager who is also an employee can switch between their personal goals and their team’s data seamlessly).

## Hierarchical Structure

*Diagram or outline the main sections, pages, screens, and sub-pages. Use a tree or indented list format.*

Below is the hierarchical outline of the Employee Performance Dashboard’s content structure. Top-level sections are listed with their primary pages and sub-pages indented beneath them:

* **Dashboard Home** – Overview with personalized widgets and alerts (e.g., tasks due, summary of performance indicators).
* **My Performance** (Employee section)

  * **My Goals** – View and update personal performance goals.
  * **My Feedback** – View feedback received from managers or peers; request new feedback.
  * **My Reviews** – Access past performance review results and upcoming review forms (self-review input when active).
* **Team Performance** (Manager section)

  * **Team Overview** – Summary of team’s performance status (overall goals progress, pending reviews).
  * **Team Members** – List of direct reports; selecting a specific employee opens their profile:

    * **Employee Profile** – Detailed view of an individual employee’s goals, feedback, and past reviews; includes action buttons (e.g., “Give Feedback”, “Start Review”).
  * **Team Reviews** – Manager’s queue of performance reviews to complete for direct reports (with links to each employee’s review form).
* **Reports & Analytics** (Manager & HR section)

  * **Team Reports** – (Managers) Charts and tables summarizing performance ratings, goal completion rates, etc., for the manager’s team.
  * **Company Reports** – (HR) High-level analytics for HR, including cross-department performance comparisons and trends.
* **HR Administration** (HR Admin section)

  * **Review Cycle Management** – Set up and edit performance review cycles (e.g., configure self-review and manager review deadlines, evaluation questions).
  * **Goal Library & Calibration** – Manage a library of standard goals or competencies; calibrate performance ratings across departments.
  * **Employee Directory** – Browse all employee profiles (read-only view similar to Employee Profile, but accessible for HR across the organization).
  * **Permissions & Roles** – Manage user roles and access rights (ensure managers have correct team assignments, etc.).
* **Help & Documentation** – User guides, FAQs, and support contact information for using the dashboard.

*(Note: The above structure is hierarchical. For instance, **Team Members** isn’t a clickable page itself but represents an expandable list in the Team Overview page; each **Employee Profile** is a separate page. Similarly, **Reports & Analytics** contains different views for managers vs. HR based on permissions.)*

## Page/Screen Descriptions

*For each section/page, briefly describe its purpose, key content or actions, and its role in user workflows.*

* **Dashboard Home:** Serves as the landing page after login. It provides a snapshot of important information and tasks: pending performance reviews, upcoming goal deadlines, recent feedback received, and key performance indicators. This page helps users quickly identify what actions they need to take (e.g., a “Complete your Q3 self-review” link or a “3 team goals need updates” alert for managers).
* **My Goals:** Allows an individual employee to create, view, and update their personal performance goals. Key elements on this page include a list of current goals (with progress indicators and due dates) and an option to add new goals. This page supports the workflow of continuous goal management, enabling employees to keep their objectives up to date and aligned with company targets. Managers can view this page for their direct reports (in read-only mode via the Employee Profile).
* **My Feedback:** Displays feedback entries that the employee has received. This can include notes from one-on-one meetings, peer feedback, or recognition badges. The page might also allow the employee to request feedback from a manager or colleague. By consolidating feedback, this page encourages a culture of continuous improvement and keeps employees informed about how they are doing throughout the year.
* **My Reviews:** Lists the employee’s performance reviews (past and current). For ongoing review cycles, it provides access to the self-review form (when applicable) and shows the status of the manager’s review or HR approval. For past cycles, it shows the final ratings and summarized comments. This page ensures employees have a record of their performance evaluations and can prepare for upcoming reviews.
* **Team Overview:** *(Managers only)* Provides a high-level dashboard of the manager’s team. Key content includes aggregate goal progress (e.g., “75% of team goals on track”), distribution of performance ratings in the last cycle for that team, and alerts (such as “2 team members have no goals set”). This overview helps managers quickly assess team performance and identify areas needing attention.
* **Employee Profile:** *(Managers & HR)* A detailed page for each employee that managers can access for their direct reports (and HR for any employee). It combines the individual’s goals, feedback, and review history on one screen. Managers can perform actions here, such as giving immediate feedback (via an **Add Feedback** button) or starting a performance review (if within the review period). This page is central to a manager’s workflow, as it’s where they evaluate and interact with an employee’s performance data.
* **Team Reviews:** *(Managers only)* A task-focused page listing all performance reviews the manager needs to complete for their team. Each entry shows an employee’s name, review due date, and status (e.g., “Not Started”, “In Progress”, “Submitted”). Managers can click an entry to fill out the review form for that employee. This page streamlines the performance review process by organizing all pending reviews in one place.
* **Team Reports:** *(Managers)* Provides analytical views for a manager about their team’s performance. Examples include the average goal completion rate per quarter, a bar chart of last cycle’s performance ratings across the team, and identification of top performers or areas of concern. These reports help managers make data-driven decisions and prepare for talent discussions.
* **Company Reports:** *(HR)* Similar to Team Reports but at an organizational level. HR can view company-wide metrics, compare departments, and track trends over time. For example, HR might see a chart of performance rating distributions across all departments or a summary of how many employees exceeded vs. met vs. fell below expectations in the last cycle. This informs HR policy decisions and executive reporting.
* **Review Cycle Management:** *(HR Admin)* The configuration hub for HR to define how performance evaluations are conducted. On this page, HR can set timelines (e.g., self-reviews open Oct 1–15, manager reviews due by Oct 31), edit the questionnaire or competencies for the review forms, and launch new review cycles. It may also list active and past cycles with their status (open, closed, archived). This page ensures the performance review process is tailored to the organization’s needs and is kept on schedule.
* **Goal Library & Calibration:** *(HR Admin)* A page for managing standardized goals and performance criteria. HR can maintain a library of common goals (which employees/managers can browse and adopt) and perform calibration of performance ratings (ensuring consistency across different teams and managers). For example, after managers submit reviews, HR might use this section to adjust or normalize ratings before finalizing results. This page supports consistency and fairness in the performance management process.
* **Employee Directory:** *(HR Admin)* A directory listing all employees, with search and filter capabilities (by department, manager, etc.). Selecting an employee opens their Profile (same view as managers see for their reports). HR uses this to access any employee’s performance data quickly, which is useful for audits or to assist in performance discussions at the organization level.
* **Permissions & Roles:** *(HR Admin/IT)* A maintenance page where HR or IT administrators assign user roles (who is a manager, who is an HR admin, etc.) and define access levels. It might list each user with their role and allowed sections, with options to update as people change positions. While not frequently used after initial setup, this page is crucial for onboarding new managers or adjusting access when organizational changes occur.
* **Help & Documentation:** Contains user assistance content such as how-to guides (“How to set a new goal”, “How to complete a self-review”) and FAQs. It provides context-sensitive help and contact info for support (like an internal helpdesk or HR IT support email). This section helps users resolve issues on their own and understand how to effectively use the dashboard’s features.

## Navigation Flows

*Describe or diagram how users move between sections/pages. Note primary navigation, shortcuts, and any contextual links.*

The Employee Performance Dashboard uses a top navigation menu (visible on every page) to allow users to switch between main sections: for example, **Dashboard**, **My Performance**, **Team Performance**, **Reports**, and **Admin** (the last two only visible to those with access). This primary navigation ensures that no matter where a user is, they can quickly jump to another major section.

Within pages, contextual links and buttons help users navigate deeper or complete tasks:

* From **Dashboard Home**, users click on widgets or alerts to go to the relevant page (e.g., clicking a “Complete Your Self-Review” alert takes an employee directly to the **My Reviews** page and opens the review form).
* In **Team Overview**, a manager can click a specific employee’s name to view that person’s **Employee Profile** page. On the profile, action buttons like **“Start Review”** or **“Add Feedback”** either navigate to the **Team Reviews** form for that employee or open a feedback form modal.
* Breadcrumb navigation is provided on sub-pages (e.g., on an Employee Profile page, a breadcrumb shows “Team Overview > \[Employee Name]”) which the manager can use to go back to the Team Overview.
* Quick access shortcuts: For example, an employee on their **My Goals** page might see a link to “View All Team Goals” (if they are a manager as well), which jumps to the Team Goals view in **Team Performance**. Likewise, HR users viewing a Company Report might have a drop-down to switch context to a specific department’s report.

Users generally start at the Dashboard and then follow the natural workflow: an **employee** completes their self-review via My Reviews, then later navigates back to Dashboard or My Performance; a **manager** goes from Dashboard to Team Performance to complete reviews for each team member, possibly viewing reports in between to check team trends; **HR** might primarily use the Admin and Reports sections, but can also view specific Employee Profiles via the directory if needed.

Overall, the navigation design emphasizes easy switching between high-level sections (through the persistent menu) and uses in-context links to guide users through multi-step processes (like completing all reviews for their team). The combination of global navigation and contextual shortcuts helps streamline user flows and reduce the number of steps needed to accomplish key tasks.

## User Access & Permissions

*If applicable, outline which users or roles can access each area of the site map.*

Different user roles have access to different sections of the Employee Performance Dashboard. Permissions are configured to ensure users only see information relevant to their role:

* **HR Administrators:** Full access to all sections and pages. HR can view and edit everything in **HR Administration**, run **Company Reports**, and also view individual **Employee Profiles** and **Team Performance** pages (mostly in read-only mode for oversight). Essentially, HR admins have the broadest access, including all employee data and all configuration settings.
* **Team Managers:** Access to **Dashboard Home**, **My Performance** (for their own goals/reviews as an employee), **Team Performance** (for managing their team), and **Team Reports**. Managers do *not* have access to HR Administration or company-wide reports. They can view profiles of their direct reports (via Team Performance) but cannot see data for employees outside their team.
* **Individual Employees:** Access limited to **Dashboard Home** and **My Performance** (their own goals, feedback, and reviews). Employees cannot access Team or Admin sections, and they only see their personal data in any shared reports. They have no visibility into other employees’ information.
* **Executives/Senior Leaders:** *(If applicable)* A role that grants read-only access to high-level **Reports & Analytics**. For example, an executive might see the Company Reports dashboard to monitor overall performance trends but would not use the tool to input data or manage employees. Their access is mainly for viewing summary information across the organization.

These permission levels ensure privacy and clarity: employees focus on their own information, managers on their team, and HR on the whole organization. The navigation menu dynamically shows or hides sections based on the user’s role (e.g., an individual contributor won’t see the Team Performance section at all).

## Integration Points

*Identify links to or from other internal systems, tools, or dashboards.*

The Employee Performance Dashboard integrates with several other internal systems to provide a seamless experience and ensure data consistency:

* **HRIS Integration:** The tool is linked with the company’s core HR Information System (i.e., the central HR database). Employee records (names, departments, reporting structure) are synchronized so the dashboard always has up-to-date information on organizational hierarchy. New hires or role changes in the HRIS automatically reflect in the dashboard’s team lists and permissions.
* **Single Sign-On (SSO):** User authentication is handled via the corporate SSO platform. Employees use their standard company credentials to access the dashboard, and their roles (HR, manager, etc.) are determined based on directory groups or attributes. This integration simplifies access control and leverages existing security protocols.
* **Email & Calendar Systems:** The dashboard sends automated email notifications (through the company’s email system) for key events – for example, reminders to complete reviews or confirmations when feedback is submitted. It also integrates with calendars by providing meeting invites or scheduling links for performance review discussions between managers and employees.
* **Data Analytics Platform:** For advanced reporting, the dashboard exports aggregate performance data to the company’s business intelligence tool (e.g., Tableau or Power BI). This allows HR analysts to combine performance data with other HR metrics (such as retention rates or training hours) to generate broader insights. Links like “View in BI Tool” may be available on certain reports for deeper analysis.
* **Other Internal Tools:** There are a few cross-links between the Performance Dashboard and other internal applications. For instance, from an employee’s profile, an HR user might click a link to open that employee’s record in the main HR management system. Similarly, the company’s intranet or HR portal provides a shortcut to launch the Performance Dashboard. These integrations ensure the tool fits into the overall ecosystem and that users can navigate between related systems easily.

All these integration points ensure the Performance Dashboard fits into the company’s larger digital ecosystem, minimizing duplicate data entry and providing users with a connected experience across different HR and IT tools.

## Annotations & Notes

*Any additional explanations, assumptions, or design rationale for the site map structure.*

* **Design Rationale:** The site map groups content by user role to reduce clutter. Early user research indicated that managers and individual contributors have very different needs, so the navigation clearly separates personal vs. team management functions. This insight drove the decision to create distinct sections for “My Performance” (personal) and “Team Performance” (management).
* **Mobile Access Assumption:** This document assumes primary use on desktop browsers (since managers typically complete reviews at their desk). A simplified mobile view might exist but is not detailed here. We deliberately kept the site map at a broad level and did not include every pop-up or modal (for example, the feedback submission form) to stay focused on primary navigation paths.
* **Employee Privacy:** Certain design decisions were made for privacy. For example, within Team Performance, managers cannot see peer feedback given to their reports unless it’s shared directly; the site map reflects this by not exposing any peer-to-peer feedback page to managers outside of an individual’s profile. Such privacy-related nuances are documented in the detailed design specifications (outside this site map).
* **Scalability:** The structure is designed to scale as the company grows. The Team Overview page, for instance, can handle large teams by paginating the list of direct reports if necessary. Similarly, Company Reports can filter by department to remain readable as the amount of data increases. These considerations were part of the information architecture planning, ensuring the site map will accommodate future growth.
* **Future Features (Not in Current Scope):** We included a placeholder for **Help & Documentation** to emphasize user support, though its content may be minimal in early versions. We also anticipate a future integration with a Learning Management System (LMS) to tie performance goals to training courses – that feature isn’t in the current site map, but space is left in the navigation for such an expansion down the line.

*(These notes provide insight into why the site map is structured as it is, and they document assumptions made during design. This context will help stakeholders and future team members understand the rationale behind the information architecture.)*

## Revision History

*Track major updates, versions, and dates for changes to the site map.*

| Version | Date         | Description of Changes                                                                                                                     | Author   |
| ------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------ | -------- |
| 0.1     | Jan 5, 2025  | **Initial Draft:** Created the first site map outline with main sections (Dashboard, My Performance, Team Performance, HR Admin).          | Jane Doe |
| 0.2     | Jan 12, 2025 | **Updated Scope:** Added “Reports & Analytics” section after stakeholder feedback; expanded Team Performance subsections for clarity.      | Jane Doe |
| 0.3     | Jan 20, 2025 | **Draft Review:** Incorporated review comments (clarified navigation flows and added the Help & Documentation section).                    | Jane Doe |
| 1.0     | Feb 1, 2025  | **Approved Release:** Finalized content post stakeholder approval. Minor edits to descriptions; no structural changes from the last draft. | Jane Doe |

## Approval & Sign-off

*Who must review and approve the UX Site Map Document?*

This document requires sign-off from the following stakeholders to ensure alignment across teams:

* **Maria Gonzales – Head of Human Resources (Project Sponsor):** Reviewed for HR process alignment and confirms that the site map’s structure aligns with company performance management policies.
* **Alex Patel – Engineering Manager (Internal Tools):** Reviewed for technical feasibility and data integration considerations; confirms that the proposed structure can be implemented within our internal systems.
* **Samira Lee – UX Lead (Product Design):** Reviewed for user experience consistency; verifies that the structure meets usability standards and aligns with the overall design strategy.
* **Michael Chen – Product Manager (Internal Systems):** Reviewed for feature completeness; ensures the site map covers all required functionality and aligns with product goals.

Each of the above stakeholders has reviewed this document. Their approval indicates agreement that the site map accurately represents the intended design, and that the team can proceed with detailed design and development according to this blueprint.
