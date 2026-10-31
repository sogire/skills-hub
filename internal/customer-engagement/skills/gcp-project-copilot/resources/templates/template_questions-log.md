# **Technical Questions Log**

# **{{CUSTOMER_NAME}} — {{PROJECT_NAME}} ({{MEETING_TITLE}})**

| Metadata Field | Document Detail |
| :---- | :---- |
| **Source Document** | [{{MEETING_DOC_TITLE}}](https://docs.google.com/document/d/{{DOC_ID}}/edit) |
| **Session Date** | `{{YYYY-MM-DD}}` |
| **Scope** | Comprehensive inventory of Customer technical questions (`[D#-Q##]` / `[P1-Q##]`) raised by {{CUSTOMER_NAME}} and Discovery & Scoping questions (`[D#-S##]` / `[P1-S##]`) raised by Google Cloud and External Partners during the session. |
| **Note** | Questions are grouped by canonical architectural domain (`D1..Dn` and `P1` from [`specs_project.md`](../../specs/specs_project.md)) and split within each domain into **1. Customer Technical Questions ({{CUSTOMER_NAME}})** (`[D#-Q##]` / `[P1-Q##]`) and **2. Discovery & Scoping Questions (Google Cloud & External Partners)** (`[D#-S##]` / `[P1-S##]`). Direct responses and architectural evaluations in `project/questions-answered/` strictly target Customer (`[D#-Q##]`) questions. |

# **Session Overview & Question Summary**

| Domain Category | Code Range (`Q` / `S`) | Core Technical Focus Areas | Customer (`Q`) | Scoping (`S`) | Total Raised |
| :---- | :---- | :---- | :----: | :----: | :----: |
| **D1. Data Platform Foundation, Ingestion & Data Products** | `D1-Q01..` / `D1-S01..` | Medallion architecture (`Bronze`/`Silver`/`Gold`), Data Product classification & contracts, ingestion/ELT pipelines, Project Factory & IaC | {{COUNT_D1_Q}} | {{COUNT_D1_S}} | {{COUNT_D1}} |
| **D2. Data Sharing, Consumer Authorization & Access Management** | `D2-Q01..` / `D2-S01..` | Consumer application authorization, Authorized Views/Datasets, semantic interface datasets, Analytics Hub & IAM scale quotas | {{COUNT_D2_Q}} | {{COUNT_D2_S}} | {{COUNT_D2}} |
| **D3. Data Governance, Knowledge Catalog, Quality & Security** | `D3-Q01..` / `D3-S01..` | Dataplex Universal Catalog, Data Quality & lineage, Cloud DLP, Column-Level Security (`Policy Tags`), Row-Level Security (`RLS`) & VPC-SC | {{COUNT_D3_Q}} | {{COUNT_D3_S}} | {{COUNT_D3}} |
| **D4. Analytics Consumption, Semantic Layer, BI & Applied ML** | `D4-Q01..` / `D4-S01..` | Governed BI & semantic layer (`Looker`, `Conversational Analytics`), analytical SQL, `BQML`, `BigFrames`, `BigLake` & `BigQuery Graph` | {{COUNT_D4_Q}} | {{COUNT_D4_S}} | {{COUNT_D4}} |
| **D5. Platform Observability, Capacity Optimization & FinOps** | `D5-Q01..` / `D5-S01..` | `BigQuery Editions` slot reservations & autoscaling, storage/query optimization, `INFORMATION_SCHEMA` telemetry & cost attribution | {{COUNT_D5_Q}} | {{COUNT_D5_S}} | {{COUNT_D5}} |
| **D6. AI Agents Architecture, Orchestration & Data Grounding** | `D6-Q01..` / `D6-S01..` | `Google ADK`, `Gemini Enterprise`, grounding over Data Products (`MCP`, `BigQuery Data Agents`, `DAK`, RAG) & OAuth `On-Behalf-Of` identity | {{COUNT_D6_Q}} | {{COUNT_D6_S}} | {{COUNT_D6}} |
| **D7. AgentOps, Evaluation, Security Guardrails & AI FinOps** | `D7-Q01..` / `D7-S01..` | Agent evaluation (`ADK Eval`, `Vertex AI Evaluation`), trace observability, `Model Armor` guardrails & token/slot FinOps | {{COUNT_D7_Q}} | {{COUNT_D7_S}} | {{COUNT_D7}} |
| **P1. Project Organization, Workstream Alignment & Delivery Governance** | `P1-Q01..` / `P1-S01..` | Roadmap prioritization, workshop cadence, cross-workstream alignment across Data, Analytics & Agents, and pilot logistics | {{COUNT_P1_Q}} | {{COUNT_P1_S}} | {{COUNT_P1}} |
| **Total** | **`{{TOTAL_QUESTIONS}} Questions`** | **All Canonical Architectural & Project Governance Domains** | **{{TOTAL_Q_QUESTIONS}}** | **{{TOTAL_S_QUESTIONS}}** | **{{TOTAL_QUESTIONS}}** |

---

# **D1. Data Platform Foundation, Ingestion & Data Products**

## 1. Customer Technical Questions ({{CUSTOMER_NAME}})

* **`[D1-Q01]` {{QUESTION_TEXT_D1_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (Customer — {{CUSTOMER_NAME}})
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

## 2. Discovery & Scoping Questions (Google Cloud & External Partners)

* **`[D1-S01]` {{QUESTION_TEXT_D1_S1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (Google Cloud)
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

---

# **D2. Data Sharing, Consumer Authorization & Access Management**

## 1. Customer Technical Questions ({{CUSTOMER_NAME}})

* **`[D2-Q01]` {{QUESTION_TEXT_D2_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (Customer — {{CUSTOMER_NAME}})
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

## 2. Discovery & Scoping Questions (Google Cloud & External Partners)

* **`[D2-S01]` {{QUESTION_TEXT_D2_S1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (External Partner — {{EXTERNAL_PARTNERS}})
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

---

# **P1. Project Organization, Workstream Alignment & Delivery Governance**

## 1. Customer Technical Questions ({{CUSTOMER_NAME}})

* **`[P1-Q01]` {{QUESTION_TEXT_P1_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (Customer — {{CUSTOMER_NAME}})
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

## 2. Discovery & Scoping Questions (Google Cloud & External Partners)

* **`[P1-S01]` {{QUESTION_TEXT_P1_S1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}} (Google Cloud)
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})
