---
name: agyhub-agent
description: Expert guidance for AI agents to discover, inspect, enable, disable, configure, and troubleshoot Antigravity skills, clusters, groups, and plugins using the agyhub CLI. Use whenever an agent or user needs to manage workspace or global customizations, activate role clusters, query the catalog, update upstream repositories, or scaffold new skills in the hub.
---

# AGYHub Agent: Autonomous Skills Hub Navigator & CLI Operator

This skill equips an AI agent to act as an autonomous **Customizations Administrator** for the Antigravity Skills Hub. It provides operational workflows, rules of engagement, decision trees, and troubleshooting procedures for executing `agyhub` commands safely and effectively.

---

## When to Use This Skill

Activate this skill whenever:
- A user or prompt asks to activate, enable, or install a skill, cluster, plugin, or repository suite (e.g. "Enable BigQuery skills", "Activate the Data Engineer cluster", "Turn on DeepMind tools").
- A user asks to inspect what skills are active in the current project or machine-wide (`agyhub status`).
- A user or workflow asks what skills exist for a particular domain or technology (e.g. "Do we have dbt skills?", "What bioinformatics tools are available?").
- The agent needs to read a skill's instructions, prompts, or triggers before using it (`agyhub info <name>`).
- Customizations need to be deactivated or the workspace reset (`agyhub disable`).
- Multi-project workspaces need to be configured without changing directories (`--workspace` / `-w`).
- New skills, plugins, architectural rules, or clusters need to be scaffolded (`agyhub create`).
- Upstream Git repositories tracking GitHub releases need checking or updating (`agyhub update`).

---

## Core Architecture & Zero-Copy Mechanics

`agyhub` manages skills and plugins with **zero file copies** by default, leveraging Antigravity's native manifest resolution system:

```mermaid
flowchart TD
    subgraph Hub ["skills-hub Repository"]
        H_EXT["external/ (Upstream submodules)"]
        H_INT["internal/ (Proprietary typologies)"]
        H_CLU["clusters/ (Role manifests)"]
    end

    subgraph Target ["Target Workspace / Global"]
        M_SKILLS[".agents/skills.json (or ~/.gemini/config/skills.json)"]
        M_PLUGINS[".agents/plugins.json (or ~/.gemini/config/plugins.json)"]
        SYM[".agents/skills/ (Optional symlinks)"]
    end

    H_EXT -->|"Zero-copy path reference"| M_SKILLS
    H_INT -->|"Zero-copy path reference"| M_SKILLS
    H_CLU -->|"Batch enables to"| M_SKILLS
    Hub -->|"Symlink mode (-s)"| SYM
```

### 1. Zero-Copy Manifest Mode (Default & Recommended)
- Skills are registered as absolute directory references inside `.agents/skills.json`:
  ```json
  {
    "skills": [
      "/home/user/local_projects/skills-hub/external/googlecloud-data/skills/bigquery-sql",
      "/home/user/local_projects/skills-hub/internal/hub-tools/skills/agyhub-agent"
    ]
  }
  ```
- Plugins are registered similarly inside `.agents/plugins.json`.
- Files in upstream submodules remain completely untouched.

### 2. Symlink Mode (`--symlink` / `-s`)
- Creates direct filesystem symlinks in `.agents/skills/<name>` pointing back to the hub.
- Useful only when legacy tools or strict filesystem scanners require directory presence.

### 3. Scope Resolution & Priority
- **Workspace Scope (Default)**: Target directory `.agents/` takes precedence over machine-wide settings.
- **Global Scope (`-G` / `--global`)**: Registers skills in `~/.gemini/config/skills.json`. Global customizations are automatically inherited by all current and future Antigravity workspaces.

### 4. Automatic Antigravity Permissions
- Enabling skills or plugins automatically configures `read_file(<hub_path>)` in `~/.gemini/antigravity-cli/settings.json`.
- This ensures Antigravity agents can inspect skills, instructions, scripts, and reference files without triggering interactive permission prompts when working in external workspaces.
- To bypass automatic permission configuration (e.g. CI environments), pass `--no-permissions`.
- To clean up permissions when resetting a workspace, pass `--clean-permissions` to `agyhub disable`.

---

## Agent Rules of Engagement

When invoking `agyhub` from agent tools, follow these operational rules:

### Rule 1: Binary Path Resolution
- `agyhub` is symlinked to `~/.local/bin/agyhub` by `./install.sh`.
- If `agyhub` is in your shell `PATH`, run `agyhub <subcommand>`.
- **Fallback**: If `agyhub` is not found in `PATH`, invoke directly using Python:
  ```bash
  python3 <hub_root>/bin/agyhub <subcommand>
  ```

