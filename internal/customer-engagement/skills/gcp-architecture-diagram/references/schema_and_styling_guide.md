# Declarative JSON Schema & Visual Styling Guide (`gcp-architecture-diagram`)

This reference defines the declarative JSON specification compiled by [`scripts/render_gcp_diagram.py`](../scripts/render_gcp_diagram.py), the visual styling tokens for the `classic` and `modern` Google Cloud themes, and the complete catalog of bundled official Google Cloud vector icons.

---

## 1. Top-Level JSON Structure

```json
{
  "title": "Optional Diagram Title",
  "subtitle": "Optional Diagram Subtitle",
  "theme": "classic",
  "layout": "vertical",
  "columns": 0,
  "stretch_zones": true,
  "align_zone_heights": true,
  "zones": [ ... ],
  "cards": [ ... ],
  "edges": [ ... ]
}
```

### Top-Level Fields
| Field | Type | Default | Description |
|---|---|---|---|
| `theme` | `"classic"` \| `"modern"` | `"classic"` | `"classic"` renders solid pastel zones with no dashed border (`data-mesh-architecture.svg`). `"modern"` renders pastel zones with colored dashed borders (`agentic-ai-build-multicloud-open-data-lakehouse.svg`). |
| `layout` | `"vertical"` \| `"horizontal"` | `"vertical"` | Default stacking direction for top-level `zones`. |
| `columns` | `int` | `0` | Optional fixed number of columns when laying out top-level `zones` in a grid. |
| `title` | `string` | `""` | Optional header title rendered at the top-left of the SVG canvas. |
| `subtitle` | `string` | `""` | Optional header subtitle rendered below `title`. |
| `stretch_zones` | `bool` | `true` | Stretches zones in narrower rows to align right edges across the canvas. |

---

## 2. Zones & Nested Subzones (`zones` / `subzones`)

Zones can be nested to arbitrary depth using `"subzones"` (or `"zones"`).

```json
{
  "id": "central_services",
  "label": "Central services",
  "color": "blue",
  "row": 0,
  "col": 0,
  "layout": "horizontal",
  "subzones": [
    {
      "id": "discovery_governance",
      "label": "Data product discovery & observability",
      "color": "amber",
      "layout": "horizontal",
      "cards": [ ... ]
    }
  ]
}
```

### Zone Fields & Layout Controls
- **`id`** *(string)*: Unique identifier for the zone (can also be referenced as an endpoint in `edges`).
- **`label`** *(string)*: Zone header text rendered at top-left (`11px` semi-bold).
- **`color`** *(string)*: Semantic zone color key:
  - `"blue"`: Central services / macro plane container (`#e3f2fd` in `classic`, `#e8f0fe` + `#174ea6` dashed border in `modern`).
  - `"amber"` (or `"yellow"`): Domain / functional subgroup container (`#fff8e1` in `classic`, `#fef7e0` + `#b06000` dashed border in `modern`).
  - `"coral"` (or `"red"`): Secondary / streaming / specialized domain container (`#fbe9e7` in `classic`, `#fce8e6` + `#c5221f` dashed border in `modern`).
  - `"green"`: Consumer / serving / clean-room container (`#e8f5e9` in `classic`, `#e6f4ea` + `#0d652d` dashed border in `modern`).
  - `"purple"`: AI / ML / reasoning container (`#f3e5f5` in `classic`, `#f3e8fd` + `#681da8` dashed border in `modern`).
  - `"grey"`: External / on-premises / neutral boundary (`#f5f5f5` in `classic`, `#f8f9fa` + `#5f6368` dashed border in `modern`).
  - `"white"`: White container with subtle grey border (`#ffffff` + `#dadce0`).
- **`transparent`** *(bool, default `false`)*: When `true`, renders an invisible layout row/column wrapper with zero padding—ideal for placing `Data producers` (left `blue` zone) and `Data consumers` (right `blue` zone) side-by-side underneath a full-width `Central services` (`blue`) banner.
- **`layout`** (`"horizontal"` \| `"vertical"`): Arrangement of child `subzones` and `cards`.
- **`columns` / `card_columns`** *(int)*: Wraps child subzones or cards into a multi-row grid with `N` items per row.
- **`row` / `col`** *(int, optional)*: Explicit 0-based grid row and column indices for fine-grained placement.

---

## 3. White GCP Service Cards (`cards`)

Each card renders as a crisp white rounded rectangle (`#ffffff`, `#c4c7c5` border, subtle drop shadow) with a `26x26` Google Cloud vector icon on the left and 2 (or 3) lines of text on the right:

```json
{
  "id": "analytics_hub",
  "title": "Data Marketplace",
  "subtitle": "Analytics Hub",
  "badge": "Zero-Copy Exchange",
  "icon": "analytics_hub"
}
```

### Card Best Practices
1. **Two-Line Architecture Center Convention**:
   - **`title`** (`#212121`, bold `10.2px`): Architectural role or business capability (e.g., `"Data Catalog"`, `"Data Marketplace"`, `"Batch & ELT"`, `"Domain Storage"`).
   - **`subtitle`** (`#757575`, regular `9.0px`): Specific Google Cloud product or component (e.g., `"Knowledge Catalog"`, `"Analytics Hub"`, `"Dataform"`, `"BigQuery"`).
   - **`badge`** *(optional, `#1a73e8`, medium `8.2px`)*: Concise governance tag, project ID, or contract note.
2. **Concise Text**: Keep `title` and `subtitle` under ~32 characters and `badge` under ~40 characters so cards remain compact (`130px–220px` wide).

---

## 4. Orthogonal Connectors & Callout Badges (`edges`)

