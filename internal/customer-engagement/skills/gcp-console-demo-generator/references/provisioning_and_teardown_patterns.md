# Phase 2 Guide: Single-Sandbox GCP Provisioning, `.runtime/` Schema & Teardown

## 1. Mandatory Pre-Flight & Safety Rules

1. **Verify Active `gcloud` Auth & Project Access**:
   Follow `google-cloud-auth-verification` (`gcloud auth list`, `gcloud projects describe <SANDBOX_PROJECT_ID> --format="value(projectNumber,name)"`).
2. **Enforce Attribution Labels**:
   Pass `--label="datacloud:antigravity"` on `bq query` commands per `enforcing-resource-attribution`.
3. **Strict Namespace Isolation (`<demo_prefix>_`)**:
   Every dataset, Data Exchange, Listing, Taxonomy, Dataplex scan, and custom role created in the shared Sandbox project **must** start with a unique short `<demo_prefix>_` (e.g., `lc_demo_`) so `teardown.sh` never touches unrelated Sandbox assets (`accidental-data-loss-prevention`).

---

## 2. Canonical `.runtime/demo_env.json` Schema

Store all real Sandbox identifiers and Argolis persona bindings exclusively inside `<demo-dir>/.runtime/demo_env.json` (never in `docs/`):

```json
{
  "sandbox_project_id": "my-argolis-sandbox-12345",
  "sandbox_project_number": "987654321098",
  "sandbox_project_name": "My Internal Argolis Sandbox",
  "default_project_alias": "gcp-logistics-domain",
  "alias_project_number": "111122223333",
  "alias_project_name": "Logistics Domain (Gold)",
  "region": "europe-west1",
  "bq_location": "EU",
  "demo_prefix": "lc_demo",
  "dataset_aliases": {
    "lc_demo_prod_cargo": "lost_cargo_dataset",
    "lc_demo_cons_cargo_shared": "lost_cargo_shared",
    "lc_demo_cons_cargo_dcr": "lost_cargo_dcr_linked"
  },
  "personas": {
    "producer": {
      "argolis_email": "architect@gcp.altostrat.com",
      "display_alias": "steward@logistics-domain.example.com",
      "banner_label": "Persona: Publisher (gcp-logistics-domain)",
      "banner_color": "amber",
      "cdp_port": 9222
    },
    "consumer": {
      "argolis_email": "analyst-test@gcp.altostrat.com",
      "display_alias": "investigator@supplychain-domain.example.com",
      "banner_label": "Persona: Subscriber (gcp-supplychain-domain)",
      "banner_color": "blue",
      "cdp_port": 9223
    }
  }
}
```

> [!NOTE]
> Save reusable project-wide defaults in **Section 6** of `<workspace>/specs/specs_project.md` (which is gitignored and excluded from Google Drive sync) so subsequent demos in the same customer workspace inherit the Sandbox Project ID and Argolis persona emails automatically.

---

## 3. Least-Privilege Argolis Persona IAM Pattern (Single Project)

For the `consumer` Argolis persona to log into Cloud Console on `SANDBOX_PROJECT_ID` and see **authentic** `Access Denied`, masked `****`, or `Restricted Export` errors without seeing internal producer datasets:

1. **Project-Level Roles for `consumer`** *(minimal Console + query execution)*:
   - `roles/browser` (allows Cloud Console top-bar project navigation and BigQuery Studio tree loading without granting read access to datasets!)
   - `roles/bigquery.jobUser` (allows running SQL queries billed to the project without reading unauthorized datasets)
2. **Dataset / Listing Roles for `consumer`**:
   - Grant `roles/analyticshub.viewer` + `roles/analyticshub.subscriber` **only on the specific Exchange Listing(s)**.
   - Grant `roles/bigquery.dataViewer` **only on the subscribed Linked Dataset** (`<demo>_cons_*`) and optional `<demo>_cons_workspace` dataset (for testing `CREATE TABLE AS SELECT` egress blocks!).
   - Do **not** grant `roles/bigquery.dataViewer`, `roles/viewer`, or `roles/datacatalog.categoryFineGrainedReader` at the project level to `consumer` unless a specific Act explicitly tests cleared access on a secondary policy tag.

### 3.1 Shared Sandbox `roles/owner` Pre-Flight Matrix

In shared team Sandboxes, secondary test accounts (`consumer`) often **already hold project-level `roles/owner` or `roles/editor`**. Always run a pre-flight IAM check before designing your security Act:

```bash
gcloud projects get-iam-policy "${SANDBOX_PROJECT_ID}" \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:${CONSUMER_EMAIL}" \
  --format="table(bindings.role)"
```

