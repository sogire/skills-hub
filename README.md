# Antigravity Skills & Plugins Hub

A centralized, zero-copy repository for maintaining, developing, and version-controlling custom Antigravity skills, official Google skill suites, and plugins.

---

## Included Skill Repositories

The hub is powered by Git submodules tracking official upstream repositories on their `main` branches:

| Folder | Upstream Repository | Description | Skills Count |
| :--- | :--- | :--- | :--- |
| [`googlecloud-data/`](file:///home/sergiobermudez/local_projects/skills-hub/googlecloud-data) | [GoogleCloudPlatform/data-agent-kit-plugin](https://github.com/GoogleCloudPlatform/data-agent-kit-plugin) | Data Agent Kit: Dataform, dbt, Spark, Composer, Lakehouse, Graph | 37 skills |
| [`googlecloud-base/`](file:///home/sergiobermudez/local_projects/skills-hub/googlecloud-base) | [google/skills](https://github.com/google/skills) | BigQuery, Cloud Build, Vertex AI, AlloyDB, Ads, Analytics | ~144 skills |
| [`deepmind-science/`](file:///home/sergiobermudez/local_projects/skills-hub/deepmind-science) | [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | AlphaFold, PubMed, ChEMBL, UniProt, ClinVar, Foldseek, BLAST | 40 skills |
| [`agents-cli/`](file:///home/sergiobermudez/local_projects/skills-hub/agents-cli) | [google/agents-cli](https://github.com/google/agents-cli) | Google Agent Development Kit (ADK), Scaffold, Deploy, Eval | 7 skills |
| [`skills/`](file:///home/sergiobermudez/local_projects/skills-hub/skills) | Local Custom Skills | Your own custom authored standalone skills | Extensible |
| [`plugins/`](file:///home/sergiobermudez/local_projects/skills-hub/plugins) | Local Custom Plugins | Multi-skill and rule packages with `plugin.json` | Extensible |

---

## Directory Structure

```text
skills-hub/
├── .git/                     # Track customizations with Git
├── .gitmodules               # Submodule definitions tracking upstream main branches
├── README.md                 # This documentation
├── googlecloud-data/         # Submodule: GoogleCloudPlatform/data-agent-kit-plugin
│   └── skills/               # dataform, dbt, spark, dataflow, airflow, etc.
├── googlecloud-base/         # Submodule: google/skills
│   ├── skills/cloud/         # bigquery, vertex, alloydb, etc.
│   ├── skills/ads/           # ads API skills
│   └── skills/analytics/     # GA4 / analytics skills
├── deepmind-science/         # Submodule: google-deepmind/science-skills
│   └── skills/               # alphafold, pubmed, chembl, etc.
├── agents-cli/               # Submodule: google/agents-cli
│   └── skills/               # ADK code, deploy, eval, workflow
├── skills/                   # Standalone local skills
│   └── template-skill/
├── plugins/                  # Bundled plugins
│   └── template-plugin/
├── rules/                    # Shared AGENTS.md rule presets
└── bin/
    └── ag-hub                # CLI tool (symlinked to ~/.local/bin/ag-hub)
```

---

## `ag-hub` CLI Guide

You can run `ag-hub` from any project terminal. All changes use **zero file copies** by default through Antigravity workspace manifests (`.agents/skills.json` and `.agents/plugins.json`).

### 1. Enabling Groups (`-g` / `--group`)

Instead of enabling skills one by one, you can activate entire suites or categories with `-g` or `--group`:

```bash
# Enable all 7 Google Agent Development Kit skills
ag-hub enable -g agents-cli

# Enable all 37 Data Agent Kit skills (Dataform, dbt, Spark, etc.)
ag-hub enable -g googlecloud-data

# Enable all DeepMind science skills (AlphaFold, PubMed, BLAST, etc.)
ag-hub enable -g deepmind-science

# Enable all general Google Cloud base skills
ag-hub enable -g googlecloud-base

# Or enable a specific subcategory within googlecloud-base:
ag-hub enable -g googlecloud-base/cloud
ag-hub enable -g googlecloud-base/ads
ag-hub enable -g googlecloud-base/analytics

# Combine a group with individual skills from other suites:
ag-hub enable -g agents-cli dbt-bigquery alphafold_database_fetch_and_analyze
```

#### Available Groups Overview

| Group Name | Skills Count | Typical Use Cases |
| :--- | :--- | :--- |
| `agents-cli` | 7 | Developing, testing, evaluating, and deploying ADK agents |
| `googlecloud-data` | 37 | Data engineering, ETL, dbt, Dataform, Dataproc Spark, Composer Airflow |
| `deepmind-science` | 40 | Bioinformatics, protein structure, literature search, chemistry |
| `googlecloud-base` | ~144 | Vertex AI, AlloyDB, BigQuery, IAM, Cloud Build, Ads & Analytics |
| `custom` | Extensible | Standalone custom skills authored in `skills-hub/skills/` |

#### Disabling Groups

To deactivate an entire group from your workspace:

```bash
# Deactivate all skills belonging to agents-cli
ag-hub disable -g agents-cli

# Deactivate all data engineering skills
ag-hub disable -g googlecloud-data
```

---

### 2. Catalog Browsing & Searching

```bash
# High-level summary of all repositories and active workspace skills
ag-hub list

# Search skills by keyword across all 200+ skills (e.g. bigquery, spark, alphafold, deploy)
ag-hub list bigquery
ag-hub list spark
ag-hub list alphafold

# Filter catalog by group/repository
ag-hub list -g googlecloud-data
ag-hub list -g deepmind-science
ag-hub list -g cloud

# List all 220+ skills in full detail
ag-hub list --all
```

---

### 3. Inspecting Skill Documentation (`info` / `show`)

Inspect the full documentation, triggers, and prompt guidelines for any skill directly from the terminal without opening files:

```bash
# View documentation for a skill
ag-hub info accidental-data-loss-prevention
# or:
ag-hub show dbt-bigquery
ag-hub describe google-agents-cli-adk-code

# View plugin details and bundled skills
ag-hub info dak
```

---

### 4. Activating & Checking Workspace Status

```bash
# Check what skills and plugins are currently active in this workspace
ag-hub status

# Enable individual skills
ag-hub enable bigquery-sql dbt-bigquery gcp-spark

# Disable specific skills
ag-hub disable bigquery-sql

# Reset workspace: disable ALL active skills and plugins at once
ag-hub disable --all
```

---

### 5. Managing Any Workspace from Anywhere (`-w` / `--workspace`)

You don't need to be in a project folder to manage its skills. Use `-w <path>` to target any workspace directory:

```bash
# Enable skills in another project
ag-hub -w ~/local_projects/my-data-pipeline enable -g googlecloud-data

# Check active status of another project
ag-hub -w ~/local_projects/my-agent status

# Reset customizations in another project
ag-hub -w ~/local_projects/my-agent disable --all
```

---

### 6. Interactive Selection (`select` / `-i`)

```bash
ag-hub select
# or:
ag-hub -i
```
Launches an interactive menu with keyword filtering and numbered toggle switches.

---

### 7. Updating Repositories from GitHub Upstream

Keep all skills updated with the latest releases from their official upstream GitHub repositories:

```bash
# Check if new commits exist upstream without pulling
ag-hub update --check

# Pull and merge latest commits for all submodules from origin/main
ag-hub update

# Update a specific repository only
ag-hub update googlecloud-data
ag-hub update googlecloud-base
ag-hub update deepmind-science
ag-hub update agents-cli
```

---

### 8. Registering New Upstream Repositories (`add-repo`)

Discovered a new GitHub repository with Antigravity skills? Register it into the hub with one command:

```bash
# Clone and register a new GitHub skills repo as a submodule
ag-hub add-repo https://github.com/example-org/genai-skills.git

# Specify custom folder name and branch:
ag-hub add-repo https://github.com/example-org/genai-skills.git custom-genai --branch main
```

---

### 9. Alternative Symlink Mode (`--symlink` / `-s`)

If your workflow requires direct file-system symlinks in `.agents/skills/` instead of `.agents/skills.json`:

```bash
# Symlink individual skills
ag-hub enable --symlink bigquery-sql

# Symlink an entire group
ag-hub enable --symlink -g agents-cli
```

---

### 10. Authoring New Custom Skills in the Hub

```bash
# Scaffold a new custom skill boilerplate in skills-hub/skills/<name>
ag-hub create skill my-specialized-tool

# Scaffold a new plugin in skills-hub/plugins/<name>
ag-hub create plugin my-specialized-plugin
```
