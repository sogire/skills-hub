# Phase 3 Guide: GCP Console Deep-Links, Selectors, Callouts & `/browser` Fallback

## 1. Deterministic Google Cloud Console Deep-Link Catalog

Always navigate directly to the target Console surface using `?project=${SANDBOX_PROJECT_ID}` rather than clicking through the left hamburger menu. **Never** append `&authuser=<email>` to `console.cloud.google.com` URLs (it breaks Angular workspace routing and causes editor timeouts); account isolation is enforced automatically by each persona's dedicated `--user-data-dir` Chrome profile and verified against `[aria-label*="Account:"]` in the top Google bar:

| GCP Service / Surface | Canonical Cloud Console Deep-Link (`https://console.cloud.google.com/...`) |
| :--- | :--- |
| **BigQuery Studio (SQL Workspace)** | `/bigquery?project=<PROJECT_ID>` |
| **BigQuery Dataset Overview / Metadata** | `/bigquery?project=<PROJECT_ID>&ws=!1m4!1m3!3m2!1s<PROJECT_ID>!2s<DATASET_ID>` |
| **BigQuery Table Schema / Policy Tags** | `/bigquery?project=<PROJECT_ID>&ws=!1m5!1m4!4m3!1s<PROJECT_ID>!2s<DATASET_ID>!3s<TABLE_ID>` |
| **BigQuery Sharing (Exchanges List)** | `/bigquery/analytics-hub/exchanges?project=<PROJECT_ID>` |
| **BigQuery Sharing (Clean Rooms List)** | `/bigquery/analytics-hub/clean-rooms?project=<PROJECT_ID>` |
| **Policy Tag Taxonomies (CLS)** | `/bigquery/policy-tags?project=<PROJECT_ID>` |
| **Dataplex Search / Universal Catalog** | `/dataplex/search?project=<PROJECT_ID>` |
| **Dataplex Data Products** | `/dataplex/data-products?project=<PROJECT_ID>` |
| **Dataplex Data Profiling & Quality** | `/dataplex/govern/quality?project=<PROJECT_ID>` |
| **IAM & Admin (Allow Policies)** | `/iam-admin/iam?project=<PROJECT_ID>` |
| **IAM Deny Policies** | `/iam-admin/deny?project=<PROJECT_ID>` |
| **Cloud Storage Buckets** | `/storage/browser?project=<PROJECT_ID>` |

---

## 2. Reliable UI Action & Wait Patterns (`capture_gcp_console.py`)

Cloud Console is an Angular Material SPA where network requests continue in the background (`wait_until: "networkidle"` can time out on streaming telemetry). Follow these rules in `capture_manifest.json`:

1. **Always use `"wait_until": "domcontentloaded"`** on `goto`, followed immediately by `"wait_for_spinners": true` and deterministic actions/waits.
2. **Prefer Semantic / ARIA / Text Selectors Over Obfuscated Classes (for HTML Chrome Elements)**:
   - Good: `[role="tab"]:has-text("Schema")`, `[role="tab"]:has-text("Lineage")`, `[aria-label*="Subscribe"]`, `text="Access Denied:"`
   - Avoid: `.ng-star-inserted > div.cfc-x72a`
3. **Executing SQL Live in BigQuery Studio (`bq_set_query` + `bq_run_query` ONLY)**:
   - **Never** use `{"type": "click", "selector": "button:has-text('Run')"}` in BigQuery Studio! BigQuery Studio renders **two** `"Run"` items (`<cfc-progress-button>` at `y≈97` vs. the `File Edit Run Tools` menu bar item at `y≈127`) and ignores untrusted JS `.click()` events.
   - Always pair `bq_set_query` (`"clean_tabs": true` by default, which closes restored `Untitled query` tabs so zero stale `Query results` drawers remain) with `bq_run_query` (`"wait_for_completion": true` by default, which dispatches trusted CDP mouse clicks on `<cfc-progress-button>` and waits for the job completion status or error banner):
     ```json
     {"type": "bq_set_query", "clean_tabs": true, "sql": "SELECT shipment_id, seal_integrity_status FROM `my_proj.lc_demo_cons_cargo_shared.manifests` WHERE seal_integrity_status = 0;"},
     {"type": "bq_run_query", "wait_for_completion": true, "timeout_ms": 45000}
     ```
   - Write the **real** `<SANDBOX_PROJECT_ID>.<demo_prefix>_...` table name in `bq_set_query` so BigQuery executes the real query against the Sandbox project. Right before snapping the PNG (after CSS/overlay reflow settles), `capture_gcp_console.py` synchronously rewrites `<SANDBOX_PROJECT_ID>` $\rightarrow$ `gcp-supplychain-domain` and `lc_demo_cons_cargo_shared` $\rightarrow$ `lost_cargo_shared` inside Monaco `.view-lines` and query tabs!
