# AI Slide-Builder Prompt & Storyboard: {{DEMO_TITLE}}

> **Source Visual Demo Guide:** [`{{DEMO_STEM}}.md`](./{{DEMO_STEM}}.md)  
> **Architecture Diagram:** [`architecture-flow.svg`](../diagrams/{{DEMO_STEM}}/architecture-flow.svg)  
> **Target Audience:** {{CUSTOMER_NAME}} Stakeholders (Business & Technical Workshop)  
> **Target Deck Length:** {{SLIDE_COUNT}} Slides (Story-Driven Walkthrough + Console Screenshot Companion — **100% Code-Free**)

---

## 1. Instructions for the Google Slides Generation Agent

### Role & Presentation Objective
You are an Executive Presentation Designer and Principal Google Cloud Architect creating a **{{SLIDE_COUNT}}-slide Google Slides presentation** titled:
**"{{PRESENTATION_TITLE}}"**

Tell an engaging, accessible story based on **{{STORY_HOOK_TITLE}}** while proving the architectural capabilities of **{{TARGET_GCP_SERVICES}}** for **{{CUSTOMER_NAME}}**.

### Strict Content & Formatting Guardrails
1. **Use the Active Google Slides Template (`Template Mode`)**:
   - Inherit the Master Template's background, typography, and branding placeholders (`TITLE`, `TITLE_AND_TWO_COLUMNS`, `TITLE_ONLY`, `TITLE_AND_BODY`).
2. **Strictly Zero Code on Any Slide**:
   - Do **not** place SQL queries, CLI commands, shell scripts, JSON payloads, or Terraform HCL on any slide. Use visual cards, business result tables, and the captured Console screenshots in `../screenshots/{{DEMO_STEM}}/`.
3. **Consistent Visual Color Language**:
   - **Producer Plane (`{{PRODUCER_PROJECT_ALIAS}}`)**: Warm Amber (`#FEF7E0` fill, `#F9AB00` border).
   - **Consumer Plane (`{{CONSUMER_PROJECT_ALIAS}}`)**: Google Blue (`#E8F0FE` fill, `#1A73E8` border).
   - **Governance / Exchange / Clean Room Bridge**: Deep Purple (`#F3E8FD` fill, `#9334E6` border).
   - **Security Enforcement Callouts**: Crimson Red (`#FCE8E6` / `#D93025`) for blocked/masked actions and Emerald Green (`#E6F4EA` / `#1E8E3E`) for authorized governed outcomes.
4. **Four Mandatory Elements per Content Slide**:
   - Action Title & Subtitle
   - Structured Visual Canvas (referencing companion diagram or screenshot where applicable)
   - Bottom "Bumper Sticker" Takeaway Banner
   - Conversational Speaker Notes

---

## 2. Deck Overview ({{SLIDE_COUNT}}-Slide Storyboard)

| Slide # | Template Layout | Slide Title | Story Beat / Demo Act | Companion Visual Asset | Core Message ("The Bumper Sticker") |
| :---: | :--- | :--- | :--- | :--- | :--- |
| **1** | `TITLE` | **{{SLIDE_1_TITLE}}** | Cover & Hook | — | {{SLIDE_1_BUMPER}} |
| **2** | `TITLE_AND_TWO_COLUMNS` | **{{SLIDE_2_TITLE}}** | Problem & {{CUSTOMER_NAME}} Parallel | — | {{SLIDE_2_BUMPER}} |
| **3** | `TITLE_ONLY` | **{{SLIDE_3_TITLE}}** | Architecture Blueprint | [`architecture-flow.png`](../diagrams/{{DEMO_STEM}}/architecture-flow.png) | {{SLIDE_3_BUMPER}} |
| **4** | `TITLE_AND_TWO_COLUMNS` | **{{SLIDE_4_TITLE}}** | Act 1 ({{ACT_1_PERSONA}}) | [`act-01-{{ACT_1_SLUG}}.png`](../screenshots/{{DEMO_STEM}}/act-01-{{ACT_1_SLUG}}.png) | {{SLIDE_4_BUMPER}} |
| **5** | `TITLE_AND_TWO_COLUMNS` | **{{SLIDE_5_TITLE}}** | Act 2 ({{ACT_2_PERSONA}}) | [`act-02-{{ACT_2_SLUG}}.png`](../screenshots/{{DEMO_STEM}}/act-02-{{ACT_2_SLUG}}.png) | {{SLIDE_5_BUMPER}} |
| **6** | `TITLE_ONLY` | **{{SLIDE_6_TITLE}}** | Act 3 (Security Contrast) | [`act-03a-{{ACT_3A_SLUG}}.png`](../screenshots/{{DEMO_STEM}}/act-03a-{{ACT_3A_SLUG}}.png) | {{SLIDE_6_BUMPER}} |
| **7** | `TITLE_AND_TWO_COLUMNS` | **{{SLIDE_7_TITLE}}** | Wrap-Up & {{CUSTOMER_NAME}} Roadmap | — | {{SLIDE_7_BUMPER}} |

---

## 3. Slide-by-Slide Content, Visual Instructions & Speaker Notes

### Slide 1 — {{SLIDE_1_TITLE}}

* **Google Slides Template Layout:** `TITLE`
* **On-Slide Text:**
  * **Main Title:** {{PRESENTATION_TITLE}}
  * **Subtitle:** {{PRESENTATION_SUBTITLE}}
* **Speaker Notes:**
  > "{{SLIDE_1_SPEAKER_NOTES}}"

---

### Slide 4 — {{SLIDE_4_TITLE}}

* **Google Slides Template Layout:** `TITLE_AND_TWO_COLUMNS`
* **Left Column — Story Beat Summary (Zero Code):**
  * {{ACT_1_SLIDE_BULLETS}}
* **Right Column — Live GCP Console Capture:**
  * Embed screenshot: ![Act 1 Screenshot](../screenshots/{{DEMO_STEM}}/act-01-{{ACT_1_SLUG}}.png)
* **Bottom Bumper Sticker Banner:**
  * *{{SLIDE_4_BUMPER}}*
* **Speaker Notes:**
  > "{{SLIDE_4_SPEAKER_NOTES}}"

