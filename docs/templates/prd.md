# Product Requirements Document (PRD) Template

Use this Markdown outline as a living document shared by Product, Engineering, and Business teams. Each heading includes a short prompt to help authors provide the right level of detail.

---

## 1. Title Page

| Field                   | Description                                 |
| ----------------------- | ------------------------------------------- |
| **Tool Name**           | Official name of the internal product/tool. |
| **Project Name / Code** | Optional codename used during development.  |
| **Version**             | Document version (e.g., *v1.0 Draft*).      |
| **Date**                | Date this version was published.            |
| **Author(s)**           | Name(s) and role(s) of primary drafter(s).  |
| **Department / Squad**  | Team that owns day‑to‑day delivery.         |

---

## 2. Purpose & Background

*Why does this product exist and why now?*

* Summarize the business process, workflow, or strategic need being addressed.
* Explain why it is a priority in the current context (e.g., regulatory deadline, cost‑saving initiative, scaling bottleneck).

---

## 3. Stakeholders & Internal Users

*Who cares and who uses it?*

| Role             | Name / Team | Responsibilities in this project   |
| ---------------- | ----------- | ---------------------------------- |
| Sponsor          |             | Owns budget and strategic fit.     |
| Product Manager  |             | Maintains the PRD and roadmap.     |
| Engineering Lead |             | Technical feasibility & estimates. |
| Core Users       |             | Daily interaction with the tool.   |
| Supporting Teams |             | Security, Legal, Analytics, etc.   |

---

## 4. Problem Statement

*What pain or opportunity are we solving?*

* Describe the current inefficiencies, risks, or lost opportunities.
* Include evidence — metrics, user feedback, audit findings, compliance gaps.

---

## 5. Goals & Success Metrics

*How will we know we succeeded?*

| Objective                      | Metric                      | Target / KPI |
| ------------------------------ | --------------------------- | ------------ |
| e.g., Reduce manual data entry | % reduction in manual steps | ≥ 80 %       |

Focus on 3‑5 measurable outcomes (efficiency, error rate, adoption, compliance, NPS).

---

## 6. In Scope

*What will be delivered in this release?*

* Bullet list of features, workflows, integrations, and user groups included.

## 7. Out of Scope

*What will **not** be delivered now?*

* Clarify excluded features, legacy system deprecations, or phases.

---

## 8. Functional Requirements

*What must the tool do?*

| #    | Requirement | Priority (MoSCoW) | Notes / Acceptance Criteria |
| ---- | ----------- | ----------------- | --------------------------- |
| FR‑1 |             |                   |                             |

Cover core features, workflows, automation rules, permission models, and integrations.

---

## 9. Non‑Functional Requirements

*Quality attributes the solution must meet.*

* **Performance** (e.g., < 2 s response for 95 % of queries)
* **Scalability** (expected load and growth)
* **Security & Privacy** (encryption, RBAC, audit logs, compliance standards)
* **Availability & Reliability** (Uptime SLAs, redundancy)
* **Maintainability** (coding standards, documentation, observability)
* **Usability & Accessibility** (UX guidelines, WCAG targets)

---

## 10. User Stories & Use Cases

*Describe desired experiences from the user’s perspective.*

```
As a [role], I want to [goal] so that [benefit].
```

List key scenarios, edge cases, and acceptance tests. Link to detailed user‑journey maps if available.

---

## 11. Process & Workflow Diagrams

*Visualize how things flow today vs. after launch.*

* **Current‑State Diagram**: highlight pain points.
* **Future‑State Diagram**: show proposed process and system interactions.
* Attach BPMN, UML, or simple flowcharts as images or links.

---

## 12. Data & Integration Requirements

*What data moves where?*

| Data Element | Source | Destination | CRUD Ops | Privacy Notes |
| ------------ | ------ | ----------- | -------- | ------------- |
|              |        |             |          |               |

* Identify APIs, message queues, file drops, or ETL jobs.
* Specify data retention, encryption, GDPR/LGPD handling, and PII masking.

---

## 13. Adoption, Training, & Support Plan

*How will people start using this tool and stay productive?*

* Roll‑out strategy (pilot, phased, big‑bang).
* Training materials (videos, live sessions, quick‑start guides).
* Support channels (Slack, service desk, runbooks, FAQs).
* Change‑management communications (emails, town‑halls, release notes).

---

## 14. Assumptions & Constraints

*What must be true, and what limits us?*

* Assumed platform availability, data quality, resources, or third‑party services.
* Constraints like budget caps, legacy tech dependencies, fixed launch window.

---

## 15. Risks & Mitigation

| Risk | Impact | Likelihood | Mitigation / Contingency |
| ---- | ------ | ---------- | ------------------------ |
|      |        |            |                          |

Include technical, operational, security, and adoption risks.

---

## 16. Timeline & Milestones

*High‑level schedule (update in project plan).*

| Phase              | Start | End | Deliverables            |
| ------------------ | ----- | --- | ----------------------- |
| Discovery & Design |       |     | Personas, wireframes    |
| Build              |       |     | MVP complete            |
| Test & QA          |       |     | Test reports, bug fixes |
| Roll‑out           |       |     | Production release      |
| Adoption & Review  |       |     | Usage targets met       |

---

## 17. Approval & Sign‑off

| Role                  | Name | Signature / Date |
| --------------------- | ---- | ---------------- |
| Product Manager       |      |                  |
| Engineering Lead      |      |                  |
| Security / Compliance |      |                  |
| Executive Sponsor     |      |                  |

Document any required change‑control process after sign‑off.

---

**How to Use This Template**

1. Duplicate the Markdown file in your team’s documentation space.
2. Replace prompts with project‑specific content.
3. Keep the document versioned and review it at each major milestone.

> *Tip:* Treat the PRD as a living artifact—update assumptions, scope, and risks whenever they change to maintain shared alignment throughout the project lifecycle.
