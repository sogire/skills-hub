# **Technical Question Evaluation & Architectural Answer**

# **{{CUSTOMER_NAME}} — {{PROJECT_NAME}} (`[{{QUESTION_ID}}]`: {{QUESTION_SHORT_TITLE}})**

| Metadata Field | Document Detail |
| :---- | :---- |
| **Customer / Project** | **{{CUSTOMER_NAME}}** — {{PROJECT_NAME}} |
| **Question ID** | **`[{{QUESTION_ID}}]`** |
| **Question** | **{{QUESTION_TEXT}}** |
| **Canonical Domain** | **{{DOMAIN_ID}}. {{DOMAIN_NAME}}** ([`specs_project.md`](../../specs/specs_project.md)) |
| **Asked By** | {{FIRST_NAME}} {{LAST_NAME_UPPER}} |
| **Source Session & Log** | [{{YYYY-MM-DD}} ({{MEETING_SLUG}})](../meetings/{{YYYY-MM-DD}}_{{MEETING_SLUG}}/{{YYYYMMDD}}_questions-log_{{MEETING_SLUG}}.md) · [Transcript {{HH:MM:SS}}](https://docs.google.com/document/d/{{DOC_ID}}/edit?tab={{TRANSCRIPT_TAB_ID}}#heading={{HEADING_ID}}) · [`project_questions-log.md`](../common/project_questions-log.md) |
| **Date Answered** | `{{YYYY-MM-DD_ANSWERED}}` |

---

## 1. Executive Summary & Solution Matrix

{{EXECUTIVE_SUMMARY_PARAGRAPH}}

| Requirement / Sub-Question | Recommended Google Cloud Solution | Architectural Layer | Implementation / Enforcement Mechanism |
| :---- | :---- | :---- | :---- |
| **{{REQUIREMENT_1}}** | {{GCP_SOLUTION_1}} | {{LAYER_1}} *(e.g., Storage / Table DDL, Transformation, Catalog, Sharing, IAM, Agentic)* | {{MECHANISM_1}} |
| **{{REQUIREMENT_2}}** | {{GCP_SOLUTION_2}} | {{LAYER_2}} | {{MECHANISM_2}} |
| **{{REQUIREMENT_3}}** | {{GCP_SOLUTION_3}} | {{LAYER_3}} | {{MECHANISM_3}} |

---

## 2. Technical Evaluation & Google Cloud Architecture

### 2.1 {{SUBSECTION_2_1_TITLE}} *(e.g., Step 1 — ..., Control 1 — ..., Pattern A — ..., or Direct Architectural Title)*
* **GCP Service / Feature**: {{SUBSECTION_2_1_GCP_SERVICE}}
* **How It Works**: {{SUBSECTION_2_1_EXPLANATION}}
* **Implementation**:
  ```sql
  {{SUBSECTION_2_1_CODE_SNIPPET}}
  ```

### 2.2 {{SUBSECTION_2_2_TITLE}}
* **GCP Service / Feature**: {{SUBSECTION_2_2_GCP_SERVICE}}
* **How It Works**: {{SUBSECTION_2_2_EXPLANATION}}
* **Implementation**:
  ```sql
  {{SUBSECTION_2_2_CODE_SNIPPET}}
  ```

### 2.3 {{SUBSECTION_2_3_TITLE}}
* **GCP Service / Feature**: {{SUBSECTION_2_3_GCP_SERVICE}}
* **How It Works**: {{SUBSECTION_2_3_EXPLANATION}}
* **Implementation**:
  ```json
  {{SUBSECTION_2_3_CODE_SNIPPET}}
  ```

---

## 3. IAM Permissions, Security Guardrails & Platform Caveats

### 3.1 IAM Permissions & Enforcement Matrix

| Operation / Vector | Required IAM Permission(s) | Predefined Roles That Grant It *(Avoid Over-Granting)* | How to Enforce / Restrict |
| :---- | :---- | :---- | :---- |
| **{{OPERATION_1}}** | `{{IAM_PERMISSION_1}}` | `{{PREDEFINED_ROLES_1}}` | {{RESTRICTION_METHOD_1}} |
| **{{OPERATION_2}}** | `{{IAM_PERMISSION_2}}` | `{{PREDEFINED_ROLES_2}}` | {{RESTRICTION_METHOD_2}} |

### 3.2 Critical Architectural Caveats & Edge Cases

> [!IMPORTANT]
> **{{CAVEAT_TITLE}}**:
> {{CAVEAT_EXPLANATION}}

---

## 4. Summary Recommendation & Next Steps for {{CUSTOMER_NAME}}

> [!TIP]
> **Recommended Target Architecture for {{CUSTOMER_NAME}} (`[{{QUESTION_ID}}]`)**:
> {{SUMMARY_RECOMMENDATION}}

1. **`[Google Cloud / {{CUSTOMER_NAME}}]` {{ACTION_ITEM_1}}**: {{ACTION_ITEM_1_DETAIL}}
2. **`[Google Cloud / {{CUSTOMER_NAME}}]` {{ACTION_ITEM_2}}**: {{ACTION_ITEM_2_DETAIL}}
3. **Related Project Deliverables**:
   * **Consolidated Questions Log**: [`project_questions-log.md`](../common/project_questions-log.md)
   * **Master Architectural Challenges**: [`project_challenges.md`](../common/project_challenges.md)

---

## 5. Google Cloud Documentation Reference Links

* **[{{DOC_TITLE_1}}]({{DOC_URL_1}})**: {{DOC_DESCRIPTION_1}}
* **[{{DOC_TITLE_2}}]({{DOC_URL_2}})**: {{DOC_DESCRIPTION_2}}
* **[{{DOC_TITLE_3}}]({{DOC_URL_3}})**: {{DOC_DESCRIPTION_3}}

---

## 6. Skills Employed

| Workspace Skill | Technical Contribution to This Evaluation |
| :---- | :---- |
| **`{{SKILL_NAME_1}}`** | {{SKILL_CONTRIBUTION_1}} |
| **`{{SKILL_NAME_2}}`** | {{SKILL_CONTRIBUTION_2}} |
| **`{{SKILL_NAME_3}}`** | {{SKILL_CONTRIBUTION_3}} |

