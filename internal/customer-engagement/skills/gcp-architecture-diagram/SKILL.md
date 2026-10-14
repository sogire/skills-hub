---
name: gcp-architecture-diagram
description: Generates publication-grade Google Cloud Reference Architecture SVG diagrams (.svg) from declarative JSON specifications or existing Mermaid flowcharts. Features official Google Cloud multi-color vector icons (49 bundled SVGs and 128 service aliases), nested pastel zone containers (classic solid fill and modern dashed-border themes), 2-line white GCP service cards, and orthogonal right-angle connectors with numbered sequence callout badges. Activate when creating Google Cloud architecture diagrams, upgrading Mermaid flowcharts into official GCP visual flows, or embedding high-DPI GCP architecture SVGs into Markdown deliverables and Google Docs. Do not use for UML sequence diagrams, entity-relationship (ER) diagrams, or interactive React/Streamlit web charts.
---

# Google Cloud Reference Architecture Diagram Generator (`gcp-architecture-diagram`)

Generates publication-grade **Google Cloud Reference Architecture `.svg` diagrams** matching the official visual language of the [Google Cloud Architecture Center](https://cloud.google.com/architecture) (such as `data-mesh-architecture.svg` and `agentic-ai-build-multicloud-open-data-lakehouse.svg`).

## Core Capabilities

1. **Declarative JSON $\rightarrow$ Official Google Cloud SVG**:
   - Compiles structured JSON topology specifications into pure-vector, zero-external-dependency `.svg` files via [`scripts/render_gcp_diagram.py`](./scripts/render_gcp_diagram.py).
   - Supports arbitrary multi-level nested zones (`blue` central/outer containers `#e3f2fd`, `amber` functional domains `#fff8e1`, `coral` secondary/streaming domains `#fbe9e7`, `green` consumer/serving zones `#e8f5e9`, `purple` AI/ML zones `#f3e5f5`, and `grey` external/on-prem zones `#f5f5f5`).
   - Supports two official Google Cloud visual themes:
     - **`classic`** *(default)*: Flat pastel zone fills (`#e3f2fd`, `#fff8e1`, `#fbe9e7`) with no outer dashed border, matching `data-mesh-architecture.svg`.
     - **`modern`**: Pastel zone fills with colored dashed borders (`#174ea6`, `#b06000`, `#c5221f`, `#0d652d`), matching `agentic-ai-build-multicloud-open-data-lakehouse.svg`.
2. **Bundled Official Google Cloud Vector Icons (`resources/icons/`)**:
   - Ships with **49 normalized `512x512` pure-vector SVGs** extracted from Google Cloud's official `category-icons.zip` and `core-products-icons.zip` archives plus 4 architectural primitives (`users`, `external_system`, `document_sheet`, `knowledge_graph`), mapped across **128 service aliases** in [`resources/icons/icon_manifest.json`](./resources/icons/icon_manifest.json).
   - Every icon uses inline hex `fill` attributes (zero `<style>` CSS class collisions when multiple icons are embedded in the same SVG canvas) and renders identically in browsers, ImageMagick `convert`, and `gdocs` (`oksvg`).
3. **Mermaid Flowchart $\rightarrow$ GCP Reference Architecture Upgrade**:
   - Directly parses existing ` ```mermaid ` (`flowchart` / `graph`) blocks inside Markdown deliverables or `.mmd` files, infers Google Cloud icons and 2-line/3-line card hierarchies, and outputs both a customizable JSON spec (`--dump-json`) and a rendered `.svg` (`--output`).
4. **Universal Renderer & Google Docs Compatibility**:
   - Emits orthogonal connectors, dashed lines, card borders, and callout pills using universal filled vector primitives so diagrams rasterize with 100% fidelity during `gdocs mutate sync --render-diagrams` / `sync_drive.py` and ImageMagick `convert`.

---

## Progressive Disclosure References

- **[`references/schema_and_styling_guide.md`](./references/schema_and_styling_guide.md)**: Full declarative JSON schema (`zones`, `subzones`, `cards`, `edges`), `classic` vs. `modern` color tokens, layout tuning options, and the complete catalog of 49 icons and 128 aliases.
- **[`references/mermaid_to_gcp_svg_workflow.md`](./references/mermaid_to_gcp_svg_workflow.md)**: Step-by-step workflow for upgrading ` ```mermaid ` flowcharts in Markdown deliverables into Google Cloud Reference Architecture SVGs and syncing them to Google Docs.
- **[`resources/examples/data_mesh_reference.json`](./resources/examples/data_mesh_reference.json)**: Canonical multi-zone Data Mesh Reference Architecture JSON specification modeled on `data-mesh-architecture.svg`.

---

## Workflow 1: Generate a GCP Reference Architecture SVG from Declarative JSON

### Step 1: Design the Zone & Card Topology
Structure the architecture using Google Cloud Architecture Center conventions (read [`references/schema_and_styling_guide.md`](./references/schema_and_styling_guide.md) for full schema details):
- **Outer Zones**: Group macro architectural planes (`Central services`, `Data producers`, `Data consumers`) using `"color": "blue"`. To place multiple outer `blue` zones side-by-side on the same row below a full-width top banner, wrap them in a container zone with `"transparent": true` and `"layout": "horizontal"`.
- **Inner Subzones**: Group domain or functional boundaries (`Management`, `Data product discovery & observability`, `Data domain 1`, `Consumer domain A`) using `"color": "amber"` (or `"coral"` / `"green"` / `"purple"` to visually distinguish specialized domains).
- **2-Line White Service Cards**: Keep card text concise so cards remain compact and scannable:
  - `"title"`: Architectural role or capability (bold, $\le 28$ chars, e.g., `"Data Catalog"`, `"Data Marketplace"`, `"Domain Storage"`).
  - `"subtitle"`: Google Cloud product name (muted grey, $\le 30$ chars, e.g., `"Knowledge Catalog"`, `"Analytics Hub"`, `"BigQuery"`).
  - `"badge"` *(optional)*: Short 3rd-line governance or technical tag in Google Blue (`#1a73e8`, $\le 36$ chars).
  - `"icon"`: Explicit icon slug or alias (e.g., `"bigquery"`, `"dataplex"`, `"knowledge_catalog"`, `"analytics_hub"`, `"dataform"`, `"dataflow"`, `"cloud_storage"`, `"pubsub"`, `"looker"`, `"vertex_ai"`, `"agents"`, `"iam"`). If omitted, the compiler automatically infers the icon from `subtitle` and `title`.
- **Orthogonal Edges & Numbered Callouts**:
  - Connect card IDs (`"from"`, `"to"`), optionally specifying `"step": 1` for numbered blue sequence circles, `"label": "..."` for callout pills, and `"style": "dashed"` for metadata/control-plane or zero-copy pointer flows.

### Step 2: Compile JSON to SVG & 2× HiDPI PNG
Run [`scripts/render_gcp_diagram.py`](./scripts/render_gcp_diagram.py) using Python 3 (zero external packages required). By default, it outputs both the vector `.svg` and a companion 2× HiDPI (`144 DPI`) `.png` in the same folder:

```bash
python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
  --input ./diagrams/<doc-stem>/specs/architecture-spec.json \
  --output ./diagrams/<doc-stem>/architecture-flow.svg
```

To switch between the `classic` (`data-mesh-architecture.svg`) and `modern` (dashed-border) styles, pass `--theme classic` or `--theme modern`.

### Step 3: Visually Inspect the Rendered Diagram
Always inspect the generated companion `.png` (`./diagrams/<doc-stem>/architecture-flow.png`) visually with `view_file` to verify that zone alignment, card titles, icons, and edge callout pills are clean and overlap-free.

---

## Workflow 2: Upgrade Existing Mermaid Flowcharts into GCP Reference Architecture SVGs

When a user asks to upgrade a ` ```mermaid ` flowchart inside a Markdown document into an official Google Cloud graphical flow (read [`references/mermaid_to_gcp_svg_workflow.md`](./references/mermaid_to_gcp_svg_workflow.md) for detailed guidance):

1. **List Mermaid Blocks in the Markdown File**:
   ```bash
   python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
     --markdown ./project/topics/my-topic/docs/architecture.md \
     --list-mermaid
   ```
   > **Note**: Only `flowchart` / `graph` blocks should be converted into GCP Reference Architecture SVGs. Keep `sequenceDiagram` blocks in Mermaid for protocol/auth call sequences.

2. **Bootstrap the Declarative JSON Spec, SVG & PNG from the Mermaid Block**:
   - Store all `.svg`, `.png`, and `specs/*.json` files for a document `<doc-stem>.md` inside a dedicated per-document subfolder at `../diagrams/<doc-stem>/` (sibling to `docs/`):
   ```bash
   python3 /path/to/gcp-architecture-diagram/scripts/render_gcp_diagram.py \
     --markdown ./project/topics/my-topic/docs/architecture.md \
     --block-index 0 \
     --dump-json ./project/topics/my-topic/diagrams/architecture/specs/flow-0.json \
     --output ./project/topics/my-topic/diagrams/architecture/flow-0.svg
   ```

3. **Refine the JSON Spec for Executive Polish *(Recommended)***:
   - Open the generated `--dump-json` file and refine verbose Mermaid bullet lists into crisp 2-line `"title"` (capability) + `"subtitle"` (GCP product) pairs, organize nested `"subzones"`, and add `"step": 1, 2, 3...` sequence callouts where appropriate.
   - Re-compile with `--input ... --output ...` and verify the rendered `.png`.

---

## Workflow 3: Embed in Markdown Deliverables & Sync to Google Docs / Google Drive

1. **Standardized Per-Document Diagram Folder & Portable Relative Links**:
   - For any Markdown document at `project/topics/<topic>/docs/<doc-stem>.md`, store its diagrams and JSON specs under `project/topics/<topic>/diagrams/<doc-stem>/` (`*.svg`, `*.png`, and `specs/*.json`) using hyphens (`-`) in filenames.
   - Reference the `.svg` from the Markdown file using a portable relative path (never `file:///` or absolute `/usr/...` paths inside repository `.md` files):
     ```markdown
     ![Enterprise Data Mesh Reference Architecture](../diagrams/<doc-stem>/data-mesh-architecture.svg)
     ```
2. **2× HiDPI Rasterization for Google Docs & Drive Asset Sync (`gcp-project-copilot` / `gdocs`)**:
   - **Why HiDPI PNG staging is required for Google Docs**: The `gdocs` CLI's internal Go SVG rasterizer only supports basic geometric primitives (`<rect>`, `<circle>`, `<polygon>`) and ignores `<path>` and `<g transform="...">`, and `gdocs`'s `uploadLocalImages` blocks `../` paths.
   - **Via `gcp-project-copilot` (`scripts/sync_drive.py`)**: `sync_drive.py` automatically ensures every `.svg` in `diagrams/<doc-stem>/` has an up-to-date 2× HiDPI (`144 DPI`) companion `.png`, stages a temporary copy in `docs/` during Google Docs import (cleaning up the temp file in `finally:`), and synchronizes the entire `diagrams/<doc-stem>/` folder (`*.svg`, `*.png`, and `specs/*.json`) into Google Drive.
