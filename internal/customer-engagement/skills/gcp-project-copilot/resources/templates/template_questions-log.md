# **Technical Questions Log**

# **{{CUSTOMER_NAME}} — {{PROJECT_NAME}} ({{MEETING_TITLE}})**

| Metadata Field | Document Detail |
| :---- | :---- |
| **Source Document** | [{{MEETING_DOC_TITLE}}](https://docs.google.com/document/d/{{DOC_ID}}/edit) |
| **Session Date** | `{{YYYY-MM-DD}}` |
| **Scope** | Comprehensive inventory of technical, architectural, and project organization questions raised by {{CUSTOMER_NAME}}, Google Cloud, and partner team members during the session. |
| **Note** | Questions are grouped by canonical architectural domain (`D1..Dn` and `P1` from [`specs_project.md`](../../specs/specs_project.md)) and prefixed with their permanent domain-scoped reference code (`[D#-Q##]` / `[P1-Q##]`). Direct responses are synthesized in the companion `challenges` document. |

# **Session Overview & Question Summary**

| Domain Category | Code Range | Core Technical Focus Areas | Total Raised |
| :---- | :---- | :---- | :---- |
| **D1. Data Platform Foundation, Ingestion & Data Products** | `D1-Q01..` | Medallion architecture (`Bronze`/`Silver`/`Gold`), Data Product classification & contracts, ingestion/ELT pipelines, Project Factory & IaC | {{COUNT_D1}} |
| **D2. Data Sharing, Consumer Authorization & Access Management** | `D2-Q01..` | Consumer application authorization, Authorized Views/Datasets, semantic interface datasets, Analytics Hub & IAM scale quotas | {{COUNT_D2}} |
| **D3. Data Governance, Knowledge Catalog, Quality & Security** | `D3-Q01..` | Dataplex Universal Catalog, Data Quality & lineage, Cloud DLP, Column-Level Security (`Policy Tags`), Row-Level Security (`RLS`) & VPC-SC | {{COUNT_D3}} |
| **D4. Analytics Consumption, Semantic Layer, BI & Applied ML** | `D4-Q01..` | Governed BI & semantic layer (`Looker`, `Conversational Analytics`), analytical SQL, `BQML`, `BigFrames`, `BigLake` & `BigQuery Graph` | {{COUNT_D4}} |
| **D5. Platform Observability, Capacity Optimization & FinOps** | `D5-Q01..` | `BigQuery Editions` slot reservations & autoscaling, storage/query optimization, `INFORMATION_SCHEMA` telemetry & cost attribution | {{COUNT_D5}} |
| **D6. AI Agents Architecture, Orchestration & Data Grounding** | `D6-Q01..` | `Google ADK`, `Gemini Enterprise`, grounding over Data Products (`MCP`, `BigQuery Data Agents`, `DAK`, RAG) & OAuth `On-Behalf-Of` identity | {{COUNT_D6}} |
| **D7. AgentOps, Evaluation, Security Guardrails & AI FinOps** | `D7-Q01..` | Agent evaluation (`ADK Eval`, `Vertex AI Evaluation`), trace observability, `Model Armor` guardrails & token/slot FinOps | {{COUNT_D7}} |
| **P1. Project Organization, Workstream Alignment & Delivery Governance** | `P1-Q01..` | Roadmap prioritization, workshop cadence, cross-workstream alignment across Data, Analytics & Agents, and pilot logistics | {{COUNT_P1}} |

---

# **D1. Data Platform Foundation, Ingestion & Data Products**

* **`[D1-Q01]` {{QUESTION_TEXT_D1_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}}
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

---

# **D2. Data Sharing, Consumer Authorization & Access Management**

* **`[D2-Q01]` {{QUESTION_TEXT_D2_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}}
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})

---

# **P1. Project Organization, Workstream Alignment & Delivery Governance**

* **`[P1-Q01]` {{QUESTION_TEXT_P1_1}}**
  * **Asked By:** {{FIRST_NAME}} {{LAST_NAME_UPPER}}
  * **Timestamp:** [Timestamp {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}})
