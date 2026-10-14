# Upgrading Mermaid Flowcharts to Google Cloud Reference Architecture SVGs

This guide details how to convert existing ` ```mermaid ` flowcharts in Markdown deliverables into publication-grade Google Cloud Reference Architecture `.svg` diagrams and synchronize them into Google Docs.

---

## 1. When to Upgrade Mermaid vs. Keep Mermaid

| Diagram Type | Recommended Format | Rationale |
|---|---|---|
| **System / Solution / Data Mesh Architecture (`flowchart` / `graph`)** | **Upgrade to GCP Reference Architecture `.svg`** | Provides official Google Cloud product icons, nested pastel zone containers (`#e3f2fd`, `#fff8e1`), 2-line white service cards, and numbered sequence badges matching `cloud.google.com/architecture`. |
| **Protocol / OAuth / API Call Sequences (`sequenceDiagram`)** | **Keep as Mermaid `sequenceDiagram`** | Time-ordered lifelines and activation bars are native to `sequenceDiagram` and should remain in Mermaid. |
| **Decision Trees (`flowchart TD` with diamond branches)** | **Either Mermaid or GCP `.svg`** | Keep pure yes/no decision trees in Mermaid; upgrade to GCP `.svg` when nodes represent concrete Google Cloud services and zones. |

---

## 2. Step-by-Step Upgrade Workflow

### Step 1: Discover Mermaid Blocks in a Markdown Document
Use `--markdown` with `--list-mermaid` to list every fenced ` ```mermaid ` block along with its line range and section heading:

```bash
python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
  --markdown ./project/topics/platform-framework/docs/rethink-data-mesh-architecture-with-knowledge-catalog-data-product.md \
  --list-mermaid
```

Example output:
```text
Found 4 Mermaid block(s) in .../rethink-data-mesh-architecture-with-knowledge-catalog-data-product.md:
  [0] Lines 80-109  | Heading: 2.1 How Storage Read vs. Compute Execution Decoupling Works in Option 2 | flowchart LR
  [1] Lines 167-205 | Heading: 3.2 Macro-to-Micro Data Mesh Hierarchy | flowchart TD
  [2] Lines 240-262 | Heading: 4.2 End-to-End Execution Flow | sequenceDiagram
  [3] Lines 288-304 | Heading: 5.1 Architectural Decision Tree | flowchart TD
```

### Step 2: Extract & Translate to a Declarative JSON Spec (`--dump-json`)
Run [`scripts/render_gcp_diagram.py`](../scripts/render_gcp_diagram.py) with `--block-index <N>`, `--dump-json`, and `--output`, placing all diagrams for `<doc-stem>.md` under `../diagrams/<doc-stem>/` (and specs under `../diagrams/<doc-stem>/specs/`):

```bash
python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
  --markdown ./project/topics/platform-framework/docs/rethink-data-mesh-architecture-with-knowledge-catalog-data-product.md \
  --block-index 0 \
  --dump-json ./project/topics/platform-framework/diagrams/rethink-data-mesh-architecture-with-knowledge-catalog-data-product/specs/storage-vs-compute-decoupling.json \
  --output ./project/topics/platform-framework/diagrams/rethink-data-mesh-architecture-with-knowledge-catalog-data-product/storage-vs-compute-decoupling.svg
```

What the automatic Mermaid translator does:
1. Maps `subgraph` blocks into colored `zones` / `subzones` and respects `direction LR|TB` layout hints.
2. Splits multi-line node labels into `title` (line 1), `subtitle` (line 2), and `badge` (line 3), stripping markdown formatting and leading bullet markers (`- `, `• `).
3. Resolves official `512x512` Google Cloud vector icons from `title` and `subtitle` against the 128 aliases in `icon_manifest.json`.
4. Converts `-->` into solid orthogonal connectors, `-.->` into dashed connectors, `<-->` into bidirectional connectors, and leading numbers in edge labels (e.g., `|1. Ingest|`) into numbered blue sequence badges (`"step": 1, "label": "Ingest"`).

### Step 3: Refine the JSON Spec for Executive Presentation *(Recommended)*
Mermaid diagrams in technical notes often cram 4–5 verbose bullet points into a single node box. After running `--dump-json`, review the JSON spec and apply these refinements if needed:
- **Shorten Card Text**: Make `"title"` the concise architectural role ($\le 28$ chars) and `"subtitle"` the Google Cloud service name ($\le 30$ chars). Move detailed bullet explanations into the Markdown prose or table below the diagram.
- **Assign Semantic Zone Colors**: Use `"blue"` (`#e3f2fd`) for outer macro planes (`Central services`, `Data producers`, `Data consumers`) and `"amber"` (`#fff8e1`) or `"coral"` (`#fbe9e7`) for inner domain subzones.
- **Re-compile & Verify Visually**:
  ```bash
  python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
    --input ./project/topics/platform-framework/diagrams/rethink-data-mesh-architecture-with-knowledge-catalog-data-product/specs/storage-vs-compute-decoupling.json \
    --output ./project/topics/platform-framework/diagrams/rethink-data-mesh-architecture-with-knowledge-catalog-data-product/storage-vs-compute-decoupling.svg
  ```
  `render_gcp_diagram.py` automatically generates both `storage-vs-compute-decoupling.svg` and the 2× HiDPI `storage-vs-compute-decoupling.png` in the same folder. View the `.png` with `view_file` to confirm crisp layout before updating the Markdown deliverable.

### Step 4: Link in the Markdown Deliverable & Sync to Google Drive
1. In the Markdown file, reference the generated `.svg` using a **portable relative path** (`../diagrams/<doc-stem>/<diagram-name>.svg`, never `file:///` or absolute `/usr/...` paths):
   ```markdown
   ![Storage Read vs. Compute Execution Decoupling](../diagrams/rethink-data-mesh-architecture-with-knowledge-catalog-data-product/storage-vs-compute-decoupling.svg)
   ```
2. When synchronizing with Google Drive using `gcp-project-copilot` (`scripts/sync_drive.py`), the companion 2× HiDPI `.png` is staged in `docs/` during Google Docs import, and all standalone `.svg`, `.png`, and `specs/*.json` files under `diagrams/<doc-stem>/` are synchronized to Google Drive.