Use this enforcement matrix so you never design an Act that silently bypasses permissions on an Owner account (and never strip a teammate's pre-existing `roles/owner` without explicit user consent):

| GCP Security / Governance Control | Enforced Even When Persona Has Project `roles/owner`? | Architectural Notes for Shared Sandboxes |
| :--- | :---: | :--- |
| **BigQuery Row-Level Security (`ROW ACCESS POLICY`)** | **Yes** | Evaluates `SESSION_USER()` / group predicates strictly per policy; `roles/owner` does **not** bypass RLS unless explicitly listed in a `TRUE` policy `GRANTEE_LIST`. |
| **BigQuery Column-Level Security (`Policy Tags` / Dynamic Masking)** | **Yes** | Data Catalog `Fine-Grained Reader` and `Masked Reader` permissions are independent of `roles/owner`; an Owner without `datacatalog.categoryFineGrainedReader` receives an authentic `Access Denied` on protected columns! |
| **IAM v2 Deny Policies** | **Yes** | Deny policies evaluate before Allow policies and override `roles/owner`. |
| **Dataset / Exchange RBAC (`roles/bigquery.dataViewer` omission)** | **No** | Project `roles/owner`, `roles/editor`, and `roles/bigquery.dataViewer` grant read access across all datasets in the project. Requires a non-Owner secondary persona account (holding only `roles/browser` + `roles/bigquery.jobUser`). |

### 3.2 Verified BigQuery `ROW ACCESS POLICY` & Data Catalog `Policy Tag` Patterns

1. **Uncorrelated Subquery Requirement in BigQuery `ROW ACCESS POLICY`**:
   BigQuery's RLS engine **rejects correlated `EXISTS (SELECT 1 FROM ... WHERE e.col = target.col)` subqueries** referencing the protected table. Always write multi-column entitlement lookups using an **uncorrelated `IN` subquery** (or `UNNEST` array membership) paired with a Data Steward `TRUE` policy:

   ```sql
   -- 1. Data Steward / Domain Owner full-table visibility policy
   CREATE OR REPLACE ROW ACCESS POLICY rls_steward_all
   ON `my-sandbox.demo_gold.fct_purchase_orders`
   GRANT TO ("user:steward@altostrat.com")
   FILTER USING (TRUE);

   -- 2. Dynamic entitlement lookup (single-column or tuple-encoded uncorrelated IN)
   CREATE OR REPLACE ROW ACCESS POLICY rls_buyer_entitlements
   ON `my-sandbox.demo_gold.fct_purchase_orders`
   GRANT TO ("user:buyer@altostrat.com")
   FILTER USING (
     CONCAT(bg_code, '|', commodity_code) IN (
       SELECT CONCAT(e.bg_code, '|', e.commodity_code)
       FROM `my-sandbox.demo_gov.purchasing_entitlements` AS e
       WHERE LOWER(e.principal_email) = LOWER(SESSION_USER())
         AND e.is_active = TRUE
     )
   );
   ```

2. **Air-Gapping Governance Entitlement Tables with a Data Catalog `Policy Tag`**:
   When `consumer` holds `roles/owner` on a shared Sandbox project, dataset RBAC alone will not block `SELECT * FROM demo_gov.purchasing_entitlements`. Attach a Data Catalog Policy Tag (e.g., `C4_Governance_Secret`) to a sensitive column on the entitlements table **without** granting `roles/datacatalog.categoryFineGrainedReader` to `consumer`:
   - BigQuery's RLS engine still evaluates `rls_buyer_entitlements` seamlessly (provided the RLS subquery only projects non-tagged columns `principal_email`, `bg_code`, `commodity_code`, `is_active`), while
   - Any direct `SELECT * FROM demo_gov.purchasing_entitlements` by `consumer` immediately triggers an authentic **CLS `Access Denied` banner** in BigQuery Studio!

---

## 4. Tracking Provisioned Resources in `.runtime/state.json` & `.runtime/teardown.sh`

Record every created resource in `.runtime/state.json`:

```json
{
  "demo_slug": "bigquery-data-sharing-lost-cargo",
  "sandbox_project_id": "my-argolis-sandbox-12345",
  "bq_location": "EU",
  "region": "europe-west1",
  "linked_datasets": ["lc_demo_cons_cargo_shared", "lc_demo_cons_cargo_dcr"],
  "source_datasets": ["lc_demo_prod_cargo", "lc_demo_cons_workspace"],
  "exchanges": [
    "projects/my-argolis-sandbox-12345/locations/eu/dataExchanges/lc_demo_exchange",
    "projects/my-argolis-sandbox-12345/locations/eu/dataExchanges/lc_demo_dcr"
  ],
  "taxonomies": [
    "projects/my-argolis-sandbox-12345/locations/eu/taxonomies/1234567890"
  ],
  "project_iam_bindings_added": [
    {"role": "roles/browser", "member": "user:analyst-test@gcp.altostrat.com"},
    {"role": "roles/bigquery.jobUser", "member": "user:analyst-test@gcp.altostrat.com"}
  ]
}
```

### Mandatory `teardown.sh` Reverse-Order Rules

Always author `.runtime/teardown.sh` (`chmod +x`, `set -euo pipefail`) so the user can tear down the live demo cleanly after their workshop:
1. Support `--dry-run` flag to preview deletions without mutating GCP.
2. **Step 1**: Delete subscribed **Linked Datasets** first (`bq rm -r -f "${PROJECT_ID}:${LINKED_DS}"`).
3. **Step 2**: Delete **Listings** and **Data Exchanges** via `DELETE https://analyticshub.googleapis.com/v1/...` (`?force=true` if supported).
4. **Step 3**: Delete **Dataplex Scans / Data Products** created with `<demo_prefix>_`.
5. **Step 4**: Delete **Source & Scratch BigQuery Datasets** matching `<demo_prefix>_*` (`bq rm -r -f "${PROJECT_ID}:${SOURCE_DS}"`).
6. **Step 5**: Delete **Data Catalog Policy Tag Taxonomies** created for the demo.
7. **Step 6**: Remove only the exact project-level IAM bindings recorded in `project_iam_bindings_added` (if dedicated to this demo).

