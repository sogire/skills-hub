# **Customer Glossary of Terms & Architectural Dictionary**

# **{{PROJECT_NAME}} ({{CUSTOMER_NAME}})**

| Metadata Field | Document Detail |
| :---- | :---- |
| **Customer / Program** | {{CUSTOMER_NAME}} — {{PROJECT_NAME}} ({{PROGRAM_NAME}}) |
| **Maintenance Scope** | **Project-Level Living Document** ([`project/common/project_glossary.md`](./project_glossary.md)) — updated after every analyzed session |
| **Last Updated** | {{YYYY-MM-DD}} |
| **Purpose** | Canonical dictionary of business concepts, source systems, domain taxonomy, compliance rules, and platform terminology, structured for both transcript disambiguation and Dataplex Business Glossary ingestion. |

# **Glossary Overview by Topic Category**

| Topic Category | Core Focus Areas | Total Terms |
| :---- | :---- | :---- |
| **1. Programs, Initiatives & Organizational Entities** | Umbrella programs, business units, external system integrators | {{COUNT_1}} |
| **2. Business Domains, Roles & Operational Concepts** | Business domains, domain processes, HR/operational attributes | {{COUNT_2}} |
| **3. Source Systems & Data Ingestion Feeds** | Operational ERPs, master data tools, ALM/CRM systems, external feeds, manual files | {{COUNT_3}} |
| **4. Data Mesh, Data Products & Medallion Taxonomy** | Customer-specific data product tiers, medallion layer rules, DLQ data models | {{COUNT_4}} |
| **5. Security, Compliance & Governance Standards** | Industry regulatory frameworks, access models, confidentiality classifications | {{COUNT_5}} |
| **6. Platform, Cloud & AI Tooling Terminology** | GCP services, catalog terms, and AI agent frameworks as used by the customer | {{COUNT_6}} |

---

# **1. Programs, Initiatives & Organizational Entities**

| Term / Acronym | Transcript Aliases | Definition & Business Context | Architectural / Project Relevance | Sessions Referenced |
| :---- | :---- | :---- | :---- | :---- |
| **{{PROJECT_ACRONYM}}** *({{PROJECT_NAME}})* | `{{PROJECT_ACRONYM}}` | Enterprise data platform initiative integrating multiple business units to prepare governed data for AI and BI usage. | Defines the multi-domain, multi-project GCP architecture pattern beyond the initial `{{PILOT_DOMAIN}}` pilot. | `{{YYYY-MM-DD}}` |
| **{{PROGRAM_NAME}}** | `{{PROGRAM_ALIAS}}` | Enterprise AI and digital transformation program sponsoring the data platform and agentic initiatives. | Governs identity propagation patterns and AI agent adoption across business domains. | `{{YYYY-MM-DD}}` |

---

# **2. Business Domains, Roles & Operational Concepts**

| Term / Acronym | Transcript Aliases | Domain | Definition & Business Context | Architectural / Technical Impact | Sessions Referenced |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **{{PILOT_USE_CASE}}** | `{{PILOT_USE_CASE}}` | {{PILOT_DOMAIN}} | Flagship analytical initiative consolidating master data, transaction facts, and KPIs across the pilot domain. | Implemented as a Gold-layer star schema and primary candidate for Analytics Hub publication. | `{{YYYY-MM-DD}}` |
| **{{DOMAIN_ROLE}}** | `{{DOMAIN_ROLE_ALIAS}}` | {{PILOT_DOMAIN}} / HR | Domain-specific operational role whose data access scope is tied to dynamic project or regional assignments. | Requires attribute-based mapping tables alongside Google Groups to enforce Row-Level Security (RLS). | `{{YYYY-MM-DD}}` |

---

# **3. Source Systems & Data Ingestion Feeds**

| System / Feed | Transcript Aliases | Primary Domain | System Type & Description | Ingestion & Schema Characteristics | Sessions Referenced |
| :---- | :---- | :---- | :---- | :---- | :---- |
| **{{ERP_SYSTEM}}** | `{{ERP_SYSTEM}}` | Finance / Operations | Core enterprise ERP system generating operational and financial transactions. | Ingested via Cloud Storage / batch connectors into the BigQuery Bronze layer. | `{{YYYY-MM-DD}}` |
| **{{MASTER_DATA_SYSTEM}}** | `{{MASTER_DATA_ALIAS}}` | {{PILOT_DOMAIN}} | Internal Master Data Management (MDM) application. | Subject to schema evolution (newly added or modified attributes), requiring schema drift handling. | `{{YYYY-MM-DD}}` |

---

# **4. Data Mesh, Data Products & Medallion Taxonomy**

| Term / Concept | Category | Customer-Specific Definition | Architectural Rule / Implementation | Sessions Referenced |
| :---- | :---- | :---- | :---- | :---- |
| **Source Data Product** | Data Product Tier | A data product relying strictly on operational source system data (normalized/cleansed) without cross-source business enrichment. | Normalized in the **Silver Layer** and exposed via governed **Gold** views for reuse across downstream domains. | `{{YYYY-MM-DD}}` |
| **Aggregated Data Product** | Data Product Tier | A data product that joins, enriches, and aggregates multiple sources into domain-level metrics and dimensions. | Resides in the **Gold Layer** (e.g., domain star schema). | `{{YYYY-MM-DD}}` |
| **Consumer Data Product** | Data Product Tier | A tailored analytical view or dataset formatted specifically for a downstream business use case, BI dashboard, or AI consumer. | Exposed via **Analytics Hub** listings or authorized views with consumer-pays compute. | `{{YYYY-MM-DD}}` |

---

# **5. Security, Compliance & Governance Standards**

| Term / Standard | Transcript Aliases | Definition & Scope | GCP Enforcement Mechanism | Sessions Referenced |
| :---- | :---- | :---- | :---- | :---- |
| **{{COMPLIANCE_STANDARD}}** | `{{COMPLIANCE_STANDARD}}` | Mandatory industry information security and tenant/data isolation standard applicable to customer workloads. | Enforced via GCP project boundary isolation, VPC Service Controls, CMEK, and BigQuery RLS/CLS. | `{{YYYY-MM-DD}}` |
| **Confidentiality Tiers (`C1–C4`)** | `C1`, `C2`, `C3`, `C4` | Enterprise data classification taxonomy ranging from Public (`C1`) to Restricted/Secret (`C4`). | Enforced via Dataplex Policy Tags, BigQuery Column-Level Security (CLS), and Dynamic Data Masking. | `{{YYYY-MM-DD}}` |

---

# **6. Platform, Cloud & AI Tooling Terminology**

| Term Used in Meetings | Official GCP / Technical Mapping | Context in Project | Sessions Referenced |
| :---- | :---- | :---- | :---- |
| **Knowledge Catalog** | **Dataplex Universal Catalog** | Used for technical metadata management, automated data profiling/quality scans, policy tags, and business glossary. | `{{YYYY-MM-DD}}` |
| **Analytics Hub** | **BigQuery Analytics Hub** | Consumer-facing data marketplace used to publish and subscribe to Data Products across project boundaries with decoupled compute billing. | `{{YYYY-MM-DD}}` |

