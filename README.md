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

You can run `ag-hub` from any project terminal:

### 1. Catalog Summary & Search
```bash
# View summary of all repositories and active skills in current workspace
ag-hub list

# Search skills by keyword (e.g. bigquery, alphafold, ads, deploy)
ag-hub list bigquery
ag-hub list alphafold

# Filter by repository or category group
ag-hub list -g deepmind-science
ag-hub list -g cloud

# List all 200+ skills
ag-hub list --all
```

### 2. Updating Skills from GitHub Upstream
Keep all repositories updated with the latest changes from their original GitHub repos:
```bash
# Check if updates are available remotely without pulling
ag-hub update --check

# Pull latest updates for all submodules from origin/main
ag-hub update

# Update a single repository
ag-hub update deepmind-science
ag-hub update googlecloud-base
ag-hub update agents-cli
```

### 3. Activating Skills in Your Workspace (Zero-Copy)
```bash
# Enable any combination of skills in the current workspace
ag-hub enable bigquery-basics alphafold_database_fetch_and_analyze google-agents-cli-adk-code

# Check active skills and plugins in current workspace
ag-hub status

# Deactivate skills
ag-hub disable alphafold_database_fetch_and_analyze
```

### 4. Interactive Selection
```bash
ag-hub select
# or: ag-hub -i
```
Launches an interactive menu with optional search filter and numbered toggles.

### 5. Alternative Symlink Mode
If you prefer direct symbolic links in `.agents/skills/`:
```bash
ag-hub enable --symlink bigquery-basics
```

### 6. Authoring New Skills in the Hub
```bash
ag-hub create skill my-custom-skill
ag-hub create plugin my-custom-plugin
```