```json
{
  "from": "d1_interface",
  "to": "analytics_hub",
  "step": 3,
  "label": "Publish listing",
  "style": "solid",
  "from_side": "top",
  "to_side": "bottom"
}
```

### Edge Fields
| Field | Type | Default | Description |
|---|---|---|---|
| `from` | `string` | *(required)* | Source card (or zone) `id`. |
| `to` | `string` | *(required)* | Target card (or zone) `id`. |
| `step` | `int` \| `string` | `null` | Optional sequence number (`1`, `2`, `3`...). Renders a solid `#3a7df0` badge circle (or a combined step-badge + label pill when `label` is also set). |
| `label` | `string` | `null` | Optional text callout pill placed along the connector with automatic collision avoidance. |
| `style` | `"solid"` \| `"dashed"` \| `"dotted"` | `"solid"` | Use `"solid"` for primary data/execution flows and `"dashed"` for metadata registration, policy enforcement, or zero-copy pointer mounts. |
| `bidirectional` | `bool` | `false` | When `true`, draws arrowheads on both ends of the orthogonal connector. |
| `from_side` / `to_side` | `"auto"` \| `"top"` \| `"bottom"` \| `"left"` \| `"right"` | `"auto"` | Optional explicit port side override. When `"auto"`, sides and multi-port slots are chosen automatically to minimize crossings. |
| `offset` | `float` | `auto` | Optional pixel nudge for the middle segment of a 4-point orthogonal dogleg. Parallel edges sharing a corridor are automatically staggered when `offset` is omitted. |
| `color` | `string` | `"#3a7df0"` | Connector and arrowhead hex color. |

---

## 5. Bundled Official Google Cloud Vector Icons (`resources/icons/`)

Run `python3 scripts/render_gcp_diagram.py --list-icons` at any time to inspect the full icon library.

### 49 Normalized `512x512` SVG Icons
- **Core Products (19)**: `alloydb`, `anthos`, `apigee`, `big_query`, `bigtable`, `cloud_armor`, `cloud_build`, `cloud_CDN`, `cloud_code`, `cloud_deploy`, `cloud_domains`, `cloud_functions`, `cloud_IAM`, `cloud_interconnect`, `cloud_logging`, `cloud_monitoring`, `cloud_run`, `cloud_spanner`, `cloud_storage`, `cloud_tasks`, `cloud_ workstation`, `compute_engine`, `config_manager`, `contact_center_ai`, `data_catalog`, `databases`, `dataflow`, `distributed_cloud`, `document_ai`, `firestore`, `gke`, `looker`, `mandiant`, `migrate`, `pub_sub`, ` recommendations_ai`, `security_command_center`, `serverless_spark`, `speech_to_text`, `translation_api`, `vertex_ai`, `vision_ai`, `workflows`.
- **Category Icons (26)**: `agents`, `ai_hypercomputer`, `ai_ml`, `analytics_hub`, `api_management`, `business_intelligence`, `collaboration`, `compute`, `connected_sheets`, `containers`, `COST_management`, `data_analytics`, `developer_tools`, `devops`, `hybrid_multicloud`, `identity_security`, `integration_services`, `management_tools`, `maps_geospatial`, `media_services`, `migration`, `mixed_reality`, `networking`, `observability`, `operations`, ` quantum`, `security_identity`, `serverless`, `storage`, `web3`, `workspace`.
- **Architectural Primitives (4)**: `users`, `external_system`, `document_sheet`, `knowledge_graph`.

### Common Service Aliases (`icon_manifest.json`)
- **Data & Analytics**: `bigquery` / `bq` / `gold` / `medallion` / `linked_dataset` $\rightarrow$ `big_query`; `dataplex` / `dataform` / `composer` / `airflow` / `dbt` / `elt` / `etl` / `bronze` / `silver` $\rightarrow$ `data_analytics`; `knowledge_catalog` / `catalog` / `metadata` / `lineage` $\rightarrow$ `databases`; `analytics_hub` / `bigquery_sharing` / `data_exchange` / `clean_room` $\rightarrow$ `analytics_hub`; `pubsub` / `kafka` / `streaming` $\rightarrow$ `pub_sub`; `dataproc` / `spark` / `iceberg` / `biglake` $\rightarrow$ `serverless_spark`; `gcs` / `bucket` / `lake` / `dlq` $\rightarrow$ `cloud_storage`.
- **AI, BI & Consumption**: `gemini` / `gemini_enterprise` / `adk` / `data_agent` / `conversational_analytics` / `mcp` / `a2a` $\rightarrow$ `agents`; `vertex` / `ml` / `notebook` / `colab` / `embeddings` / `vector_search` $\rightarrow$ `vertex_ai`; `looker` / `lookml` $\rightarrow$ `looker`; `looker_studio` / `bi` / `dashboard` $\rightarrow$ `business_intelligence`; `sheets` / `connected_sheets` $\rightarrow$ `connected_sheets`; `graph` / `property_graph` / `gql` / `ontology` $\rightarrow$ `knowledge_graph`.
- **Security, Governance & Platform**: `iam` / `rbac` / `abac` / `oauth` / `workforce_identity` $\rightarrow$ `cloud_IAM`; `kms` / `cmek` / `dlp` / `sdp` / `vpc_sc` / `tags` $\rightarrow$ `security_identity`; `service_catalog` / `terraform` / `iac` $\rightarrow$ `config_manager`; `monitoring` / `slo` / `alerting` $\rightarrow$ `cloud_monitoring`; `logging` / `audit_logs` $\rightarrow$ `cloud_logging`; `sap` / `erp` / `on_prem` / `s3` / `azure` $\rightarrow$ `external_system`.