### Rule 2: Workspace Targeting without `cd`
- Coding agents should avoid using `cd` in commands because subshells may not preserve state.
- Always use the `-w` / `--workspace` flag to target a project directory:
  ```bash
  agyhub -w /path/to/project enable -c data-engineer
  agyhub -w /path/to/project status
  ```
- Alternatively, use `-r` / `--find-root` to auto-detect the `.git` or `.agents` workspace root if running from a deep subdirectory.

### Rule 3: Inspect Before Activating
- If uncertain about what a skill does or when it should be triggered, inspect its YAML frontmatter and documentation using:
  ```bash
  agyhub info <skill-name>
  ```
- This prevents loading irrelevant or conflicting skills.

### Rule 4: Match Granularity to Scope
- **Individual Skills** (`agyhub enable <name>`): Use for precise, targeted tasks (e.g. `bigquery-sql`).
- **Clusters** (`agyhub enable -c <cluster>`): Use when supporting a full engineering role or multi-tool persona (e.g. `data-engineer`, `gcp-data-enterprise-architect`).
- **Groups** (`agyhub enable -g <group>`): Use when a project requires an entire upstream repository (e.g. `agents-cli`, `googlecloud-data`, `deepmind-science`, `cloud`).

### Rule 5: Keep Global Scope Minimal
- Global activation (`-G` / `--global`) affects every project on the machine.
- Reserve global scope for safety guardrails (`accidental-data-loss-prevention`) or universal agent developer tools. Do not clutter global scope with specialized domain tools.

---

## The 7 Operational Playbooks

### Playbook 1: Catalog Search & Discovery

```bash
# 1. Summary of available repositories, clusters, and active workspace items:
agyhub list

# 2. Search by keyword across all 230+ skills:
agyhub list bigquery
agyhub list alphafold
agyhub list spark
agyhub list agent

# 3. Filter skills by repository or category:
agyhub list -g googlecloud-data
agyhub list -g deepmind-science
agyhub list -g cloud
agyhub list -g hub-tools

# 4. View entire 230+ catalog with descriptions:
agyhub list --all
```

> [!TIP]
> You can also consult [`CURRENT_SKILLS.md`](CURRENT_SKILLS.md) directly for an offline, organized index.

---

### Playbook 2: Skill & Plugin Inspection

Before activating an unknown skill, view its instructions, prompt triggers, and options:

```bash
# View documentation for a skill
agyhub info <skill-name>
# Aliases: agyhub show <skill-name>, agyhub describe <skill-name>

# View plugin manifest and bundled skills
agyhub info <plugin-name>
```

---

### Playbook 3: Workspace Status Check

Always verify the current state before adding or removing tools:

```bash
# Check local workspace active skills and plugins:
agyhub status

# Check targeted external workspace:
agyhub -w /path/to/project status

# Check machine-wide global customizations:
agyhub status -G
```

---

### Playbook 4: Enabling Customizations

Activate individual skills, clusters, or entire groups:

```bash
# Enable individual skills in workspace:
agyhub enable bigquery-sql dbt-bigquery

# Enable a curated role cluster:
agyhub enable -c data-engineer
# or:
agyhub cluster enable data-engineer

# Enable multiple clusters and individual skills together:
agyhub enable -c data-engineer -c agent-developer accidental-data-loss-prevention

# Enable an entire repository group:
agyhub enable -g agents-cli
agyhub enable -g googlecloud-data
agyhub enable -g deepmind-science

# Enable in a remote project workspace:
agyhub -w /path/to/project enable -c data-engineer

# Enable globally machine-wide:
agyhub enable -G accidental-data-loss-prevention
agyhub enable -G -c agent-developer

# Enable with symlinks instead of manifest:
agyhub enable --symlink -c data-engineer

# Enable without modifying Antigravity permissions (e.g. CI / automated pipelines):
agyhub enable --no-permissions -c data-engineer
```

---

### Playbook 5: Disabling & Resetting Customizations

```bash
# Disable specific skills:
agyhub disable bigquery-sql

# Disable an entire cluster:
agyhub disable -c data-engineer
# or:
agyhub cluster disable data-engineer

# Disable an entire group:
agyhub disable -g agents-cli

# Reset workspace: remove ALL active customizations in current project:
agyhub disable --all

# Reset workspace AND revoke external hub read permissions from Antigravity settings:
agyhub disable --all --clean-permissions

# Reset global customizations (preserves core system plugins like Chrome DevTools):
agyhub disable -G --all

# Disable in a specific workspace:
agyhub -w /path/to/project disable --all
```

