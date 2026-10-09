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

Scaffold `specs/` and `project/{common,meetings,topics}`, customize `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`, and initialize the 5 living master documents in `project/common/`.
```

---

## 2. Bootstrap a New Customer Workspace Directly from a Kickoff Meeting Google Doc
```text
I am starting a new customer project. Use the gcp-project-copilot skill to bootstrap this workspace from our first kickoff meeting notes:
https://docs.google.com/document/d/<KICKOFF_DOC_ID>
and synchronize it with our Google Drive folder:
https://drive.google.com/drive/folders/<ROOT_FOLDER_ID>

1. Scaffold the workspace (`specs/` and `project/{common,meetings,topics}`) and populate `specs/specs_project.md` and `specs/gdrive_sync_manifest.json`.
2. Generate the first session's `questions-log` and `challenges` files in `project/meetings/`.
3. Populate all 5 living master documents in `project/common/` and synchronize `project/` to Google Drive.
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

## 4. Analyze a Single New Meeting (Full Workflow: Session Outputs + Sync `project/common/` & Google Drive)
```text
Use the gcp-project-copilot skill and @specs/specs_project.md to analyze this new meeting notes document:
https://docs.google.com/document/d/<DOC_ID>

Generate the session `questions-log` and `challenges` files in `project/meetings/`, synchronize all 5 living project files in `project/common/` (including `project_members.md` and `project_glossary.md`), and sync `project/` to Google Drive.
```

---

## 5. Analyze Multiple Meetings in Chronological Order (Batch Backfill)
```text
Use the gcp-project-copilot skill and @specs/specs_project.md to analyze the following meeting notes in chronological order:
1. https://docs.google.com/document/d/<DOC_ID_1>
2. https://docs.google.com/document/d/<DOC_ID_2>

For each meeting, generate its `questions-log` and `challenges` files under `project/meetings/YYYY-MM-DD_<slug>/` with deep-linked transcript timestamps, consolidate all members, glossary terms, questions, and challenges into `project/common/`, and sync `project/` to Google Drive.
```

---

## 6. Update Only the Project Glossary & Members from a Document or Transcript
```text
Use the gcp-project-copilot skill to scan this document:
https://docs.google.com/document/d/<DOC_ID>

Extract any new business concepts, source systems, domain terms, or participants and upsert them into @project/common/project_glossary.md and @project/common/project_members.md (storing any ASR phonetic aliases exclusively in @specs/specs_project.md).
```

---

## 7. Promote a Topic Challenge into a Deep-Dive Workstream (`project/topics/`)
```text
Using the gcp-project-copilot skill and based on @project/common/project_challenges.md, @project/common/project_questions-log.md, and @specs/specs_project.md, initialize a new deep-dive workstream folder under `project/topics/<topic-slug>/docs/` for Domain <D#>.
1. Create a comprehensive architectural evaluation in `project/topics/<topic-slug>/docs/` addressing all customer questions and challenges raised so far on this topic.
2. Link the new deliverable back into @project/common/project_challenges.md and @specs/specs_project.md, and sync to Google Drive.
```

---

## 8. Synchronize Local `project/` Hierarchy with Google Drive
```text
Use the gcp-project-copilot skill to synchronize all new or modified folders and Markdown documents in @project with Google Drive, and refresh the synchronized registry in @specs/specs_project.md.
```
