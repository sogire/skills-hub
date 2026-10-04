# Antigravity Skills & Plugins Hub

A centralized, zero-copy repository for developing, maintaining, and version-controlling custom Antigravity skills, plugins, and shared rules.

---

## Why This Hub?

Antigravity natively discovers customizations in your projects or global configuration. When working across many repositories, you often want:
1. **Single Source of Truth**: Author and update your skills and plugins in one repository.
2. **Selective Activation**: Enable only the specific skills and plugins relevant to each workspace.
3. **Zero File Duplication**: Avoid copying files or maintaining duplicate folders across projects.

This hub comes with `ag-hub`, a command-line tool that lets you selectively attach skills and plugins to any workspace with zero file copies.

---

## Directory Structure

```text
skills-hub/
├── .git/                     # Track customizations with Git
├── README.md                 # This documentation
├── skills/                   # Standalone custom skills
│   └── template-skill/       # Standard skill boilerplate
│       └── SKILL.md
├── agents-cli/               # Google Agents CLI suite skills (symlinked from ~/.agents/skills)
│   ├── google-agents-cli-adk-code
│   ├── google-agents-cli-deploy
│   ├── google-agents-cli-eval
│   ├── google-agents-cli-observability
│   ├── google-agents-cli-publish
│   ├── google-agents-cli-scaffold
│   └── google-agents-cli-workflow
├── plugins/                  # Bundled plugins (skills + rules + MCP config)
│   └── template-plugin/
│       ├── plugin.json
│       ├── skills/
│       └── rules/
├── rules/                    # Reusable rules / AGENTS.md presets
└── bin/
    └── ag-hub                # CLI tool (symlinked to ~/.local/bin/ag-hub)
```

---

## Quick Reference: `ag-hub` Commands

You can run `ag-hub` from inside any project directory or terminal:

### 1. View Available Customizations & Status
```bash
ag-hub list
```
Shows all available skills and plugins in the hub, and marks which ones are active in your current workspace.

### 2. View Active Customizations in Current Workspace
```bash
ag-hub status
```

### 3. Enable Skills or Plugins (Zero-Copy Native Manifest)
```bash
# Enable one or multiple skills in the current workspace
ag-hub enable template-skill google-agents-cli-adk-code

# Enable a plugin
ag-hub enable template-plugin
```
This generates or updates `.agents/skills.json` and `.agents/plugins.json` in your workspace using Antigravity's native `include_only` directive. No skill files are copied.

### 4. Enable via Symlinks (Alternative Zero-Copy Mode)
If you prefer skills to appear directly in your workspace directory tree:
```bash
ag-hub enable --symlink template-skill
```
This creates a symbolic link in `.agents/skills/template-skill`.

### 5. Disable Skills or Plugins
```bash
ag-hub disable template-skill
```
Removes the skill from `.agents/skills.json` or removes its symlink.

### 6. Interactive Selection Menu
```bash
ag-hub select
# or: ag-hub -i
```
Launches an interactive checklist where you can toggle skills on and off by number and press `save`.

### 7. Authoring New Skills & Plugins
To scaffold a new skill or plugin inside the hub:
```bash
# Create a new skill in skills/<name>
ag-hub create skill my-new-skill

# Create a new plugin in plugins/<name>
ag-hub create plugin my-new-plugin
```

---

## How It Works Behind the Scenes

### Native Manifest Engine (Default)
When you run `ag-hub enable <skill>`, it configures `.agents/skills.json`:
```json
{
  "entries": [
    {
      "path": "/home/sergiobermudez/local_projects/skills-hub/skills",
      "include_only": [
        "template-skill"
      ]
    }
  ]
}
```
Antigravity automatically discovers `.agents/skills.json`, resolves the path back to the hub, and loads only the specified skills using progressive disclosure.

---

## Git Version Control
You can push this repository to your personal GitHub, GitLab, or internal Git server:
```bash
cd /home/sergiobermudez/local_projects/skills-hub
git add .
git commit -m "Initial commit of Antigravity skills hub"
# git remote add origin <your-git-url>
# git push -u origin master
```