---

### Playbook 6: Cluster Operations & Scaffolding

```bash
# List all clusters with active status and scope badges ([HUB] vs [WORKSPACE]):
agyhub cluster list
# or:
agyhub clusters

# Inspect cluster details, contained skills, and source path:
agyhub cluster info gcp-data-enterprise-architect
agyhub cluster info data-engineer

# Scaffold a new official hub cluster manifest (in clusters/):
agyhub create cluster mlops-platform

# Scaffold a workspace-specific cluster manifest (in .agents/clusters/):
agyhub create cluster my-project-role --local
# or:
agyhub cluster create my-project-role --local

# Enable/disable a cluster (works identically for [HUB] and [WORKSPACE] clusters):
agyhub enable -c my-project-role
agyhub disable -c my-project-role

# Scaffold a new skill in a specific typology (in internal/<typology>/skills/):
agyhub create skill my-tool -g data-platform

# Scaffold a workspace-local skill (in .agents/skills/):
agyhub create skill my-tool --local

# Scaffold a new plugin in a specific typology:
agyhub create plugin my-plugin -g data-platform

# Scaffold a new architectural rule:
agyhub create rule my-rule -g data-platform
```

> [!TIP]
> To interactively design a new cluster (either official in `clusters/` or workspace-specific in `.agents/clusters/`) with interview gates and companion documentation, use the companion skill [`agyhub-cluster-role-creation`](../agyhub-cluster-role-creation/SKILL.md). To author a missing skill, use [`agyhub-skills-gap-creator`](../agyhub-skills-gap-creator/SKILL.md).

---

### Playbook 7: Upstream Submodule Maintenance

```bash
# Check if new commits exist upstream without fetching:
agyhub update --check

# Pull latest commits for all upstream submodules from origin/main:
agyhub update

# Update a specific repository only:
agyhub update googlecloud-data
agyhub update googlecloud-base
agyhub update deepmind-science
agyhub update agents-cli

# Register a new upstream GitHub skills repository into the hub:
agyhub add-repo https://github.com/example-org/ai-skills.git [name] [--branch main]
```

---

## Agent Troubleshooting & Self-Healing Matrix

| Symptom / Error | Root Cause | Automated Resolution |
| :--- | :--- | :--- |
| `agyhub: command not found` | `~/.local/bin` not in `$PATH` | Invoke via `python3 <hub_dir>/bin/agyhub` or run `./install.sh`. |
| `Error: Skill '<name>' not found in catalog` | Typo or uninitialized submodules | 1. Run `agyhub list <query>` to search for closest name.<br>2. Run `git -C <hub_dir> submodule update --init --recursive` to ensure submodules are cloned. |
| `.agents/skills.json` contains duplicate entries | Multiple manual edits | Run `agyhub enable <skill>` or `agyhub disable <skill>`; `agyhub` automatically deduplicates and cleans manifests. |
| Workspace has broken symlinks | Hub moved to new directory | 1. Switch to manifest mode: `agyhub disable --all` followed by `agyhub enable -c <cluster>`.<br>2. Re-symlink: `agyhub enable --symlink -c <cluster>`. |
| Submodule in detached HEAD state | Upstream Git tracking | Run `agyhub update <repo>` to checkout and merge tracking branch. |

---

## Agent Command Reference Cheat Sheet

| Command | Shorthand / Aliases | Primary Arguments | Description |
| :--- | :--- | :--- | :--- |
| `agyhub list` | `ls` | `[query]`, `-g <group>`, `--all` | Browse or search skills catalog |
| `agyhub status` | | `-w <dir>`, `-G` | Display active workspace or global tools |
| `agyhub info` | `show`, `describe` | `<name>` | Display skill documentation and triggers |
| `agyhub enable` | `add` | `<names...>`, `-c <cluster>`, `-g <group>`, `-G`, `-s` | Activate customizations in scope |
| `agyhub disable` | `rm` | `<names...>`, `-c <cluster>`, `-g <group>`, `--all`, `-G` | Deactivate customizations in scope |
| `agyhub cluster` | `clusters` | `list`, `info <name>`, `enable <name>`, `disable <name>` | Manage predefined role clusters |
| `agyhub select` | `interactive`, `-i` | | Interactive numbered checklist |
| `agyhub update` | | `[repos...]`, `--check` | Pull latest updates from upstream GitHub |
| `agyhub add-repo` | | `<url> [name] [--branch <b>]` | Register a new Git submodule in hub |
| `agyhub create` | | `skill\|plugin\|rule\|cluster <name> [-g <grp>]` | Scaffold new customization in hub |