4. **2026 BigQuery Studio HTML5 `<canvas>` Result Grid Rule**:
   - BigQuery Studio paints query result rows and cell values onto an **HTML5 `<canvas>`**, **not** HTML `<td>` elements!
   - **Never** use `wait_for_text` or `selector: "text=..."` on query result cell values (they do not exist in the DOM and will always time out). Rely on `bq_run_query` (`"wait_for_completion": true`) or DOM chrome text (`"Query results"`, `"Access Denied:"`).
   - Highlight `<canvas>` result rows using explicit viewport coordinates (`1600x1000` viewport: typically `"x": 380, "y": 652, "width": 1140, "height": 120` for the first 4 rows, or `"height": 175` for 6 rows) with `"anchor": "bottom-left"` or `"top-right"` so the callout pill never obscures data cells!

---

## 3. Canonical Visual Color Language for Callouts & Persona Banners

Keep screenshot `persona_banner` and `callouts` colors 100% consistent with `gcp-architecture-diagram` and Google Slides storyboards:

| Color Token | Hex | Semantic Meaning in Demo Screenshots |
| :--- | :--- | :--- |
| **`amber`** | `#F9AB00` | **Producer / Data Owner ("Yellow Box")** — source dataset curation, Exchange publishing, audit telemetry |
| **`blue`** | `#1A73E8` | **Consumer / Subscriber ("Blue Box")** — Linked Dataset shortcut, consumer SQL query, neutral step callout |
| **`purple`** | `#9334E6` | **Data Sharing Exchange / Data Clean Room / Catalog Governance** — privacy rules, policy tag taxonomy, lineage |
| **`red`** | `#D93025` | **Blocked / Masked / Denied Security Enforcement** — CLS `Access Denied`, dynamic mask, `CTAS` egress block, Clean Room raw-row block |
| **`green`** | `#1E8E3E` | **Authorized / Verified Outcome** — successful governed query result, `100%` Data Quality pass, `$0` producer compute |

Keep callout density crisp: **2 to 4 numbered callouts (`step: 1, 2, 3`) per screenshot** with concise labels ($\le 36$ chars) so screenshots remain uncluttered and executive-readable inside Google Docs and Slides.

---

## 4. Built-In `--inspect-scene` Diagnostics & `/browser` Fallback

1. **Built-In Live UI Diagnostic Flag (`--inspect-scene`)**:
   Whenever a Console surface changes layout or you need exact `(x, y, width, height)` bounding boxes for `<canvas>` grids, tabs, or error banners, run `capture_gcp_console.py --inspect-scene` instead of writing ad-hoc `scratch/*.py` scripts:
   ```bash
   python3 <skill-dir>/scripts/capture_gcp_console.py \
     --manifest <demo-dir>/.runtime/capture_manifest.json \
     --inspect-scene <scene-id>
   ```
   This prints structured JSON (`actual_email`, `tabs`, `buttons`, `canvases`, `banners_and_status`) and saves an unmasked diagnostic PNG to `/tmp/gcp_console_inspect_<scene-id>.png` (safely outside `project/` so it is never synced to Google Drive). Pass `--no-actions` to inspect initial page state before scene actions run.
2. **Interactive `/browser` Fallback**:
   Use `capture_gcp_console.py` for 95% of Console captures. Fall back to Antigravity's `/browser` mode only when an interactive WebGL/SVG force-directed canvas (such as Dataplex Lineage pan/zoom) requires manual framing.

