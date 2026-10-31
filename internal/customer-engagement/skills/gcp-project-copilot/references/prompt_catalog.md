# Prompt Examples Catalog (`gcp-project-copilot`)

Use the prompt examples below to execute specific workflows governed by the `gcp-project-copilot` skill across any customer workspace.

---

## 1. Scaffold & Setup a Brand-New Customer Workspace
```text
Use the gcp-project-copilot skill to scaffold and initialize this workspace for our new customer project:
- Customer: <Customer Name> (<customer.com>)
- Project: <Project Name> (<Program Name>)
- Pilot Domain: <Pilot Domain>
- Root Project Google Drive Folder: https://drive.google.com/drive/folders/<FOLDER_ID>

Scaffold `specs/` and `project/{common,meetings,working-process,questions-answered,deliverables}`, customize `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`, and initialize the 5 living master documents in `project/common/`.
```

---

## 2. Bootstrap a New Customer Workspace Directly from a Kickoff Meeting Google Doc
```text
I am starting a new customer project. Use the gcp-project-copilot skill to bootstrap this workspace from our first kickoff meeting notes:
https://docs.google.com/document/d/<KICKOFF_DOC_ID>
and configure our Google Drive folder:
https://drive.google.com/drive/folders/<ROOT_FOLDER_ID>

1. Scaffold the workspace (`specs/` and `project/{common,meetings,working-process,questions-answered,deliverables}`) and populate `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`.
2. Generate the first session's `questions-log` and `challenges` files in `project/meetings/`.
3. Populate all 5 living master documents in `project/common/`.
```

---

## 3. Customize or Update `specs/specs_project.md` & `specs/gdrive_sync_manifest.json`
```text
Use the gcp-project-copilot skill to customize @specs/specs_project.md and @specs/gdrive_sync_manifest.json:
- Set the Root Project Drive Folder to: https://drive.google.com/drive/folders/<NEW_FOLDER_ID>
- Set the Meeting Notes Folder to: https://drive.google.com/drive/folders/<NOTES_FOLDER_ID>
- Discover any existing Drive subfolders and keep `specs_project.md` and `gdrive_sync_manifest.json` synchronized.
```

---

## 4. Analyze a Single New Meeting (Session Outputs + Upsert `project/common/`)
```text
Use the gcp-project-copilot skill and @specs/specs_project.md to analyze this new meeting notes document:
https://docs.google.com/document/d/<DOC_ID>

Generate the session `questions-log` and `challenges` files in `project/meetings/` and update all 5 living project files in `project/common/` (including `project_members.md` and `project_glossary.md`). Hold Google Drive sync until I review the generated files.
```

---

## 5. Analyze Multiple Meetings in Chronological Order (Batch Backfill)
```text
Use the gcp-project-copilot skill and @specs/specs_project.md to analyze the following meeting notes in chronological order:
1. https://docs.google.com/document/d/<DOC_ID_1>
2. https://docs.google.com/document/d/<DOC_ID_2>

For each meeting, generate its `questions-log` and `challenges` files under `project/meetings/YYYY-MM-DD_<slug>/` with deep-linked transcript timestamps, and consolidate all members, glossary terms, questions, and challenges into `project/common/`.
```

---

## 6. Update Only the Project Glossary & Members from a Document or Transcript
```text
Use the gcp-project-copilot skill to scan this document:
https://docs.google.com/document/d/<DOC_ID>

Extract any new business concepts, source systems, domain terms, or participants and upsert them into @project/common/project_glossary.md and @project/common/project_members.md (storing any ASR phonetic aliases exclusively in @specs/specs_project.md).
```

---

## 7. Deep-Dive Topic Exploration in `project/working-process/`
```text
Using the gcp-project-copilot skill and based on @project/common/project_challenges.md, @project/common/project_questions-log.md, and @specs/specs_project.md, initialize a deep-dive working-process folder under `project/working-process/<topic-slug>/docs/` for Domain <D#>.
1. Create an exploratory architectural analysis in `project/working-process/<topic-slug>/docs/` addressing the customer questions and challenges raised so far on this topic.
2. Link the new working document back into @project/common/project_challenges.md and @specs/specs_project.md.
```

---

## 8. Answer One or More Technical Questions Using Workspace GCP Skills (`project/questions-answered/`)
```text
Use the gcp-project-copilot skill to evaluate and answer question(s) <D#-Q##> (or all questions in domain <D#>) from @project/common/project_questions-log.md:
1. Read the matching active external Google Cloud skills (`SKILL.md` + `references/*.md`) via `read_file` before authoring, and use `retrieving-developer-knowledge` to verify any CLI flag, SQL DDL option, YAML/JSON schema, or IAM permission not verbatim in a local skill.
2. Save an individual structured answer file per question in `project/questions-answered/` strictly following `resources/templates/template_answers_to_questions.md` (never list `gcp-project-copilot` or other `agyhub` internal/IDE meta-skills in Section 6; map 100% of `§2.x` code blocks and `§3.1` in Section 6; if delegating to subagents, require each subagent to read `template_answers_to_questions.md` and all cited `SKILL.md` files first) and verify with `scripts/validate_question_answers.py --require-active-skills`.
3. Cross-link the answer(s) in @project/common/project_questions-log.md.
```

---

## 9. Synthesize a Clean Customer-Facing Deliverable (`project/deliverables/`)
```text
Use the gcp-project-copilot skill to synthesize a final customer-facing deliverable in `project/deliverables/docs/<deliverable-stem>.md` based on our working-process analysis in @project/working-process/<topic-slug>/docs/<source-doc>.md:
1. Follow `resources/templates/template_deliverable.md` and place companion GCP Reference Architecture diagrams under `project/deliverables/diagrams/<deliverable-stem>/`.
2. Ensure the deliverable is 100% customer-ready and PDF-clean: remove all inline `[D#-Q##]` question codes and internal document links from the headers and Sections 1–5, keep only public official Google Cloud links in Section 6.1, and list internal working source filenames (without URLs) in Section 6.2.
3. Validate with `scripts/validate_deliverables.py` and link the deliverable in @project/common/project_challenges.md.
```

---

## 10. Export the Cumulative Question List to CSV for Google Sheets (`project/questions-answered/question-list.csv`)
```text
Use the gcp-project-copilot skill to export all coded questions from @project/common/project_questions-log.md into `project/questions-answered/question-list.csv` (`Updated,Code,Section,Asked By,Session Date,Question`) for Google Sheets import.
```

---

## 11. Synchronize Local `project/` (or Specific Subfolders) with Google Drive
```text
Use the gcp-project-copilot skill to synchronize all new or modified folders and Markdown documents in @project (or only `project/questions-answered/` or `project/deliverables/`) with Google Drive and update @specs/gdrive_sync_manifest.json.
```
