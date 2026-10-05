# Antigravity Skills & Plugins Hub

A centralized, zero-copy repository for maintaining, developing, version-controlling, and distributing Antigravity skills, official Google skill suites, and plugins across teams.

---

## Quick Start & Installation

### 1. Clone the Repository
```bash
# Clone with all upstream submodules included:
git clone --recurse-submodules https://github.com/sogire/skills-hub.git
cd skills-hub

# Run the 1-click installer:
./install.sh
```

> **Note**: If you already cloned without `--recurse-submodules`, running `./install.sh` will automatically fetch and initialize all submodules for you.

### 2. System Requirements
- **Python**: `>= 3.10`
  - **Zero pip dependencies**: `ag-hub` is implemented entirely using the Python 3 Standard Library. No `pip install` or virtual environment required.
- **Git**: `>= 2.25` (with submodule support).

---

## Included Skill Repositories

The hub is organized into two primary domains: **`external/`** for read-only upstream Git submodules tracking GitHub releases, and **`internal/`** for your team's proprietary custom skills, rules, and plugins:

| Domain / Folder | Upstream / Source | Description | Skills Count |
| :--- | :--- | :--- | :--- |
| [`external/googlecloud-data/`](external/googlecloud-data) | [GoogleCloudPlatform/data-agent-kit-plugin](https://github.com/GoogleCloudPlatform/data-agent-kit-plugin) | Data Agent Kit: Dataform, dbt, Spark, Composer, Lakehouse, Graph | 37 skills |
| [`external/googlecloud-base/`](external/googlecloud-base) | [google/skills](https://github.com/google/skills) | BigQuery, Cloud Build, Vertex AI, AlloyDB, Ads, Analytics | ~144 skills |
| [`external/deepmind-science/`](external/deepmind-science) | [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | AlphaFold, PubMed, ChEMBL, UniProt, ClinVar, Foldseek, BLAST | 40 skills |
| [`external/agents-cli/`](external/agents-cli) | [google/agents-cli](https://github.com/google/agents-cli) | Google Agent Development Kit (ADK), Scaffold, Deploy, Eval | 7 skills |
| [`internal/skills/`](internal/skills) | Internal Custom Skills | Standalone custom skills authored for your projects | Extensible |
| [`internal/rules/`](internal/rules) | Internal Custom Rules | Always-on coding standards and architectural policies | Extensible |
| [`internal/plugins/`](internal/plugins) | Internal Custom Plugins | Multi-skill and rule packages with `plugin.json` | Extensible |

---

## Directory Structure

```text
skills-hub/
├── .git/                          # Track customizations with Git
├── .gitmodules                    # Submodule definitions tracking upstream main branches
├── .gitignore                     # Git exclusions
├── README.md                      # This documentation
│
├── external/                      # [Upstream Git Submodules]
│   ├── googlecloud-data/          # Submodule: GoogleCloudPlatform/data-agent-kit-plugin
│   │   └── skills/                # dataform, dbt, spark, dataflow, airflow, etc.
│   ├── googlecloud-base/          # Submodule: google/skills
│   │   ├── skills/cloud/          # bigquery, vertex, alloydb, etc.
│   │   ├── skills/ads/            # ads API skills
│   │   └── skills/analytics/      # GA4 / analytics skills
│   ├── deepmind-science/          # Submodule: google-deepmind/science-skills
│   │   └── skills/                # alphafold, pubmed, chembl, etc.
│   └── agents-cli/                # Submodule: google/agents-cli
│       └── skills/                # ADK code, deploy, eval, workflow
│
├── internal/                      # [Proprietary / In-House Customizations]
│   ├── hub-tools/                 # Meta-tooling skills (role design, gap authoring)
│   │   ├── cluster-role-creation/ # Agent skill for designing role clusters & docs
│   │   └── skills-gaps-creator/   # Agent skill for authoring missing/gap skills
│   ├── skills/                    # General / Uncategorized fallback skills
│   │   └── template-skill/
│   ├── rules/                     # Shared AGENTS.md rule presets
│   │   └── general-standards.md
│   └── plugins/                   # Bundled plugins (plugin.json)
│       └── template-plugin/
│
├── clusters/                      # [Curated Skill Clusters across Internal & External sources]
│   ├── gcp-data-enterprise-architect.json # Lakehouse, Data Mesh, Governance, Lineage, FinOps, Security
│   ├── gcp-data-enterprise-architect.md   # Architectural blueprint & role documentation
│   ├── data-engineer.json         # BigQuery, dbt, Spark, Dataform
│   ├── science-researcher.json    # AlphaFold, PubMed, ChEMBL, UniProt, Clinical Trials
│   └── agent-developer.json       # ADK code, eval, deploy, workflow, template-skill
│
└── bin/
    └── ag-hub                     # CLI tool (symlinked to ~/.local/bin/ag-hub)
```

---

## `ag-hub` CLI Guide

You can run `ag-hub` from any project terminal. All changes use **zero file copies** by default through Antigravity workspace manifests (`.agents/skills.json` and `.agents/plugins.json`).

### 1. Enabling Groups (`-g` / `--group`)

Instead of enabling skills one by one, you can activate entire suites or categories with `-g` or `--group`:

```bash
# Enable an entire external suite (names or full group paths work):
ag-hub enable -g agents-cli
# or:
ag-hub enable -g external/agents-cli

# Enable all 37 Data Agent Kit skills (Dataform, dbt, Spark, etc.)
ag-hub enable -g googlecloud-data

# Enable all DeepMind science skills (AlphaFold, PubMed, BLAST, etc.)
ag-hub enable -g deepmind-science

# Enable all internal proprietary skills across all typologies
ag-hub enable -g internal

# Enable a specific internal typology group (e.g. hub meta-tooling)
ag-hub enable -g hub-tools

# Enable all general Google Cloud base skills
ag-hub enable -g googlecloud-base

# Or enable a specific subcategory within googlecloud-base:
ag-hub enable -g cloud
ag-hub enable -g ads
ag-hub enable -g analytics

# Combine a group with individual skills from other suites:
ag-hub enable -g agents-cli dbt-bigquery alphafold_database_fetch_and_analyze
```

#### Available Groups Overview

| Group Name | Skills Count | Provenance | Typical Use Cases |
| :--- | :--- | :--- | :--- |
| `external/agents-cli` (or `agents-cli`) | 7 | Upstream | Developing, testing, evaluating, and deploying ADK agents |
| `external/googlecloud-data` (or `googlecloud-data`) | 37 | Upstream | Data engineering, ETL, dbt, Dataform, Dataproc Spark, Airflow |
| `external/deepmind-science` (or `deepmind-science`) | 40 | Upstream | Bioinformatics, protein structure, literature search, chemistry |
| `external/googlecloud-base` (or `googlecloud-base`) | ~144 | Upstream | Vertex AI, AlloyDB, BigQuery, IAM, Cloud Build, Ads & Analytics |
| `internal` (or `internal/skills`) | Extensible | Internal | Proprietary custom skills authored in `skills-hub/internal/skills/` |

#### Disabling Groups

To deactivate an entire group from your workspace:

```bash
# Deactivate all skills belonging to agents-cli
ag-hub disable -g agents-cli

# Deactivate all data engineering skills
ag-hub disable -g googlecloud-data

# Deactivate all internal skills
ag-hub disable -g internal
```

---

### 2. Curated Skill Clusters (`-c` / `--cluster` & `ag-hub cluster`)

While `--group` enables all skills from a single repository or category, **Clusters** allow you to activate a curated subset of skills tailored for specific engineering roles, personas, or workflows across **multiple repositories** (combining internal and external skills):

| Predefined Cluster | Description | Included Skill Sources |
| :--- | :--- | :--- |
| `gcp-data-enterprise-architect` | Lakehouse & Data Mesh, Dataplex governance & lineage, WAF, FinOps, zero-trust security | `external/googlecloud-base`, `external/googlecloud-data` |
| `data-engineer` | BigQuery, dbt, Spark, Dataform, BigQuery optimization | `external/googlecloud-data`, `external/googlecloud-base` |
| `science-researcher` | AlphaFold, PubMed, ChEMBL, UniProt, Clinical Trials | `external/deepmind-science` |
| `agent-developer` | ADK code, eval, deploy, workflow, template-skill | `external/agents-cli`, `internal/skills` |

#### Cluster Commands
```bash
# List all available clusters and their activation status in current workspace
ag-hub cluster list
# or:
ag-hub clusters

# Inspect a cluster's skills and status
ag-hub cluster info data-engineer
ag-hub cluster info science-researcher

# Activate a cluster in current workspace
ag-hub enable -c data-engineer
# or:
ag-hub cluster enable data-engineer

# Activate multiple clusters or combine clusters with individual skills:
ag-hub enable -c data-engineer -c agent-developer accidental-data-loss-prevention

# Deactivate a cluster from current workspace
ag-hub disable -c data-engineer
# or:
ag-hub cluster disable data-engineer

# Create a new custom cluster template
ag-hub create cluster ml-ops
```

#### Predefining Custom Clusters (JSON & YAML)
Clusters are configured via simple JSON files (or standard YAML) with zero external dependencies. You can place cluster definitions in:
- **Hub-wide clusters**: `clusters/<name>.json` or `internal/clusters/<name>.json`
- **Catalog file**: `clusters.json` in the hub root
- **Workspace-local clusters**: `<workspace>/.agents/clusters/<name>.json`

Example definition (`clusters/data-engineer.json`):
```json
{
  "name": "data-engineer",
  "description": "GCP Data Engineering and ETL toolset (BigQuery, dbt, Spark, Dataform)",
  "skills": [
    "bigquery-sql",
    "dbt-bigquery",
    "gcp-spark",
    "dataform-bigquery",
    "bigquery-optimization"
  ],
  "plugins": []
}
```

#### Companion Role Documentation (`clusters/<name>.md`)
Clusters can be accompanied by human-readable markdown guides (e.g. [`clusters/gcp-data-enterprise-architect.md`](clusters/gcp-data-enterprise-architect.md)) documenting:
1. **Role Definition & Core Architectural Pillars** (with Mermaid architecture topology).
2. **Skill Breakdown by Competency** (matrix of skills, architectural rationale, and provenance).
3. **Missing Skills Analysis (Catalog Gaps)** (roadmaps for authoring missing skills in `internal/<typology>/`).

> [!TIP]
> **Need help creating clusters?** Enable the internal skill [`cluster-role-creation`](internal/hub-tools/cluster-role-creation/SKILL.md) (`ag-hub enable cluster-role-creation`) to have an agent interview you, explore the catalog, identify missing skills, and automatically generate both the JSON manifest and Markdown blueprint.
>
> **Need to build a missing skill or resolve a role gap?** Enable the internal skill [`skills-gaps-creator`](internal/hub-tools/skills-gaps-creator/SKILL.md) (`ag-hub enable skills-gaps-creator`) as an independent, standalone task anytime. An agent will grill you on boundaries, ingest documentation links (web URLs or local files), and author a complete, verified skill under `internal/<typology>/<name>/` (e.g. `internal/data-platform/<name>/`).

---

### 3. Catalog Browsing & Searching

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

### 4. Inspecting Skill Documentation (`info` / `show`)

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

### 5. Activating & Checking Workspace Status

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

### 6. Global Skills across All Workspaces (`-G` / `--global`)

Antigravity natively supports machine-wide customizations loaded into **every** project workspace from `~/.gemini/config/`. With `ag-hub`, you can promote any skill, cluster, or group to be globally active with zero file copies:

```bash
# Enable an individual skill globally (e.g., safety guardrails)
ag-hub enable -G accidental-data-loss-prevention

# Enable a cluster globally across all workspaces
ag-hub enable -G -c agent-developer

# Enable an entire group globally (e.g., all 7 Agent Development Kit tools everywhere)
ag-hub enable -G -g agents-cli

# Check global customizations
ag-hub status -G

# Normal workspace status also displays inherited global skills:
ag-hub status

# Disable an individual skill globally
ag-hub disable -G google-agents-cli-scaffold

# Disable an entire cluster globally
ag-hub disable -G -c agent-developer

# Disable an entire group globally
ag-hub disable -G -g agents-cli

# Reset all global hub customizations (preserves core system plugins like Chrome DevTools)
ag-hub disable -G --all
```

> [!TIP]
> Global skills are registered via `~/.gemini/config/skills.json` pointing directly to your local hub repository. They are inherited by all existing and future Antigravity workspaces on this machine.

---

### 7. Workspace Resolution & Directory Targeting

`ag-hub` gives you complete control over which directory is treated as your target workspace:

1. **Current Directory by Default**:
   By default, `ag-hub` executes strictly in the **current working directory** where you invoke it (`cwd`), creating or modifying `.agents/` right there:
   ```bash
   cd ~/my-monorepo/packages/backend
   ag-hub enable -c data-engineer   # Configures ~/my-monorepo/packages/backend/.agents/
   ```

2. **Search for Git / Agents Root (`-r` / `--find-root`)**:
   If you are deep in a subdirectory of a project and want `ag-hub` to search parent directories upward for the `.git` or `.agents` workspace root:
   ```bash
   cd ~/my-monorepo/packages/backend/src/controllers
   ag-hub status -r                 # Automatically targets ~/my-monorepo
   ag-hub enable -r -c data-engineer
   ```

3. **Explicit Workspace Target (`-w` / `--workspace`)**:
   You can target any workspace directory from anywhere without `cd`:
   ```bash
   # Enable skills in another project
   ag-hub -w ~/local_projects/my-data-pipeline enable -c data-engineer

   # Check active status of another project
   ag-hub -w ~/local_projects/my-agent status

   # Reset customizations in another project
   ag-hub -w ~/local_projects/my-agent disable --all
   ```

---

### 8. Interactive Selection (`select` / `-i`)

```bash
ag-hub select
# or:
ag-hub -i
```
Launches an interactive menu with keyword filtering and numbered toggle switches.

---

### 9. Updating Repositories from GitHub Upstream

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

### 10. Registering New Upstream Repositories (`add-repo`)

Discovered a new GitHub repository with Antigravity skills? Register it into the hub with one command:

```bash
# Clone and register a new GitHub skills repo as a submodule
ag-hub add-repo https://github.com/example-org/genai-skills.git

# Specify custom folder name and branch:
ag-hub add-repo https://github.com/example-org/genai-skills.git custom-genai --branch main
```

---

### 11. Alternative Symlink Mode (`--symlink` / `-s`)

If your workflow requires direct file-system symlinks in `.agents/skills/` instead of `.agents/skills.json`:

```bash
# Symlink individual skills
ag-hub enable --symlink bigquery-sql

# Symlink an entire cluster
ag-hub enable --symlink -c data-engineer

# Symlink an entire group
ag-hub enable --symlink -g agents-cli
```

---

### 12. Authoring New Custom Skills, Plugins & Clusters in the Hub

```bash
# Scaffold a new skill in a specific typology group (e.g. skills-hub/internal/hub-tools/<name> or data-platform/<name>)
ag-hub create skill my-specialized-tool -g data-platform

# Scaffold in general skills-hub/internal/skills/<name> (default)
ag-hub create skill my-specialized-tool

# Scaffold a new plugin in skills-hub/internal/plugins/<name>
ag-hub create plugin my-specialized-plugin

# Scaffold a new cluster definition in skills-hub/clusters/<name>.json
ag-hub create cluster my-project-team
```

