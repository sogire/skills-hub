# **{{DELIVERABLE_TITLE}}**

# **{{CUSTOMER_NAME}} — {{PROJECT_NAME}}: {{DELIVERABLE_SUBTITLE}}**

| Metadata Field | Document Detail |
| :---- | :---- |
| **Customer / Initiative** | **{{CUSTOMER_NAME}}** — {{PROJECT_NAME}} ({{PROGRAM_NAME}}) |
| **Deliverable Type & Audience** | {{DELIVERABLE_TYPE_AND_AUDIENCE}} *(e.g., Architecture Blueprint & Deployment Guide — Executive & Technical Stakeholders)* |
| **Architectural Scope** | {{ARCHITECTURAL_SCOPE_SUMMARY}} |
| **Document Version** | `{{DOCUMENT_VERSION}}` *(e.g., `1.0.0`)* |
| **Date** | `{{YYYY-MM-DD}}` |

---

## 1. Executive Summary & Architectural Decisions

{{EXECUTIVE_SUMMARY_PARAGRAPH}}

| Architectural Dimension / Requirement | Recommended Google Cloud Pattern | Target GCP Services | Key Governance & Operational Benefit |
| :---- | :---- | :---- | :---- |
| **{{REQUIREMENT_1}}** | {{RECOMMENDED_PATTERN_1}} | {{GCP_SERVICES_1}} | {{BENEFIT_1}} |
| **{{REQUIREMENT_2}}** | {{RECOMMENDED_PATTERN_2}} | {{GCP_SERVICES_2}} | {{BENEFIT_2}} |
| **{{REQUIREMENT_3}}** | {{RECOMMENDED_PATTERN_3}} | {{GCP_SERVICES_3}} | {{BENEFIT_3}} |

---

## 2. Customer Context, Current State & Core Challenges

### 2.1 Current State & Business Objectives ({{CUSTOMER_NAME}})
* **{{CURRENT_STATE_POINT_1_TITLE}}**: {{CURRENT_STATE_POINT_1_DETAIL}}
* **{{CURRENT_STATE_POINT_2_TITLE}}**: {{CURRENT_STATE_POINT_2_DETAIL}}

### 2.2 Core Technical Challenges & Constraints to Resolve
* **{{CHALLENGE_1_TITLE}}**: {{CHALLENGE_1_DETAIL}}
* **{{CHALLENGE_2_TITLE}}**: {{CHALLENGE_2_DETAIL}}

---

## 3. Recommended Google Cloud Target Architecture

{{TARGET_ARCHITECTURE_OVERVIEW}}

![{{DIAGRAM_CAPTION}}](../diagrams/{{DELIVERABLE_STEM}}/{{DIAGRAM_FILENAME}}.svg)

### 3.1 End-to-End Architectural Flow & Design Principles
1. **{{FLOW_STEP_1_TITLE}}**: {{FLOW_STEP_1_DETAIL}}
2. **{{FLOW_STEP_2_TITLE}}**: {{FLOW_STEP_2_DETAIL}}
3. **{{FLOW_STEP_3_TITLE}}**: {{FLOW_STEP_3_DETAIL}}

### 3.2 Architectural Alternatives & Trade-Off Evaluation

| Evaluation Criterion | Recommended Target Architecture ({{OPTION_A_NAME}}) | Alternative Approach ({{OPTION_B_NAME}}) | Architectural Rationale |
| :---- | :---- | :---- | :---- |
| **{{CRITERION_1}}** | {{OPTION_A_CRIT_1}} | {{OPTION_B_CRIT_1}} | {{RATIONALE_1}} |
| **{{CRITERION_2}}** | {{OPTION_A_CRIT_2}} | {{OPTION_B_CRIT_2}} | {{RATIONALE_2}} |

---

## 4. Detailed Technical Design, Security & FinOps Guardrails

### 4.1 {{SUBSECTION_4_1_TITLE}}
{{SUBSECTION_4_1_EXPLANATION}}

```sql
{{SUBSECTION_4_1_CODE_SNIPPET}}
```

### 4.2 {{SUBSECTION_4_2_TITLE}}
{{SUBSECTION_4_2_EXPLANATION}}

```bash
{{SUBSECTION_4_2_CODE_SNIPPET}}
```

### 4.3 Security, IAM Governance & Platform Guardrails

| Governance / Security Layer | Enforcement Mechanism | Required IAM Roles / Policy Configuration | Operational Guardrail |
| :---- | :---- | :---- | :---- |
| **{{SECURITY_LAYER_1}}** | {{MECHANISM_1}} | `{{IAM_OR_POLICY_1}}` | {{GUARDRAIL_1}} |
| **{{SECURITY_LAYER_2}}** | {{MECHANISM_2}} | `{{IAM_OR_POLICY_2}}` | {{GUARDRAIL_2}} |

> [!IMPORTANT]
> **{{CRITICAL_GUARDRAIL_TITLE}}**:
> {{CRITICAL_GUARDRAIL_EXPLANATION}}

---

## 5. Implementation Roadmap & Recommended Next Steps for {{CUSTOMER_NAME}}

> [!TIP]
> **Priority Architectural Recommendation for {{CUSTOMER_NAME}}**:
> {{SUMMARY_RECOMMENDATION}}

| Phase / Milestone | Action Item & Deliverable | Accountable Owner | Target Outcome |
| :---- | :---- | :---- | :---- |
| **Phase 1 — Foundation** | **{{ACTION_1_TITLE}}**: {{ACTION_1_DETAIL}} | `{{ACTION_1_OWNER}}` | {{ACTION_1_OUTCOME}} |
| **Phase 2 — Industrialization** | **{{ACTION_2_TITLE}}**: {{ACTION_2_DETAIL}} | `{{ACTION_2_OWNER}}` | {{ACTION_2_OUTCOME}} |

---

## 6. References & Source Traceability

### 6.1 Official Google Cloud Documentation
* **[{{DOC_TITLE_1}}]({{DOC_URL_1}})**: {{DOC_DESCRIPTION_1}}
* **[{{DOC_TITLE_2}}]({{DOC_URL_2}})**: {{DOC_DESCRIPTION_2}}

### 6.2 Internal Working Sources (Filename Reference Only)
* `{{WORKING_PROCESS_SOURCE_FILENAME_1}}.md`
* `{{QUESTION_ANSWERED_SOURCE_FILENAME_1}}.md`

