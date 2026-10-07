# Antigravity Skills Hub — Current Skills, Groups & Clusters Catalog

This document provides a comprehensive, centralized catalog of all skills, groups, curated clusters, and plugins available in the **Antigravity Skills & Plugins Hub**.

> [!TIP]
> For setup, installation requirements, and the complete CLI reference guide for managing and activating these customizations, please refer to [README.md](README.md).

## Table of Contents

- [Catalog Overview](#catalog-overview)
- [Curated Clusters](#curated-clusters)
  - [1. gcp-data-enterprise-architect](#1-gcp-data-enterprise-architect)
  - [2. data-engineer](#2-data-engineer)
  - [3. science-researcher](#3-science-researcher)
  - [4. agent-developer](#4-agent-developer)
- [Available Groups & Sources](#available-groups--sources)
  - [Subcategories in external/googlecloud-base](#subcategories-in-externalgooglecloud-base)
- [Bundled Plugins](#bundled-plugins)
- [Complete Skills Inventory](#complete-skills-inventory)
  - [external/agents-cli (Google ADK Agents CLI)](#externalagents-cli-google-adk-agents-cli)
  - [external/googlecloud-data (Data Agent Kit)](#externalgooglecloud-data-data-agent-kit)
  - [external/deepmind-science (DeepMind Science)](#externaldeepmind-science-deepmind-science)
  - [external/googlecloud-base/cloud (Google Cloud Platform & ML)](#externalgooglecloud-basecloud-google-cloud-platform--ml)
  - [external/googlecloud-base/ads (Google Ads API)](#externalgooglecloud-baseads-google-ads-api)
  - [external/googlecloud-base/analytics (Google Analytics)](#externalgooglecloud-baseanalytics-google-analytics)
  - [external/googlecloud-base/developers (Developer Knowledge)](#externalgooglecloud-basedevelopers-developer-knowledge)
  - [external/googlecloud-base/identity (Identity & Auth)](#externalgooglecloud-baseidentity-identity--auth)
  - [internal/hub-tools (Hub Meta-Tooling)](#internalhub-tools-hub-meta-tooling)
  - [internal/templates (Starter Templates)](#internaltemplates-starter-templates)

---

## Catalog Overview

| Metric | Count | Details |
| :--- | :--- | :--- |
| **Total Skills** | **232** | Across all internal typologies and upstream submodules |
| **Curated Clusters** | **4** | Role-tailored skill bundles combining internal & external tools |
| **Bundled Plugins** | **5** | Ready-to-use Antigravity plugins |
| **Upstream Submodules** | **4** | Google Cloud Platform, DeepMind Science, Google ADK |
| **Internal Typologies** | **2+** | Hub meta-tooling and starter templates (extensible) |

---

## Curated Clusters

Skill clusters allow you to activate a curated subset of skills tailored for specific engineering personas or workflows across **multiple repositories** with a single command (`agyhub enable -c <cluster>`).

| Predefined Cluster | Description | Skills Count | Key Technologies / Focus |
| :--- | :--- | :--- | :--- |
| [`gcp-data-enterprise-architect`](#1-gcp-data-enterprise-architect) | Google Cloud Data Enterprise Architect: multi-product lakehouse design, data mesh, governance, lineage, FinOps, security, and migration | 21 skills + 1 plugin | Lakehouse, Data Mesh, Dataplex Governance, Lineage, FinOps, Security |
| [`data-engineer`](#2-data-engineer) | GCP Data Engineering and ETL toolset (BigQuery, dbt, Spark, Dataform) | 5 skills | BigQuery, dbt, Spark, Dataform, BigQuery Optimization |
| [`science-researcher`](#3-science-researcher) | DeepMind bioinformatics, protein structure, and biomedical research tools | 5 skills | AlphaFold, PubMed, ChEMBL, UniProt, Clinical Trials |
| [`agent-developer`](#4-agent-developer) | Google Agent Development Kit (ADK) agent authoring, testing, eval, and deployment | 5 skills | ADK code, eval, deploy, workflow, template-skill |

### 1. gcp-data-enterprise-architect

**Description**: Google Cloud Data Enterprise Architect: multi-product lakehouse design, data mesh, governance, lineage, FinOps, security, and migration

```bash
# Activate this cluster in current workspace:
agyhub enable -c gcp-data-enterprise-architect

# Or activate globally across all workspaces:
agyhub enable -G -c gcp-data-enterprise-architect
```

> [!NOTE]
> For detailed architectural rationale, pillar breakdown, and capability matrices, see the companion guide: [`clusters/gcp-data-enterprise-architect.md`](clusters/gcp-data-enterprise-architect.md).

**Included Customizations:**

| Type | Name | Provenance | Description |
| :--- | :--- | :--- | :--- |
| Skill | [`google-cloud-solution-architecture`](external/googlecloud-base/skills/cloud/google-cloud-solution-architecture/SKILL.md) | `external/googlecloud-base/cloud` | Interactively discovers requirements and designs holistic, multi-product system archi... |
| Skill | [`google-cloud-solution-agentic-ai-borderless-data-lakehouse`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-borderless-data-lakehouse/SKILL.md) | `external/googlecloud-base/cloud` | Discovers requirements and designs a borderless open data lakehouse using Lakehouse f... |
| Skill | [`google-cloud-solution-agentic-analytics-spark-knowledge-catalog`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-analytics-spark-knowledge-catalog/SKILL.md) | `external/googlecloud-base/cloud` | Discovers requirements and designs an end-to-end governed agentic analytics solution ... |
| Skill | [`google-cloud-recipe-foundation-builder`](external/googlecloud-base/skills/cloud/google-cloud-recipe-foundation-builder/SKILL.md) | `external/googlecloud-base/cloud` | Deploys a baseline landing zone foundation for a Google Cloud Organization, establish... |
| Skill | [`google-cloud-waf-cost-optimization`](external/googlecloud-base/skills/cloud/google-cloud-waf-cost-optimization/SKILL.md) | `external/googlecloud-base/cloud` | Evaluates Google Cloud workloads for cost efficiency and FinOps alignment using the G... |
| Skill | [`google-cloud-waf-security`](external/googlecloud-base/skills/cloud/google-cloud-waf-security/SKILL.md) | `external/googlecloud-base/cloud` | Generates security-focused guidance for Google Cloud workloads based on the design pr... |
| Skill | [`google-cloud-waf-reliability`](external/googlecloud-base/skills/cloud/google-cloud-waf-reliability/SKILL.md) | `external/googlecloud-base/cloud` | Generates guidance for reliability, resilience, availability, redundancy, fault-toler... |
| Skill | [`bigquery-optimization`](external/googlecloud-base/skills/cloud/bigquery-optimization/SKILL.md) | `external/googlecloud-base/cloud` | Provides workflows to optimize BigQuery environments (capacity planning, editions), s... |
| Skill | [`bigquery-slot-cost-optimizer`](external/googlecloud-base/skills/cloud/bigquery-slot-cost-optimizer/SKILL.md) | `external/googlecloud-base/cloud` | Analyzes Google Cloud BigQuery slot consumption, query costs, and execution bottlenec... |
| Skill | [`datalineage-summary`](external/googlecloud-base/skills/cloud/datalineage-summary/SKILL.md) | `external/googlecloud-base/cloud` | Summarizes Google Cloud Data Lineage graphs to help users debug data quality issues a... |
| Skill | [`datalineage-bigquery-asset-impact-analysis`](external/googlecloud-base/skills/cloud/datalineage-bigquery-asset-impact-analysis/SKILL.md) | `external/googlecloud-base/cloud` | Analyzes the downstream impact (blast radius) when a BigQuery table or view is broken... |
| Skill | [`federate-lakehouse-catalog`](external/googlecloud-data/skills/federate-lakehouse-catalog/SKILL.md) | `external/googlecloud-data` | Sets up Google Cloud Lakehouse federated catalogs to remote Iceberg REST Catalogs. Cu... |
| Skill | [`discovering-gcp-data-assets`](external/googlecloud-data/skills/discovering-gcp-data-assets/SKILL.md) | `external/googlecloud-data` | Finds and inspects data assets within Google Cloud. Relevant when any of the followin... |
| Skill | [`google-cloud-storage-bucket-architect`](external/googlecloud-data/skills/google-cloud-storage-bucket-architect/SKILL.md) | `external/googlecloud-data` | Creates Cloud Storage (Google Cloud Storage, or GCS) buckets. Analyzes the workload (... |
| Skill | [`iam-helper-for-policy-management`](external/googlecloud-base/skills/cloud/iam-helper-for-policy-management/SKILL.md) | `external/googlecloud-base/cloud` | Streamlines the creation, modification, and management of IAM allow policies (v1) and... |
| Skill | [`iam-helper-for-privileged-access-management`](external/googlecloud-base/skills/cloud/iam-helper-for-privileged-access-management/SKILL.md) | `external/googlecloud-base/cloud` | Manages the end-to-end lifecycle of on-demand, temporary access using Privileged Acce... |
| Skill | [`gcp-data-pipelines`](external/googlecloud-data/skills/gcp-data-pipelines/SKILL.md) | `external/googlecloud-data` | 'Primary entry point for building, managing, and orchestrating data pipelines on Goog... |
| Skill | [`gcp-dataflow`](external/googlecloud-data/skills/gcp-dataflow/SKILL.md) | `external/googlecloud-data` | Guides writing, packaging, executing, and troubleshooting Apache Beam pipelines on Da... |
| Skill | [`dbt-sf-to-bq-translator`](external/googlecloud-base/skills/cloud/dbt-sf-to-bq-translator/SKILL.md) | `external/googlecloud-base/cloud` | Translates Snowflake dbt SQL models to Standardized BigQuery SQL. Handles SQL compila... |
| Skill | [`gcs-security-assessment`](external/googlecloud-data/skills/gcs-security-assessment/SKILL.md) | `external/googlecloud-data` | Assesses the security posture of Google Cloud Storage (GCS) buckets and projects. Gro... |
| Skill | [`accidental-data-loss-prevention`](external/googlecloud-data/skills/accidental-data-loss-prevention/SKILL.md) | `external/googlecloud-data` | **STOP AND VERIFY**: Before running any command or tool that results in irreversible ... |
| Plugin | [`googlecloud-data`](external/googlecloud-data/plugin.json) | `external/googlecloud-data` | This plugin provides a specialized suite of skills for data engineers and database pr... |

### 2. data-engineer

**Description**: GCP Data Engineering and ETL toolset (BigQuery, dbt, Spark, Dataform)

```bash
# Activate this cluster in current workspace:
agyhub enable -c data-engineer

# Or activate globally across all workspaces:
agyhub enable -G -c data-engineer
```

**Included Customizations:**

| Type | Name | Provenance | Description |
| :--- | :--- | :--- | :--- |
| Skill | [`bigquery-sql`](external/googlecloud-data/skills/bigquery-sql/SKILL.md) | `external/googlecloud-data` | Provides BigQuery SQL query optimization techniques, execution best practices, and pe... |
| Skill | [`dbt-bigquery`](external/googlecloud-data/skills/dbt-bigquery/SKILL.md) | `external/googlecloud-data` | Expert guidance for creating, modifying, and optimizing dbt pipelines for BigQuery. U... |
| Skill | [`gcp-spark`](external/googlecloud-data/skills/gcp-spark/SKILL.md) | `external/googlecloud-data` | Develops, optimizes and executes Spark code on Managed Spark on Google Cloud (Datapro... |
| Skill | [`dataform-bigquery`](external/googlecloud-data/skills/dataform-bigquery/SKILL.md) | `external/googlecloud-data` | Expertise in generating clean, correct, and efficient Dataform pipeline code for BigQ... |
| Skill | [`bigquery-optimization`](external/googlecloud-base/skills/cloud/bigquery-optimization/SKILL.md) | `external/googlecloud-base/cloud` | Provides workflows to optimize BigQuery environments (capacity planning, editions), s... |

### 3. science-researcher

**Description**: DeepMind bioinformatics, protein structure, and biomedical research tools

```bash
# Activate this cluster in current workspace:
agyhub enable -c science-researcher

# Or activate globally across all workspaces:
agyhub enable -G -c science-researcher
```

**Included Customizations:**

| Type | Name | Provenance | Description |
| :--- | :--- | :--- | :--- |
| Skill | [`alphafold_database_fetch_and_analyze`](external/deepmind-science/skills/alphafold_database_fetch_and_analyze/SKILL.md) | `external/deepmind-science` | Retrieve and analyze AlphaFold predicted structures for a protein. Use when the user ... |
| Skill | [`pubmed_database`](external/deepmind-science/skills/pubmed_database/SKILL.md) | `external/deepmind-science` | Search PubMed for scientific literature, including published clinical trials. Fetch a... |
| Skill | [`chembl_database`](external/deepmind-science/skills/chembl_database/SKILL.md) | `external/deepmind-science` | Query the ChEMBL database for bioactive molecules, drug targets, bioactivity data, ap... |
| Skill | [`uniprot_database`](external/deepmind-science/skills/uniprot_database/SKILL.md) | `external/deepmind-science` | Access protein metadata, function, taxonomy, and sequences across UniProtKB, UniParc,... |
| Skill | [`clinical_trials_database`](external/deepmind-science/skills/clinical_trials_database/SKILL.md) | `external/deepmind-science` | Query ClinicalTrials.gov via APIv2. Use when you want to search for trials by conditi... |

### 4. agent-developer

**Description**: Google Agent Development Kit (ADK) agent authoring, testing, eval, and deployment

```bash
# Activate this cluster in current workspace:
agyhub enable -c agent-developer

# Or activate globally across all workspaces:
agyhub enable -G -c agent-developer
```

**Included Customizations:**

| Type | Name | Provenance | Description |
| :--- | :--- | :--- | :--- |
| Skill | [`google-agents-cli-adk-code`](external/agents-cli/skills/google-agents-cli-adk-code/SKILL.md) | `external/agents-cli` | This skill should be used when the user wants to "write agent code", "build an agent ... |
| Skill | [`google-agents-cli-eval`](external/agents-cli/skills/google-agents-cli-eval/SKILL.md) | `external/agents-cli` | This skill should be used when the user wants to "run an evaluation", "evaluate my ag... |
| Skill | [`google-agents-cli-deploy`](external/agents-cli/skills/google-agents-cli-deploy/SKILL.md) | `external/agents-cli` | This skill should be used when the user wants to "deploy an agent", "deploy my ADK ag... |
| Skill | [`google-agents-cli-workflow`](external/agents-cli/skills/google-agents-cli-workflow/SKILL.md) | `external/agents-cli` | This skill should be used when the user wants to "develop an agent", "build an agent ... |
| Skill | [`template-skill`](internal/templates/skills/template-skill/SKILL.md) | `internal/templates` | A template skill showing the standard structure and best practices for authoring Anti... |

---

## Available Groups & Sources

The hub organizes tools into **`external/`** (read-only upstream submodules) and **`internal/`** (proprietary custom typologies). You can activate an entire group at once using `agyhub enable -g <group>`.

| Group Identifier | Provenance / Upstream | Skills Count | Description & Use Cases | Quick Enable Command |
| :--- | :--- | :--- | :--- | :--- |
| `external/agents-cli` (or `agents-cli`) | [google/agents-cli](https://github.com/google/agents-cli) | 7 | Google Agent Development Kit (ADK) agent authoring, scaffolding, testing, and deployment | `agyhub enable -g agents-cli` |
| `external/googlecloud-data` (or `googlecloud-data`) | [GoogleCloudPlatform/data-agent-kit-plugin](https://github.com/GoogleCloudPlatform/data-agent-kit-plugin) | 37 | Data Agent Kit: BigQuery, dbt, Spark, Dataform, Airflow, Lakehouse catalogs | `agyhub enable -g googlecloud-data` |
| `external/deepmind-science` (or `deepmind-science`) | [google-deepmind/science-skills](https://github.com/google-deepmind/science-skills) | 40 | DeepMind bioinformatics, protein structures (AlphaFold), PubMed, BLAST, chemistry | `agyhub enable -g deepmind-science` |
| `external/googlecloud-base` (or `googlecloud-base`) | [google/skills](https://github.com/google/skills) | 144 | Comprehensive Google Cloud Platform suite (AlloyDB, BigQuery, Vertex, SecOps, WAF, etc.) | `agyhub enable -g googlecloud-base` |
| `internal/hub-tools` (or `hub-tools`) | Local Typology | 3 | Meta-tooling skills (`agyhub-cluster-role-creation`, `agyhub-skills-gap-creator`, `agyhub-agent`) | `agyhub enable -g hub-tools` |
| `internal/templates` (or `templates`) | Local Typology | 1 | Starter templates for creating new skills, plugins, and rules | `agyhub enable -g templates` |
| `internal` | Local Typologies | 4+ | All proprietary custom skills, plugins, and rules across all internal typologies | `agyhub enable -g internal` |

### Subcategories in `external/googlecloud-base`

The large `googlecloud-base` repository is further divided into modular subcategories:

| Subcategory | Skills Count | Target Domain | Quick Enable Command |
| :--- | :--- | :--- | :--- |
| `cloud` | 125 | GCP Infrastructure, AI/ML, Databases, Security, Networking | `agyhub enable -g cloud` |
| `ads` | 14 | Google Ads API, Campaigns, Reporting | `agyhub enable -g ads` |
| `analytics` | 2 | Google Analytics 4 (GA4) Admin & Data APIs | `agyhub enable -g analytics` |
| `developers` | 2 | Developer knowledge retrieval & skill discovery | `agyhub enable -g developers` |
| `identity` | 1 | DPoP OAuth 2.0 token security | `agyhub enable -g identity` |

---

## Bundled Plugins

Plugins bundle skills, rules, and optional MCP configurations into portable packages:

| Plugin Name | Source / Group | Description | Quick Enable Command |
| :--- | :--- | :--- | :--- |
| [`agents-cli`](external/agents-cli/plugin.json) | `external/agents-cli` | Scaffold, develop, evaluate, and deploy AI agents with Google ADK. Bundles skills for... | `agyhub enable agents-cli` |
| [`deepmind-science`](external/deepmind-science/plugin.json) | `external/deepmind-science` | Curated collection of agent skills for science tasks. | `agyhub enable deepmind-science` |
| [`google-cloud-developer`](external/googlecloud-base/plugins/cloud/google-cloud-developer/plugin.json) | `external/googlecloud-base/cloud` | Google Cloud guidance for coding agents: first-project onboarding, authentication and... | `agyhub enable google-cloud-developer` |
| [`googlecloud-data`](external/googlecloud-data/plugin.json) | `external/googlecloud-data` | This plugin provides a specialized suite of skills for data engineers and database pr... | `agyhub enable googlecloud-data` |
| [`template-plugin`](internal/templates/plugins/template-plugin/plugin.json) | `internal/templates` | A starter template plugin packaging skills, rules, and optional MCP configs into a bu... | `agyhub enable template-plugin` |

---

## Complete Skills Inventory

Below is the complete inventory of all 231 skills available in the hub, categorized by their provenance and group.

### external/agents-cli (Google ADK Agents CLI)

Skills for authoring, evaluating, and deploying agents with the Google Agent Development Kit (ADK).

*Total skills in this category: **7***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`google-agents-cli-adk-code`](external/agents-cli/skills/google-agents-cli-adk-code/SKILL.md) | This skill should be used when the user wants to "write agent code", "build an agent ... | [`external/agents-cli/skills/google-agents-cli-adk-code`](external/agents-cli/skills/google-agents-cli-adk-code) |
| [`google-agents-cli-deploy`](external/agents-cli/skills/google-agents-cli-deploy/SKILL.md) | This skill should be used when the user wants to "deploy an agent", "deploy my ADK ag... | [`external/agents-cli/skills/google-agents-cli-deploy`](external/agents-cli/skills/google-agents-cli-deploy) |
| [`google-agents-cli-eval`](external/agents-cli/skills/google-agents-cli-eval/SKILL.md) | This skill should be used when the user wants to "run an evaluation", "evaluate my ag... | [`external/agents-cli/skills/google-agents-cli-eval`](external/agents-cli/skills/google-agents-cli-eval) |
| [`google-agents-cli-observability`](external/agents-cli/skills/google-agents-cli-observability/SKILL.md) | This skill should be used when the user wants to "set up tracing", "monitor my agent"... | [`external/agents-cli/skills/google-agents-cli-observability`](external/agents-cli/skills/google-agents-cli-observability) |
| [`google-agents-cli-publish`](external/agents-cli/skills/google-agents-cli-publish/SKILL.md) | This skill should be used when the user wants to "publish an agent", "publish my ADK ... | [`external/agents-cli/skills/google-agents-cli-publish`](external/agents-cli/skills/google-agents-cli-publish) |
| [`google-agents-cli-scaffold`](external/agents-cli/skills/google-agents-cli-scaffold/SKILL.md) | This skill should be used when the user wants to "create an agent project", "start a ... | [`external/agents-cli/skills/google-agents-cli-scaffold`](external/agents-cli/skills/google-agents-cli-scaffold) |
| [`google-agents-cli-workflow`](external/agents-cli/skills/google-agents-cli-workflow/SKILL.md) | This skill should be used when the user wants to "develop an agent", "build an agent ... | [`external/agents-cli/skills/google-agents-cli-workflow`](external/agents-cli/skills/google-agents-cli-workflow) |

### external/googlecloud-data (Data Agent Kit)

Skills for modern data engineering, lakehouses, orchestration, and BigQuery analytics.

*Total skills in this category: **37***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`accidental-data-loss-prevention`](external/googlecloud-data/skills/accidental-data-loss-prevention/SKILL.md) | **STOP AND VERIFY**: Before running any command or tool that results in irreversible ... | [`external/googlecloud-data/skills/accidental-data-loss-prevention`](external/googlecloud-data/skills/accidental-data-loss-prevention) |
| [`bigquery-ai-ml`](external/googlecloud-data/skills/bigquery-ai-ml/SKILL.md) | Leverages BigQuery's built-in machine learning and GenAI capabilities for advanced da... | [`external/googlecloud-data/skills/bigquery-ai-ml`](external/googlecloud-data/skills/bigquery-ai-ml) |
| [`bigquery-bigframes`](external/googlecloud-data/skills/bigquery-bigframes/SKILL.md) | Generates Python code using BigQuery DataFrames (BigFrames). Use by default for any P... | [`external/googlecloud-data/skills/bigquery-bigframes`](external/googlecloud-data/skills/bigquery-bigframes) |
| [`bigquery-data-transfer-service`](external/googlecloud-data/skills/bigquery-data-transfer-service/SKILL.md) | Discovers and inspects BigQuery Data Transfer Service (DTS) configurations. Use this ... | [`external/googlecloud-data/skills/bigquery-data-transfer-service`](external/googlecloud-data/skills/bigquery-data-transfer-service) |
| [`bigquery-graph-author`](external/googlecloud-data/skills/bigquery-graph-author/SKILL.md) | Provides an end-to-end journey for authoring a BigQuery property graph from your tabl... | [`external/googlecloud-data/skills/bigquery-graph-author`](external/googlecloud-data/skills/bigquery-graph-author) |
| [`bigquery-graph-query`](external/googlecloud-data/skills/bigquery-graph-query/SKILL.md) | Provides guidelines and best practices for querying BigQuery property graphs and sema... | [`external/googlecloud-data/skills/bigquery-graph-query`](external/googlecloud-data/skills/bigquery-graph-query) |
| [`bigquery-sql`](external/googlecloud-data/skills/bigquery-sql/SKILL.md) | Provides BigQuery SQL query optimization techniques, execution best practices, and pe... | [`external/googlecloud-data/skills/bigquery-sql`](external/googlecloud-data/skills/bigquery-sql) |
| [`bigtable-basics`](external/googlecloud-data/skills/bigtable-basics/SKILL.md) | Assists in provisioning instances/tables, designing performant schemas, and querying ... | [`external/googlecloud-data/skills/bigtable-basics`](external/googlecloud-data/skills/bigtable-basics) |
| [`building-data-apps`](external/googlecloud-data/skills/building-data-apps/SKILL.md) | Build modern data apps, dashboards, and interactive reports using either React + Vite... | [`external/googlecloud-data/skills/building-data-apps`](external/googlecloud-data/skills/building-data-apps) |
| [`dak-setup`](external/googlecloud-data/skills/dak-setup/SKILL.md) | Configures (or reconfigures) the Google Cloud Data Agent Kit (DAK) plugin by checking... | [`external/googlecloud-data/skills/dak-setup`](external/googlecloud-data/skills/dak-setup) |
| [`data-autocleaning`](external/googlecloud-data/skills/data-autocleaning/SKILL.md) | Automated data quality and transformation capabilities for Dataform/dbt/BigQuery pipe... | [`external/googlecloud-data/skills/data-autocleaning`](external/googlecloud-data/skills/data-autocleaning) |
| [`dataform-bigquery`](external/googlecloud-data/skills/dataform-bigquery/SKILL.md) | Expertise in generating clean, correct, and efficient Dataform pipeline code for BigQ... | [`external/googlecloud-data/skills/dataform-bigquery`](external/googlecloud-data/skills/dataform-bigquery) |
| [`dbt-bigquery`](external/googlecloud-data/skills/dbt-bigquery/SKILL.md) | Expert guidance for creating, modifying, and optimizing dbt pipelines for BigQuery. U... | [`external/googlecloud-data/skills/dbt-bigquery`](external/googlecloud-data/skills/dbt-bigquery) |
| [`discovering-gcp-data-assets`](external/googlecloud-data/skills/discovering-gcp-data-assets/SKILL.md) | Finds and inspects data assets within Google Cloud. Relevant when any of the followin... | [`external/googlecloud-data/skills/discovering-gcp-data-assets`](external/googlecloud-data/skills/discovering-gcp-data-assets) |
| [`enforcing-resource-attribution`](external/googlecloud-data/skills/enforcing-resource-attribution/SKILL.md) | Enforces resource attribution for CLI commands. Use this skill whenever you are runni... | [`external/googlecloud-data/skills/enforcing-resource-attribution`](external/googlecloud-data/skills/enforcing-resource-attribution) |
| [`federate-lakehouse-catalog`](external/googlecloud-data/skills/federate-lakehouse-catalog/SKILL.md) | Sets up Google Cloud Lakehouse federated catalogs to remote Iceberg REST Catalogs. Cu... | [`external/googlecloud-data/skills/federate-lakehouse-catalog`](external/googlecloud-data/skills/federate-lakehouse-catalog) |
| [`gcp-composer-troubleshooting`](external/googlecloud-data/skills/gcp-composer-troubleshooting/SKILL.md) | 'Provides expert guidance for troubleshooting Cloud Composer (Apache Airflow) and Orc... | [`external/googlecloud-data/skills/gcp-composer-troubleshooting`](external/googlecloud-data/skills/gcp-composer-troubleshooting) |
| [`gcp-data-pipelines`](external/googlecloud-data/skills/gcp-data-pipelines/SKILL.md) | 'Primary entry point for building, managing, and orchestrating data pipelines on Goog... | [`external/googlecloud-data/skills/gcp-data-pipelines`](external/googlecloud-data/skills/gcp-data-pipelines) |
| [`gcp-dataflow`](external/googlecloud-data/skills/gcp-dataflow/SKILL.md) | Guides writing, packaging, executing, and troubleshooting Apache Beam pipelines on Da... | [`external/googlecloud-data/skills/gcp-dataflow`](external/googlecloud-data/skills/gcp-dataflow) |
| [`gcp-managed-airflow-dag-authoring`](external/googlecloud-data/skills/gcp-managed-airflow-dag-authoring/SKILL.md) | Guides the authoring and validation of Apache Airflow DAGs for Managed Service for Ap... | [`external/googlecloud-data/skills/gcp-managed-airflow-dag-authoring`](external/googlecloud-data/skills/gcp-managed-airflow-dag-authoring) |
| [`gcp-managed-airflow-migrations`](external/googlecloud-data/skills/gcp-managed-airflow-migrations/SKILL.md) | Provides guidance for migrating Apache Airflow DAGs in Managed Service for Apache Air... | [`external/googlecloud-data/skills/gcp-managed-airflow-migrations`](external/googlecloud-data/skills/gcp-managed-airflow-migrations) |
| [`gcp-managed-airflow-recommendations`](external/googlecloud-data/skills/gcp-managed-airflow-recommendations/SKILL.md) | 'Provides recommendations and best practices for creating, configuring, tuning and op... | [`external/googlecloud-data/skills/gcp-managed-airflow-recommendations`](external/googlecloud-data/skills/gcp-managed-airflow-recommendations) |
| [`gcp-managed-spark-upgrades`](external/googlecloud-data/skills/gcp-managed-spark-upgrades/SKILL.md) | Upgrades GCP Spark/Dataproc jobs to newer versions by analyzing, remediating, and tes... | [`external/googlecloud-data/skills/gcp-managed-spark-upgrades`](external/googlecloud-data/skills/gcp-managed-spark-upgrades) |
| [`gcp-pipeline-orchestration`](external/googlecloud-data/skills/gcp-pipeline-orchestration/SKILL.md) | This skill helps the agent generate or update orchestration pipeline definitions for ... | [`external/googlecloud-data/skills/gcp-pipeline-orchestration`](external/googlecloud-data/skills/gcp-pipeline-orchestration) |
| [`gcp-pipeline-resource-provisioning`](external/googlecloud-data/skills/gcp-pipeline-resource-provisioning/SKILL.md) | Automates declarative resource creation and provisioning for data pipelines, supporti... | [`external/googlecloud-data/skills/gcp-pipeline-resource-provisioning`](external/googlecloud-data/skills/gcp-pipeline-resource-provisioning) |
| [`gcp-spark`](external/googlecloud-data/skills/gcp-spark/SKILL.md) | Develops, optimizes and executes Spark code on Managed Spark on Google Cloud (Datapro... | [`external/googlecloud-data/skills/gcp-spark`](external/googlecloud-data/skills/gcp-spark) |
| [`gcp-spark-troubleshooting`](external/googlecloud-data/skills/gcp-spark-troubleshooting/SKILL.md) | "Provides expert guidance for troubleshooting Google Cloud Spark and Dataproc workloa... | [`external/googlecloud-data/skills/gcp-spark-troubleshooting`](external/googlecloud-data/skills/gcp-spark-troubleshooting) |
| [`gcs-security-assessment`](external/googlecloud-data/skills/gcs-security-assessment/SKILL.md) | Assesses the security posture of Google Cloud Storage (GCS) buckets and projects. Gro... | [`external/googlecloud-data/skills/gcs-security-assessment`](external/googlecloud-data/skills/gcs-security-assessment) |
| [`google-cloud-auth-verification`](external/googlecloud-data/skills/google-cloud-auth-verification/SKILL.md) | Mandatory Step 0 pre-flight execution order and authentication verification for Googl... | [`external/googlecloud-data/skills/google-cloud-auth-verification`](external/googlecloud-data/skills/google-cloud-auth-verification) |
| [`google-cloud-storage-basics`](external/googlecloud-data/skills/google-cloud-storage-basics/SKILL.md) | Stores, retrieves, and manages data as objects in Cloud Storage (Google Cloud Storage... | [`external/googlecloud-data/skills/google-cloud-storage-basics`](external/googlecloud-data/skills/google-cloud-storage-basics) |
| [`google-cloud-storage-bucket-architect`](external/googlecloud-data/skills/google-cloud-storage-bucket-architect/SKILL.md) | Creates Cloud Storage (Google Cloud Storage, or GCS) buckets. Analyzes the workload (... | [`external/googlecloud-data/skills/google-cloud-storage-bucket-architect`](external/googlecloud-data/skills/google-cloud-storage-bucket-architect) |
| [`google-cloud-storage-fuse`](external/googlecloud-data/skills/google-cloud-storage-fuse/SKILL.md) | Mounts Cloud Storage buckets as a POSIX file system with Cloud Storage FUSE (gcsfuse)... | [`external/googlecloud-data/skills/google-cloud-storage-fuse`](external/googlecloud-data/skills/google-cloud-storage-fuse) |
| [`managing-python-dependencies`](external/googlecloud-data/skills/managing-python-dependencies/SKILL.md) | Ensures proper Python dependency management, avoiding global `pip install` and adheri... | [`external/googlecloud-data/skills/managing-python-dependencies`](external/googlecloud-data/skills/managing-python-dependencies) |
| [`ml-best-practices`](external/googlecloud-data/skills/ml-best-practices/SKILL.md) | CRITICAL RULE: You MUST use this skill whenever the task involves any machine learnin... | [`external/googlecloud-data/skills/ml-best-practices`](external/googlecloud-data/skills/ml-best-practices) |
| [`notebook-guidance`](external/googlecloud-data/skills/notebook-guidance/SKILL.md) | - This skill guides the use of Jupyter notebooks for data analysis, exploration, and ... | [`external/googlecloud-data/skills/notebook-guidance`](external/googlecloud-data/skills/notebook-guidance) |
| [`resolving-mcp-region-configs`](external/googlecloud-data/skills/resolving-mcp-region-configs/SKILL.md) | Mandatory Step 0 pre-flight check for regional Google Cloud MCP servers (e.g. Datapro... | [`external/googlecloud-data/skills/resolving-mcp-region-configs`](external/googlecloud-data/skills/resolving-mcp-region-configs) |
| [`schema-mapping`](external/googlecloud-data/skills/schema-mapping/SKILL.md) | Guides the process of analyzing, mapping, and documenting transformations between sou... | [`external/googlecloud-data/skills/schema-mapping`](external/googlecloud-data/skills/schema-mapping) |

### external/deepmind-science (DeepMind Science)

Bioinformatics, cheminformatics, structural biology, and biomedical literature research skills.

*Total skills in this category: **40***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`alphafold_database_fetch_and_analyze`](external/deepmind-science/skills/alphafold_database_fetch_and_analyze/SKILL.md) | Retrieve and analyze AlphaFold predicted structures for a protein. Use when the user ... | [`external/deepmind-science/skills/alphafold_database_fetch_and_analyze`](external/deepmind-science/skills/alphafold_database_fetch_and_analyze) |
| [`alphagenome_atlas_website_links`](external/deepmind-science/skills/alphagenome_atlas_website_links/SKILL.md) | Constructs deep-links and URLs for the AlphaGenome Atlas website. Supports generating... | [`external/deepmind-science/skills/alphagenome_atlas_website_links`](external/deepmind-science/skills/alphagenome_atlas_website_links) |
| [`alphagenome_single_variant_analysis`](external/deepmind-science/skills/alphagenome_single_variant_analysis/SKILL.md) | Analyzes genetic variant effects on gene expression (RNA-seq), chromatin accessibilit... | [`external/deepmind-science/skills/alphagenome_single_variant_analysis`](external/deepmind-science/skills/alphagenome_single_variant_analysis) |
| [`alphagenome_variant_impact_score`](external/deepmind-science/skills/alphagenome_variant_impact_score/SKILL.md) | Score, annotate, and analyze the functional impact of genetic variants using AlphaGen... | [`external/deepmind-science/skills/alphagenome_variant_impact_score`](external/deepmind-science/skills/alphagenome_variant_impact_score) |
| [`chembl_database`](external/deepmind-science/skills/chembl_database/SKILL.md) | Query the ChEMBL database for bioactive molecules, drug targets, bioactivity data, ap... | [`external/deepmind-science/skills/chembl_database`](external/deepmind-science/skills/chembl_database) |
| [`clinical_trials_database`](external/deepmind-science/skills/clinical_trials_database/SKILL.md) | Query ClinicalTrials.gov via APIv2. Use when you want to search for trials by conditi... | [`external/deepmind-science/skills/clinical_trials_database`](external/deepmind-science/skills/clinical_trials_database) |
| [`clinvar_database`](external/deepmind-science/skills/clinvar_database/SKILL.md) | Use when needing clinical significance, pathogenicity classifications (e.g., Pathogen... | [`external/deepmind-science/skills/clinvar_database`](external/deepmind-science/skills/clinvar_database) |
| [`credentials`](external/deepmind-science/skills/credentials/SKILL.md) | Instructions for handling API keys and credentials safely, verifying their presence, ... | [`external/deepmind-science/skills/credentials`](external/deepmind-science/skills/credentials) |
| [`dbsnp_database`](external/deepmind-science/skills/dbsnp_database/SKILL.md) | Use when you want to look up, map, and search for short genetic variants (SNPs, indel... | [`external/deepmind-science/skills/dbsnp_database`](external/deepmind-science/skills/dbsnp_database) |
| [`embl_ebi_ols`](external/deepmind-science/skills/embl_ebi_ols/SKILL.md) | Query and search the EMBL-EBI Ontology Lookup Service (OLS) for biomedical ontology t... | [`external/deepmind-science/skills/embl_ebi_ols`](external/deepmind-science/skills/embl_ebi_ols) |
| [`encode_ccres_database`](external/deepmind-science/skills/encode_ccres_database/SKILL.md) | Query the ENCODE Registry of cis-Regulatory Elements (cCREs) via the SCREEN GraphQL A... | [`external/deepmind-science/skills/encode_ccres_database`](external/deepmind-science/skills/encode_ccres_database) |
| [`ensembl_database`](external/deepmind-science/skills/ensembl_database/SKILL.md) | Query the Ensembl database to resolve gene, transcript, and protein IDs, fetch genomi... | [`external/deepmind-science/skills/ensembl_database`](external/deepmind-science/skills/ensembl_database) |
| [`foldseek_structural_search`](external/deepmind-science/skills/foldseek_structural_search/SKILL.md) | Performs 3D structural searches of proteins against various databases (PDB, AlphaFold... | [`external/deepmind-science/skills/foldseek_structural_search`](external/deepmind-science/skills/foldseek_structural_search) |
| [`gnomad_database`](external/deepmind-science/skills/gnomad_database/SKILL.md) | Query the Genome Aggregation Database (gnomAD). Use when determining the rarity or al... | [`external/deepmind-science/skills/gnomad_database`](external/deepmind-science/skills/gnomad_database) |
| [`gtex_database`](external/deepmind-science/skills/gtex_database/SKILL.md) | Use when you want to retrieve quantitative RNA expression data and variant eQTL infor... | [`external/deepmind-science/skills/gtex_database`](external/deepmind-science/skills/gtex_database) |
| [`human_protein_atlas_database`](external/deepmind-science/skills/human_protein_atlas_database/SKILL.md) | Use when you want to retrieve semi-quantitative protein expression and spatial locali... | [`external/deepmind-science/skills/human_protein_atlas_database`](external/deepmind-science/skills/human_protein_atlas_database) |
| [`interpro_database`](external/deepmind-science/skills/interpro_database/SKILL.md) | Identify domains, families, and sites in proteins; find all proteins in a family or s... | [`external/deepmind-science/skills/interpro_database`](external/deepmind-science/skills/interpro_database) |
| [`jaspar_database`](external/deepmind-science/skills/jaspar_database/SKILL.md) | Query the JASPAR database for Transcription Factor (TF) binding profiles. Use when re... | [`external/deepmind-science/skills/jaspar_database`](external/deepmind-science/skills/jaspar_database) |
| [`literature_search_arxiv`](external/deepmind-science/skills/literature_search_arxiv/SKILL.md) | Search for scientific papers, preprints, and publications on arXiv. Extract metadata,... | [`external/deepmind-science/skills/literature_search_arxiv`](external/deepmind-science/skills/literature_search_arxiv) |
| [`literature_search_biorxiv`](external/deepmind-science/skills/literature_search_biorxiv/SKILL.md) | Browse, filter, and download life sciences, biology, and medical preprints from bioRx... | [`external/deepmind-science/skills/literature_search_biorxiv`](external/deepmind-science/skills/literature_search_biorxiv) |
| [`literature_search_europepmc`](external/deepmind-science/skills/literature_search_europepmc/SKILL.md) | Search Europe PMC for scientific literature and download open-access full texts and P... | [`external/deepmind-science/skills/literature_search_europepmc`](external/deepmind-science/skills/literature_search_europepmc) |
| [`literature_search_openalex`](external/deepmind-science/skills/literature_search_openalex/SKILL.md) | Query the OpenAlex scholarly database for research papers, authors, institutions, top... | [`external/deepmind-science/skills/literature_search_openalex`](external/deepmind-science/skills/literature_search_openalex) |
| [`ncbi_sequence_fetch`](external/deepmind-science/skills/ncbi_sequence_fetch/SKILL.md) | Retrieve protein and nucleotide sequences from NCBI databases using E-utilities. Supp... | [`external/deepmind-science/skills/ncbi_sequence_fetch`](external/deepmind-science/skills/ncbi_sequence_fetch) |
| [`openfda_database`](external/deepmind-science/skills/openfda_database/SKILL.md) | Query, search, and download data from the openFDA API for drugs, devices, foods, toba... | [`external/deepmind-science/skills/openfda_database`](external/deepmind-science/skills/openfda_database) |
| [`opentargets_database`](external/deepmind-science/skills/opentargets_database/SKILL.md) | Query Open Targets Platform for target-disease associations, drug target discovery, t... | [`external/deepmind-science/skills/opentargets_database`](external/deepmind-science/skills/opentargets_database) |
| [`pdb_database`](external/deepmind-science/skills/pdb_database/SKILL.md) | Use when you want to search for or download experimentally-determined 3D structures f... | [`external/deepmind-science/skills/pdb_database`](external/deepmind-science/skills/pdb_database) |
| [`predictingthepast`](external/deepmind-science/skills/predictingthepast/SKILL.md) | Ancient text restoration, attribution, dating, contextualization, and embedding via A... | [`external/deepmind-science/skills/predictingthepast`](external/deepmind-science/skills/predictingthepast) |
| [`protein_sequence_msa`](external/deepmind-science/skills/protein_sequence_msa/SKILL.md) | Performs multiple sequence alignment of proteins with EBI Clustal Omega. Use when you... | [`external/deepmind-science/skills/protein_sequence_msa`](external/deepmind-science/skills/protein_sequence_msa) |
| [`protein_sequence_similarity_search`](external/deepmind-science/skills/protein_sequence_similarity_search/SKILL.md) | Searches for homologous protein sequences using MMseqs2 (fast, default) or BLAST (com... | [`external/deepmind-science/skills/protein_sequence_similarity_search`](external/deepmind-science/skills/protein_sequence_similarity_search) |
| [`pubchem_database`](external/deepmind-science/skills/pubchem_database/SKILL.md) | Query PubChem, search by name/CID/SMILES, retrieve properties, similarity/substructur... | [`external/deepmind-science/skills/pubchem_database`](external/deepmind-science/skills/pubchem_database) |
| [`pubmed_database`](external/deepmind-science/skills/pubmed_database/SKILL.md) | Search PubMed for scientific literature, including published clinical trials. Fetch a... | [`external/deepmind-science/skills/pubmed_database`](external/deepmind-science/skills/pubmed_database) |
| [`pymol`](external/deepmind-science/skills/pymol/SKILL.md) | Visualize, analyze, and render protein and molecular structures using PyMOL. Use when... | [`external/deepmind-science/skills/pymol`](external/deepmind-science/skills/pymol) |
| [`quickgo_database`](external/deepmind-science/skills/quickgo_database/SKILL.md) | Query the QuickGO and Evidence & Conclusion Ontology (ECO) REST API. Use this when yo... | [`external/deepmind-science/skills/quickgo_database`](external/deepmind-science/skills/quickgo_database) |
| [`reactome_database`](external/deepmind-science/skills/reactome_database/SKILL.md) | Query the Reactome database (Analysis and Content Services). Use when the user asks a... | [`external/deepmind-science/skills/reactome_database`](external/deepmind-science/skills/reactome_database) |
| [`string_database`](external/deepmind-science/skills/string_database/SKILL.md) | Query the STRING database for protein-protein interactions (PPIs), functional enrichm... | [`external/deepmind-science/skills/string_database`](external/deepmind-science/skills/string_database) |
| [`ucsc_conservation_and_tfbs`](external/deepmind-science/skills/ucsc_conservation_and_tfbs/SKILL.md) | Fetch Evolutionary Conservation scores (phyloP, phastCons) and Transcription Factor B... | [`external/deepmind-science/skills/ucsc_conservation_and_tfbs`](external/deepmind-science/skills/ucsc_conservation_and_tfbs) |
| [`unibind_database`](external/deepmind-science/skills/unibind_database/SKILL.md) | Queries the UniBind database for experimentally validated transcription factor (TF) b... | [`external/deepmind-science/skills/unibind_database`](external/deepmind-science/skills/unibind_database) |
| [`uniprot_database`](external/deepmind-science/skills/uniprot_database/SKILL.md) | Access protein metadata, function, taxonomy, and sequences across UniProtKB, UniParc,... | [`external/deepmind-science/skills/uniprot_database`](external/deepmind-science/skills/uniprot_database) |
| [`uv`](external/deepmind-science/skills/uv/SKILL.md) | Checks whether the uv Python package manager is installed and installs it if missing.... | [`external/deepmind-science/skills/uv`](external/deepmind-science/skills/uv) |
| [`workflow_skill_creator`](external/deepmind-science/skills/workflow_skill_creator/SKILL.md) | Distills a completed user workflow or interaction into a reusable agent skill. Use wh... | [`external/deepmind-science/skills/workflow_skill_creator`](external/deepmind-science/skills/workflow_skill_creator) |

### external/googlecloud-base/cloud (Google Cloud Platform & ML)

Infrastructure, database management, FinOps, security architecture, and Vertex AI skills.

*Total skills in this category: **125***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`agent-platform-alert-configuration`](external/googlecloud-base/skills/cloud/agent-platform-alert-configuration/SKILL.md) | Configures best-practice alerting policies for AI agents using OpenTelemetry (OTel) m... | [`external/googlecloud-base/skills/cloud/agent-platform-alert-configuration`](external/googlecloud-base/skills/cloud/agent-platform-alert-configuration) |
| [`agent-platform-deploy`](external/googlecloud-base/skills/cloud/agent-platform-deploy/SKILL.md) | Deploy open models or custom weights from Model Garden to Agent Platform endpoints, c... | [`external/googlecloud-base/skills/cloud/agent-platform-deploy`](external/googlecloud-base/skills/cloud/agent-platform-deploy) |
| [`agent-platform-endpoint-management`](external/googlecloud-base/skills/cloud/agent-platform-endpoint-management/SKILL.md) | Manages Agent Platform serving endpoints. Use when you need to create, list, describe... | [`external/googlecloud-base/skills/cloud/agent-platform-endpoint-management`](external/googlecloud-base/skills/cloud/agent-platform-endpoint-management) |
| [`agent-platform-eval-flywheel`](external/googlecloud-base/skills/cloud/agent-platform-eval-flywheel/SKILL.md) | Measures and improves the quality of AI models and agents on Google Cloud using the E... | [`external/googlecloud-base/skills/cloud/agent-platform-eval-flywheel`](external/googlecloud-base/skills/cloud/agent-platform-eval-flywheel) |
| [`agent-platform-inference`](external/googlecloud-base/skills/cloud/agent-platform-inference/SKILL.md) | Connects to and performs inference with Google Cloud Agent Platform GenAI models, inc... | [`external/googlecloud-base/skills/cloud/agent-platform-inference`](external/googlecloud-base/skills/cloud/agent-platform-inference) |
| [`agent-platform-migrate-from-ai-studio`](external/googlecloud-base/skills/cloud/agent-platform-migrate-from-ai-studio/SKILL.md) | Guides agents and users through migrating from Gemini API in Google AI Studio to Gemi... | [`external/googlecloud-base/skills/cloud/agent-platform-migrate-from-ai-studio`](external/googlecloud-base/skills/cloud/agent-platform-migrate-from-ai-studio) |
| [`agent-platform-model-registry`](external/googlecloud-base/skills/cloud/agent-platform-model-registry/SKILL.md) | Agent Platform Model Registry Management. Use when you need to upload, list, describe... | [`external/googlecloud-base/skills/cloud/agent-platform-model-registry`](external/googlecloud-base/skills/cloud/agent-platform-model-registry) |
| [`agent-platform-prompt-management`](external/googlecloud-base/skills/cloud/agent-platform-prompt-management/SKILL.md) | Manages and orchestrates prompts in Agent Platform. Use when you need to create, list... | [`external/googlecloud-base/skills/cloud/agent-platform-prompt-management`](external/googlecloud-base/skills/cloud/agent-platform-prompt-management) |
| [`agent-platform-rag-engine-management`](external/googlecloud-base/skills/cloud/agent-platform-rag-engine-management/SKILL.md) | Manage and query Agent Platform RAG Engine Corpora and retrieve grounded contexts usi... | [`external/googlecloud-base/skills/cloud/agent-platform-rag-engine-management`](external/googlecloud-base/skills/cloud/agent-platform-rag-engine-management) |
| [`agent-platform-skill-registry`](external/googlecloud-base/skills/cloud/agent-platform-skill-registry/SKILL.md) | Interact with the Gemini Enterprise Agent Platform Skill Registry to create and searc... | [`external/googlecloud-base/skills/cloud/agent-platform-skill-registry`](external/googlecloud-base/skills/cloud/agent-platform-skill-registry) |
| [`agent-platform-troubleshooting`](external/googlecloud-base/skills/cloud/agent-platform-troubleshooting/SKILL.md) | Troubleshoots Google Cloud Gemini Enterprise Agent Platform issues (Agent Gateway, Re... | [`external/googlecloud-base/skills/cloud/agent-platform-troubleshooting`](external/googlecloud-base/skills/cloud/agent-platform-troubleshooting) |
| [`agent-platform-tuning`](external/googlecloud-base/skills/cloud/agent-platform-tuning/SKILL.md) | Agent Platform Model Tuning. Use when you need to fine-tune open models or Gemini mod... | [`external/googlecloud-base/skills/cloud/agent-platform-tuning`](external/googlecloud-base/skills/cloud/agent-platform-tuning) |
| [`agent-platform-tuning-management`](external/googlecloud-base/skills/cloud/agent-platform-tuning-management/SKILL.md) | Manages GenAI tuning jobs in Agent Platform. Use this to list, get, or cancel ongoing... | [`external/googlecloud-base/skills/cloud/agent-platform-tuning-management`](external/googlecloud-base/skills/cloud/agent-platform-tuning-management) |
| [`alloydb-basics`](external/googlecloud-base/skills/cloud/alloydb-basics/SKILL.md) | Manages clusters, instances, and backups for AlloyDB for PostgreSQL, and integrates w... | [`external/googlecloud-base/skills/cloud/alloydb-basics`](external/googlecloud-base/skills/cloud/alloydb-basics) |
| [`application-design-center-design-deploy`](external/googlecloud-base/skills/cloud/application-design-center-design-deploy/SKILL.md) | Processes GCP infrastructure design and deployment workflows within Application Desig... | [`external/googlecloud-base/skills/cloud/application-design-center-design-deploy`](external/googlecloud-base/skills/cloud/application-design-center-design-deploy) |
| [`bigquery-basics`](external/googlecloud-base/skills/cloud/bigquery-basics/SKILL.md) | Manages datasets, tables, and jobs in BigQuery. Use when you need to interact with Bi... | [`external/googlecloud-base/skills/cloud/bigquery-basics`](external/googlecloud-base/skills/cloud/bigquery-basics) |
| [`bigquery-observability`](external/googlecloud-base/skills/cloud/bigquery-observability/SKILL.md) | Provides data-retrieval best practices, tool selection guidance, and performant SQL q... | [`external/googlecloud-base/skills/cloud/bigquery-observability`](external/googlecloud-base/skills/cloud/bigquery-observability) |
| [`bigquery-optimization`](external/googlecloud-base/skills/cloud/bigquery-optimization/SKILL.md) | Provides workflows to optimize BigQuery environments (capacity planning, editions), s... | [`external/googlecloud-base/skills/cloud/bigquery-optimization`](external/googlecloud-base/skills/cloud/bigquery-optimization) |
| [`bigquery-slot-cost-optimizer`](external/googlecloud-base/skills/cloud/bigquery-slot-cost-optimizer/SKILL.md) | Analyzes Google Cloud BigQuery slot consumption, query costs, and execution bottlenec... | [`external/googlecloud-base/skills/cloud/bigquery-slot-cost-optimizer`](external/googlecloud-base/skills/cloud/bigquery-slot-cost-optimizer) |
| [`bigquery-troubleshooting`](external/googlecloud-base/skills/cloud/bigquery-troubleshooting/SKILL.md) | Provides diagnostic workflows and step-by-step root-cause analysis procedures for act... | [`external/googlecloud-base/skills/cloud/bigquery-troubleshooting`](external/googlecloud-base/skills/cloud/bigquery-troubleshooting) |
| [`cloud-build-basics`](external/googlecloud-base/skills/cloud/cloud-build-basics/SKILL.md) | Teaches the fundamentals of Google Cloud Build (GCB). Covers core concepts, API enabl... | [`external/googlecloud-base/skills/cloud/cloud-build-basics`](external/googlecloud-base/skills/cloud/cloud-build-basics) |
| [`cloud-databases-onboarding`](external/googlecloud-base/skills/cloud/cloud-databases-onboarding/SKILL.md) | Guides users through discovering their database requirements, recommends a Google Clo... | [`external/googlecloud-base/skills/cloud/cloud-databases-onboarding`](external/googlecloud-base/skills/cloud/cloud-databases-onboarding) |
| [`cloud-logging-configuration-basics`](external/googlecloud-base/skills/cloud/cloud-logging-configuration-basics/SKILL.md) | Configure single-project Google Cloud Logging: regional log buckets, log sinks, log v... | [`external/googlecloud-base/skills/cloud/cloud-logging-configuration-basics`](external/googlecloud-base/skills/cloud/cloud-logging-configuration-basics) |
| [`cloud-logging-cross-project-configuration`](external/googlecloud-base/skills/cloud/cloud-logging-cross-project-configuration/SKILL.md) | Configure and troubleshoot Google Cloud cross-project centralized logging and read-ti... | [`external/googlecloud-base/skills/cloud/cloud-logging-cross-project-configuration`](external/googlecloud-base/skills/cloud/cloud-logging-cross-project-configuration) |
| [`cloud-logging-query-generation`](external/googlecloud-base/skills/cloud/cloud-logging-query-generation/SKILL.md) | Generates Logging Query Language (LQL) queries for Google Cloud Logging from natural ... | [`external/googlecloud-base/skills/cloud/cloud-logging-query-generation`](external/googlecloud-base/skills/cloud/cloud-logging-query-generation) |
| [`cloud-monitoring-chart-generation`](external/googlecloud-base/skills/cloud/cloud-monitoring-chart-generation/SKILL.md) | Generates Google Cloud Monitoring Server-Driven UI (SDUI) Widget and XyChart Protocol... | [`external/googlecloud-base/skills/cloud/cloud-monitoring-chart-generation`](external/googlecloud-base/skills/cloud/cloud-monitoring-chart-generation) |
| [`cloud-monitoring-list-time-series-request`](external/googlecloud-base/skills/cloud/cloud-monitoring-list-time-series-request/SKILL.md) | Generates valid Cloud Monitoring ListTimeSeries requests and aggregation specificatio... | [`external/googlecloud-base/skills/cloud/cloud-monitoring-list-time-series-request`](external/googlecloud-base/skills/cloud/cloud-monitoring-list-time-series-request) |
| [`cloud-monitoring-metric-selection`](external/googlecloud-base/skills/cloud/cloud-monitoring-metric-selection/SKILL.md) | Retrieve, query, and identify relevant Google Cloud Monitoring metric descriptors for... | [`external/googlecloud-base/skills/cloud/cloud-monitoring-metric-selection`](external/googlecloud-base/skills/cloud/cloud-monitoring-metric-selection) |
| [`cloud-monitoring-promql-query`](external/googlecloud-base/skills/cloud/cloud-monitoring-promql-query/SKILL.md) | Generates valid PromQL queries from Cloud Monitoring metric descriptors and resource ... | [`external/googlecloud-base/skills/cloud/cloud-monitoring-promql-query`](external/googlecloud-base/skills/cloud/cloud-monitoring-promql-query) |
| [`cloud-run-alert-configuration`](external/googlecloud-base/skills/cloud/cloud-run-alert-configuration/SKILL.md) | Configures best-practice, high-signal alerting policies for Google Cloud Run resource... | [`external/googlecloud-base/skills/cloud/cloud-run-alert-configuration`](external/googlecloud-base/skills/cloud/cloud-run-alert-configuration) |
| [`cloud-run-basics`](external/googlecloud-base/skills/cloud/cloud-run-basics/SKILL.md) | Manages Cloud Run services, jobs, and worker pools. Use when you need to deploy appli... | [`external/googlecloud-base/skills/cloud/cloud-run-basics`](external/googlecloud-base/skills/cloud/cloud-run-basics) |
| [`cloud-sql-basics`](external/googlecloud-base/skills/cloud/cloud-sql-basics/SKILL.md) | This file generates or explains Cloud SQL resources. Use this file when the user asks... | [`external/googlecloud-base/skills/cloud/cloud-sql-basics`](external/googlecloud-base/skills/cloud/cloud-sql-basics) |
| [`datalineage-bigquery-asset-impact-analysis`](external/googlecloud-base/skills/cloud/datalineage-bigquery-asset-impact-analysis/SKILL.md) | Analyzes the downstream impact (blast radius) when a BigQuery table or view is broken... | [`external/googlecloud-base/skills/cloud/datalineage-bigquery-asset-impact-analysis`](external/googlecloud-base/skills/cloud/datalineage-bigquery-asset-impact-analysis) |
| [`datalineage-summary`](external/googlecloud-base/skills/cloud/datalineage-summary/SKILL.md) | Summarizes Google Cloud Data Lineage graphs to help users debug data quality issues a... | [`external/googlecloud-base/skills/cloud/datalineage-summary`](external/googlecloud-base/skills/cloud/datalineage-summary) |
| [`dbt-sf-to-bq-translator`](external/googlecloud-base/skills/cloud/dbt-sf-to-bq-translator/SKILL.md) | Translates Snowflake dbt SQL models to Standardized BigQuery SQL. Handles SQL compila... | [`external/googlecloud-base/skills/cloud/dbt-sf-to-bq-translator`](external/googlecloud-base/skills/cloud/dbt-sf-to-bq-translator) |
| [`detection-engineering-coverage-evaluation`](external/googlecloud-base/skills/cloud/detection-engineering-coverage-evaluation/SKILL.md) | Automates the end-to-end detection engineering workflow in Google SecOps using MCP to... | [`external/googlecloud-base/skills/cloud/detection-engineering-coverage-evaluation`](external/googlecloud-base/skills/cloud/detection-engineering-coverage-evaluation) |
| [`developer-device-platform-basics`](external/googlecloud-base/skills/cloud/developer-device-platform-basics/SKILL.md) | Provides guidance and instructions on managing remote devices on Developer Device Pla... | [`external/googlecloud-base/skills/cloud/developer-device-platform-basics`](external/googlecloud-base/skills/cloud/developer-device-platform-basics) |
| [`developing-genkit-dart`](external/googlecloud-base/skills/cloud/developing-genkit-dart/SKILL.md) | Generates code and provides documentation for the Genkit Dart SDK. Use when the user ... | [`external/googlecloud-base/skills/cloud/developing-genkit-dart`](external/googlecloud-base/skills/cloud/developing-genkit-dart) |
| [`developing-genkit-go`](external/googlecloud-base/skills/cloud/developing-genkit-go/SKILL.md) | Develop AI-powered applications using Genkit in Go. Use when the user asks to build A... | [`external/googlecloud-base/skills/cloud/developing-genkit-go`](external/googlecloud-base/skills/cloud/developing-genkit-go) |
| [`developing-genkit-js`](external/googlecloud-base/skills/cloud/developing-genkit-js/SKILL.md) | Develop AI-powered applications using Genkit in Node.js/TypeScript. Use when the user... | [`external/googlecloud-base/skills/cloud/developing-genkit-js`](external/googlecloud-base/skills/cloud/developing-genkit-js) |
| [`developing-genkit-python`](external/googlecloud-base/skills/cloud/developing-genkit-python/SKILL.md) | Develop AI-powered applications using Genkit in Python. Use when the user asks about ... | [`external/googlecloud-base/skills/cloud/developing-genkit-python`](external/googlecloud-base/skills/cloud/developing-genkit-python) |
| [`firebase-basics`](external/googlecloud-base/skills/cloud/firebase-basics/SKILL.md) | Provides foundational Firebase CLI setup, CLI installation, version checks (`firebase... | [`external/googlecloud-base/skills/cloud/firebase-basics`](external/googlecloud-base/skills/cloud/firebase-basics) |
| [`gcloud`](external/googlecloud-base/skills/cloud/gcloud/SKILL.md) | Provides safety-critical validation, guardrails, and data reduction for gcloud CLI op... | [`external/googlecloud-base/skills/cloud/gcloud`](external/googlecloud-base/skills/cloud/gcloud) |
| [`gemini-agents-api`](external/googlecloud-base/skills/cloud/gemini-agents-api/SKILL.md) | Manages custom Agent resources on Gemini Enterprise Agent Platform. Use when the user... | [`external/googlecloud-base/skills/cloud/gemini-agents-api`](external/googlecloud-base/skills/cloud/gemini-agents-api) |
| [`gemini-api`](external/googlecloud-base/skills/cloud/gemini-api/SKILL.md) | Use when the user asks about using Gemini in an enterprise environment or explicitly ... | [`external/googlecloud-base/skills/cloud/gemini-api`](external/googlecloud-base/skills/cloud/gemini-api) |
| [`gemini-interactions-api`](external/googlecloud-base/skills/cloud/gemini-interactions-api/SKILL.md) | Guides the usage of Gemini Interactions API on Gemini Enterprise Agent Platform. Use ... | [`external/googlecloud-base/skills/cloud/gemini-interactions-api`](external/googlecloud-base/skills/cloud/gemini-interactions-api) |
| [`gemini-live-api`](external/googlecloud-base/skills/cloud/gemini-live-api/SKILL.md) | Generates a Gemini LiveAPI client service class in the user's chosen programming lang... | [`external/googlecloud-base/skills/cloud/gemini-live-api`](external/googlecloud-base/skills/cloud/gemini-live-api) |
| [`gke-ai-troubleshooting-handle-disruption-gpu-tpu`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-handle-disruption-gpu-tpu/SKILL.md) | Diagnoses, predicts, and mitigates node disruptions during Compute Engine host mainte... | [`external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-handle-disruption-gpu-tpu`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-handle-disruption-gpu-tpu) |
| [`gke-ai-troubleshooting-jobset-interruption`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-jobset-interruption/SKILL.md) | Diagnoses GKE JobSet interruptions, restarts, and preemptions for AI/ML training work... | [`external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-jobset-interruption`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-jobset-interruption) |
| [`gke-ai-troubleshooting-tpu-dynamic-slices-monitoring`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-dynamic-slices-monitoring/SKILL.md) | Monitors, troubleshoots, and manages GKE TPU Dynamic Slices custom resources. Use whe... | [`external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-dynamic-slices-monitoring`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-dynamic-slices-monitoring) |
| [`gke-ai-troubleshooting-tpu-metrics-monitoring`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-metrics-monitoring/SKILL.md) | Monitors and troubleshoots GKE TPU workloads, nodes, and node pools using GKE system ... | [`external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-metrics-monitoring`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-metrics-monitoring) |
| [`gke-ai-troubleshooting-tpu-vbar-oom`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-vbar-oom/SKILL.md) | Diagnoses and prevents vbar_control_agent segfaults, out-of-memory (OOM) errors, and ... | [`external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-vbar-oom`](external/googlecloud-base/skills/cloud/gke-ai-troubleshooting-tpu-vbar-oom) |
| [`gke-alert-configuration`](external/googlecloud-base/skills/cloud/gke-alert-configuration/SKILL.md) | Configures alerting policies in Terraform for Google Kubernetes Engine (GKE) clusters... | [`external/googlecloud-base/skills/cloud/gke-alert-configuration`](external/googlecloud-base/skills/cloud/gke-alert-configuration) |
| [`gke-app-onboarding`](external/googlecloud-base/skills/cloud/gke-app-onboarding/SKILL.md) | Manages GKE application onboarding, covering containerization, deployment manifests, ... | [`external/googlecloud-base/skills/cloud/gke-app-onboarding`](external/googlecloud-base/skills/cloud/gke-app-onboarding) |
| [`gke-backup-dr`](external/googlecloud-base/skills/cloud/gke-backup-dr/SKILL.md) | Configures Backup for GKE: the BackupRestore cluster addon, BackupPlan and RestorePla... | [`external/googlecloud-base/skills/cloud/gke-backup-dr`](external/googlecloud-base/skills/cloud/gke-backup-dr) |
| [`gke-basics`](external/googlecloud-base/skills/cloud/gke-basics/SKILL.md) | Manages core GKE cluster provisioning, credentials, Autopilot vs Standard selection, ... | [`external/googlecloud-base/skills/cloud/gke-basics`](external/googlecloud-base/skills/cloud/gke-basics) |
| [`gke-batch-hpc`](external/googlecloud-base/skills/cloud/gke-batch-hpc/SKILL.md) | Runs batch and HPC workloads on GKE, utilizing job queues and parallel processing. Us... | [`external/googlecloud-base/skills/cloud/gke-batch-hpc`](external/googlecloud-base/skills/cloud/gke-batch-hpc) |
| [`gke-cluster-autoscaler`](external/googlecloud-base/skills/cloud/gke-cluster-autoscaler/SKILL.md) | Trigger on mention of GKE cluster autoscaler, node autoscaling, node pool auto-creati... | [`external/googlecloud-base/skills/cloud/gke-cluster-autoscaler`](external/googlecloud-base/skills/cloud/gke-cluster-autoscaler) |
| [`gke-cluster-creation`](external/googlecloud-base/skills/cloud/gke-cluster-creation/SKILL.md) | Plans and executes GKE cluster creation, provisioning, and production readiness audit... | [`external/googlecloud-base/skills/cloud/gke-cluster-creation`](external/googlecloud-base/skills/cloud/gke-cluster-creation) |
| [`gke-compute-classes`](external/googlecloud-base/skills/cloud/gke-compute-classes/SKILL.md) | Configures, optimizes, and troubleshoots GKE ComputeClasses. Use when configuring Spo... | [`external/googlecloud-base/skills/cloud/gke-compute-classes`](external/googlecloud-base/skills/cloud/gke-compute-classes) |
| [`gke-cost-analysis`](external/googlecloud-base/skills/cloud/gke-cost-analysis/SKILL.md) | Answer natural language questions and perform analysis on GKE cluster and workload co... | [`external/googlecloud-base/skills/cloud/gke-cost-analysis`](external/googlecloud-base/skills/cloud/gke-cost-analysis) |
| [`gke-cost-optimization`](external/googlecloud-base/skills/cloud/gke-cost-optimization/SKILL.md) | Optimizes GKE costs, rightsizes workloads, and configures Spot VMs, CUDs, cost alloca... | [`external/googlecloud-base/skills/cloud/gke-cost-optimization`](external/googlecloud-base/skills/cloud/gke-cost-optimization) |
| [`gke-custom-golden-image-discovery`](external/googlecloud-base/skills/cloud/gke-custom-golden-image-discovery/SKILL.md) | Discovers golden base images for creating GKE custom node images based on technical s... | [`external/googlecloud-base/skills/cloud/gke-custom-golden-image-discovery`](external/googlecloud-base/skills/cloud/gke-custom-golden-image-discovery) |
| [`gke-golden-path`](external/googlecloud-base/skills/cloud/gke-golden-path/SKILL.md) | Provides GKE golden path configuration defaults, production readiness checklists, and... | [`external/googlecloud-base/skills/cloud/gke-golden-path`](external/googlecloud-base/skills/cloud/gke-golden-path) |
| [`gke-inference`](external/googlecloud-base/skills/cloud/gke-inference/SKILL.md) | Deploys and optimizes AI/ML inference workloads on GKE, using GPUs, TPUs, and model s... | [`external/googlecloud-base/skills/cloud/gke-inference`](external/googlecloud-base/skills/cloud/gke-inference) |
| [`gke-manifest-generation`](external/googlecloud-base/skills/cloud/gke-manifest-generation/SKILL.md) | Generates and updates secure, production-ready Kubernetes YAML manifests optimized fo... | [`external/googlecloud-base/skills/cloud/gke-manifest-generation`](external/googlecloud-base/skills/cloud/gke-manifest-generation) |
| [`gke-multitenancy`](external/googlecloud-base/skills/cloud/gke-multitenancy/SKILL.md) | Plans and configures multi-tenancy on GKE. Covers namespace isolation, RBAC planning ... | [`external/googlecloud-base/skills/cloud/gke-multitenancy`](external/googlecloud-base/skills/cloud/gke-multitenancy) |
| [`gke-networking`](external/googlecloud-base/skills/cloud/gke-networking/SKILL.md) | Plans, configures, and manages core GKE cluster networking. Covers private clusters, ... | [`external/googlecloud-base/skills/cloud/gke-networking`](external/googlecloud-base/skills/cloud/gke-networking) |
| [`gke-node-notready`](external/googlecloud-base/skills/cloud/gke-node-notready/SKILL.md) | Diagnoses GKE nodes reporting NotReady or Unknown status by inspecting node condition... | [`external/googlecloud-base/skills/cloud/gke-node-notready`](external/googlecloud-base/skills/cloud/gke-node-notready) |
| [`gke-observability`](external/googlecloud-base/skills/cloud/gke-observability/SKILL.md) | Configures GKE observability, including Cloud Logging, Cloud Monitoring, and managed ... | [`external/googlecloud-base/skills/cloud/gke-observability`](external/googlecloud-base/skills/cloud/gke-observability) |
| [`gke-platform-security`](external/googlecloud-base/skills/cloud/gke-platform-security/SKILL.md) | Plans, configures, and hardens platform-level Google Kubernetes Engine (GKE) cluster ... | [`external/googlecloud-base/skills/cloud/gke-platform-security`](external/googlecloud-base/skills/cloud/gke-platform-security) |
| [`gke-productionize`](external/googlecloud-base/skills/cloud/gke-productionize/SKILL.md) | Orchestrates comprehensive production readiness reviews and assessments for GKE clust... | [`external/googlecloud-base/skills/cloud/gke-productionize`](external/googlecloud-base/skills/cloud/gke-productionize) |
| [`gke-reliability`](external/googlecloud-base/skills/cloud/gke-reliability/SKILL.md) | Improves GKE workload reliability, using PDBs, health probes, and topology spread con... | [`external/googlecloud-base/skills/cloud/gke-reliability`](external/googlecloud-base/skills/cloud/gke-reliability) |
| [`gke-service-networking`](external/googlecloud-base/skills/cloud/gke-service-networking/SKILL.md) | Configures GKE edge networking, traffic routing, load balancing, and private service ... | [`external/googlecloud-base/skills/cloud/gke-service-networking`](external/googlecloud-base/skills/cloud/gke-service-networking) |
| [`gke-storage`](external/googlecloud-base/skills/cloud/gke-storage/SKILL.md) | Manages GKE storage, including PVCs, PersistentVolumes, and Filestore. Use when confi... | [`external/googlecloud-base/skills/cloud/gke-storage`](external/googlecloud-base/skills/cloud/gke-storage) |
| [`gke-storage-troubleshooting`](external/googlecloud-base/skills/cloud/gke-storage-troubleshooting/SKILL.md) | Diagnoses GKE persistent-storage failures — volume attach/mount errors (Regional PD o... | [`external/googlecloud-base/skills/cloud/gke-storage-troubleshooting`](external/googlecloud-base/skills/cloud/gke-storage-troubleshooting) |
| [`gke-upgrades`](external/googlecloud-base/skills/cloud/gke-upgrades/SKILL.md) | Plans, executes, and validates Google Kubernetes Engine (GKE) cluster upgrades and ma... | [`external/googlecloud-base/skills/cloud/gke-upgrades`](external/googlecloud-base/skills/cloud/gke-upgrades) |
| [`gke-workload-identity`](external/googlecloud-base/skills/cloud/gke-workload-identity/SKILL.md) | Configures and diagnoses Workload Identity Federation for GKE authentication failures... | [`external/googlecloud-base/skills/cloud/gke-workload-identity`](external/googlecloud-base/skills/cloud/gke-workload-identity) |
| [`gke-workload-scaling`](external/googlecloud-base/skills/cloud/gke-workload-scaling/SKILL.md) | Manages scaling for GKE workloads using HPA and VPA. Use when configuring Horizontal ... | [`external/googlecloud-base/skills/cloud/gke-workload-scaling`](external/googlecloud-base/skills/cloud/gke-workload-scaling) |
| [`gke-workload-scaling-troubleshooting`](external/googlecloud-base/skills/cloud/gke-workload-scaling-troubleshooting/SKILL.md) | Diagnoses GKE HorizontalPodAutoscaler (HPA) failures — metrics showing as <unknown>, ... | [`external/googlecloud-base/skills/cloud/gke-workload-scaling-troubleshooting`](external/googlecloud-base/skills/cloud/gke-workload-scaling-troubleshooting) |
| [`gke-workload-security`](external/googlecloud-base/skills/cloud/gke-workload-security/SKILL.md) | Audits, configures, and hardens workload-level security controls for Google Kubernete... | [`external/googlecloud-base/skills/cloud/gke-workload-security`](external/googlecloud-base/skills/cloud/gke-workload-security) |
| [`gke-workload-troubleshooting`](external/googlecloud-base/skills/cloud/gke-workload-troubleshooting/SKILL.md) | Diagnoses GKE workload failures (CrashLoopBackOff, OOMKilled, ImagePullBackOff, Pendi... | [`external/googlecloud-base/skills/cloud/gke-workload-troubleshooting`](external/googlecloud-base/skills/cloud/gke-workload-troubleshooting) |
| [`google-agents-cli-onboarding`](external/googlecloud-base/skills/cloud/google-agents-cli-onboarding/SKILL.md) | Onboarding entrypoint for agents-cli in Agent Platform. It should be used when the us... | [`external/googlecloud-base/skills/cloud/google-agents-cli-onboarding`](external/googlecloud-base/skills/cloud/google-agents-cli-onboarding) |
| [`google-cloud-filestore-auditing`](external/googlecloud-base/skills/cloud/google-cloud-filestore-auditing/SKILL.md) | Audits Google Cloud Filestore instances across projects for disaster recovery readine... | [`external/googlecloud-base/skills/cloud/google-cloud-filestore-auditing`](external/googlecloud-base/skills/cloud/google-cloud-filestore-auditing) |
| [`google-cloud-filestore-autoscale`](external/googlecloud-base/skills/cloud/google-cloud-filestore-autoscale/SKILL.md) | Inspects Google Cloud Filestore capacity and utilization, evaluates storage scaling r... | [`external/googlecloud-base/skills/cloud/google-cloud-filestore-autoscale`](external/googlecloud-base/skills/cloud/google-cloud-filestore-autoscale) |
| [`google-cloud-filestore-log-troubleshooting`](external/googlecloud-base/skills/cloud/google-cloud-filestore-log-troubleshooting/SKILL.md) | Diagnoses and resolves Google Cloud Filestore client mount failures, permission error... | [`external/googlecloud-base/skills/cloud/google-cloud-filestore-log-troubleshooting`](external/googlecloud-base/skills/cloud/google-cloud-filestore-log-troubleshooting) |
| [`google-cloud-filestore-nfs-browser`](external/googlecloud-base/skills/cloud/google-cloud-filestore-nfs-browser/SKILL.md) | Inspects, searches, and reads files and POSIX metadata on Google Cloud Filestore (NFS... | [`external/googlecloud-base/skills/cloud/google-cloud-filestore-nfs-browser`](external/googlecloud-base/skills/cloud/google-cloud-filestore-nfs-browser) |
| [`google-cloud-global-frontend-configuration`](external/googlecloud-base/skills/cloud/google-cloud-global-frontend-configuration/SKILL.md) | Guides agents through a 6-step discovery process to design and deploy Google Cloud gl... | [`external/googlecloud-base/skills/cloud/google-cloud-global-frontend-configuration`](external/googlecloud-base/skills/cloud/google-cloud-global-frontend-configuration) |
| [`google-cloud-networking-observability`](external/googlecloud-base/skills/cloud/google-cloud-networking-observability/SKILL.md) | Investigates Google Cloud networking issues by analyzing GCP logs, metrics, and diagn... | [`external/googlecloud-base/skills/cloud/google-cloud-networking-observability`](external/googlecloud-base/skills/cloud/google-cloud-networking-observability) |
| [`google-cloud-recipe-auth`](external/googlecloud-base/skills/cloud/google-cloud-recipe-auth/SKILL.md) | Provides expert guidance on authenticating and authorizing to Google Cloud services a... | [`external/googlecloud-base/skills/cloud/google-cloud-recipe-auth`](external/googlecloud-base/skills/cloud/google-cloud-recipe-auth) |
| [`google-cloud-recipe-foundation-builder`](external/googlecloud-base/skills/cloud/google-cloud-recipe-foundation-builder/SKILL.md) | Deploys a baseline landing zone foundation for a Google Cloud Organization, establish... | [`external/googlecloud-base/skills/cloud/google-cloud-recipe-foundation-builder`](external/googlecloud-base/skills/cloud/google-cloud-recipe-foundation-builder) |
| [`google-cloud-recipe-onboarding`](external/googlecloud-base/skills/cloud/google-cloud-recipe-onboarding/SKILL.md) | Guides a developer's first steps on Google Cloud, covering account creation, billing ... | [`external/googlecloud-base/skills/cloud/google-cloud-recipe-onboarding`](external/googlecloud-base/skills/cloud/google-cloud-recipe-onboarding) |
| [`google-cloud-scc-query`](external/googlecloud-base/skills/cloud/google-cloud-scc-query/SKILL.md) | Queries and retrieves active security findings, external exposures, toxic combination... | [`external/googlecloud-base/skills/cloud/google-cloud-scc-query`](external/googlecloud-base/skills/cloud/google-cloud-scc-query) |
| [`google-cloud-slo-alert-configuration`](external/googlecloud-base/skills/cloud/google-cloud-slo-alert-configuration/SKILL.md) | Configures PromQL-based Service Level Objective (SLO) alerting policies for Google Cl... | [`external/googlecloud-base/skills/cloud/google-cloud-slo-alert-configuration`](external/googlecloud-base/skills/cloud/google-cloud-slo-alert-configuration) |
| [`google-cloud-solution-agentic-ai-bidirectional-streaming`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-bidirectional-streaming/SKILL.md) | Guides agents to interactively discover customer requirements for live, bidirectional... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-bidirectional-streaming`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-bidirectional-streaming) |
| [`google-cloud-solution-agentic-ai-borderless-data-lakehouse`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-borderless-data-lakehouse/SKILL.md) | Discovers requirements and designs a borderless open data lakehouse using Lakehouse f... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-borderless-data-lakehouse`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-borderless-data-lakehouse) |
| [`google-cloud-solution-agentic-ai-data-science-workflow`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-data-science-workflow/SKILL.md) | Designs a tailored multi-product agentic data science architecture on Google Cloud th... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-data-science-workflow`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-ai-data-science-workflow) |
| [`google-cloud-solution-agentic-analytics-spark-knowledge-catalog`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-analytics-spark-knowledge-catalog/SKILL.md) | Discovers requirements and designs an end-to-end governed agentic analytics solution ... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-analytics-spark-knowledge-catalog`](external/googlecloud-base/skills/cloud/google-cloud-solution-agentic-analytics-spark-knowledge-catalog) |
| [`google-cloud-solution-architecture`](external/googlecloud-base/skills/cloud/google-cloud-solution-architecture/SKILL.md) | Interactively discovers requirements and designs holistic, multi-product system archi... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-architecture`](external/googlecloud-base/skills/cloud/google-cloud-solution-architecture) |
| [`google-cloud-solution-build-deploy-agents`](external/googlecloud-base/skills/cloud/google-cloud-solution-build-deploy-agents/SKILL.md) | Designs, builds, and deploys AI agents or multi-agent systems on Google Cloud. Provid... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-build-deploy-agents`](external/googlecloud-base/skills/cloud/google-cloud-solution-build-deploy-agents) |
| [`google-cloud-solution-guided-gke-ai-migration`](external/googlecloud-base/skills/cloud/google-cloud-solution-guided-gke-ai-migration/SKILL.md) | Guides the migration of existing AI workloads (Cloud Run, Gemini API, Gemini Enterpri... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-guided-gke-ai-migration`](external/googlecloud-base/skills/cloud/google-cloud-solution-guided-gke-ai-migration) |
| [`google-cloud-solution-hybrid-search-alloydb`](external/googlecloud-base/skills/cloud/google-cloud-solution-hybrid-search-alloydb/SKILL.md) | Discovers requirements and generates architectural, design, and deployment guidance f... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-hybrid-search-alloydb`](external/googlecloud-base/skills/cloud/google-cloud-solution-hybrid-search-alloydb) |
| [`google-cloud-solution-multi-agent-security`](external/googlecloud-base/skills/cloud/google-cloud-solution-multi-agent-security/SKILL.md) | Designs, deploys, and secures Google Cloud Agent Gateway solutions. Use when the user... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-multi-agent-security`](external/googlecloud-base/skills/cloud/google-cloud-solution-multi-agent-security) |
| [`google-cloud-solution-n-tier-serverless-web-app`](external/googlecloud-base/skills/cloud/google-cloud-solution-n-tier-serverless-web-app/SKILL.md) | Assists in designing and implementing secure n-tier serverless web applications and m... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-n-tier-serverless-web-app`](external/googlecloud-base/skills/cloud/google-cloud-solution-n-tier-serverless-web-app) |
| [`google-cloud-solution-rag-enterprise-search-gke-sqldb`](external/googlecloud-base/skills/cloud/google-cloud-solution-rag-enterprise-search-gke-sqldb/SKILL.md) | Discovers requirements, and generates architectural, design, and deployment guidance ... | [`external/googlecloud-base/skills/cloud/google-cloud-solution-rag-enterprise-search-gke-sqldb`](external/googlecloud-base/skills/cloud/google-cloud-solution-rag-enterprise-search-gke-sqldb) |
| [`google-cloud-waf-cost-optimization`](external/googlecloud-base/skills/cloud/google-cloud-waf-cost-optimization/SKILL.md) | Evaluates Google Cloud workloads for cost efficiency and FinOps alignment using the G... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-cost-optimization`](external/googlecloud-base/skills/cloud/google-cloud-waf-cost-optimization) |
| [`google-cloud-waf-operational-excellence`](external/googlecloud-base/skills/cloud/google-cloud-waf-operational-excellence/SKILL.md) | Generates operations-focused guidance for Google Cloud workloads based on the design ... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-operational-excellence`](external/googlecloud-base/skills/cloud/google-cloud-waf-operational-excellence) |
| [`google-cloud-waf-performance-optimization`](external/googlecloud-base/skills/cloud/google-cloud-waf-performance-optimization/SKILL.md) | Generates performance-focused guidance for Google Cloud workloads based on the design... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-performance-optimization`](external/googlecloud-base/skills/cloud/google-cloud-waf-performance-optimization) |
| [`google-cloud-waf-reliability`](external/googlecloud-base/skills/cloud/google-cloud-waf-reliability/SKILL.md) | Generates guidance for reliability, resilience, availability, redundancy, fault-toler... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-reliability`](external/googlecloud-base/skills/cloud/google-cloud-waf-reliability) |
| [`google-cloud-waf-security`](external/googlecloud-base/skills/cloud/google-cloud-waf-security/SKILL.md) | Generates security-focused guidance for Google Cloud workloads based on the design pr... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-security`](external/googlecloud-base/skills/cloud/google-cloud-waf-security) |
| [`google-cloud-waf-sustainability`](external/googlecloud-base/skills/cloud/google-cloud-waf-sustainability/SKILL.md) | Provides recommendations for environmental sustainability, carbon footprint reduction... | [`external/googlecloud-base/skills/cloud/google-cloud-waf-sustainability`](external/googlecloud-base/skills/cloud/google-cloud-waf-sustainability) |
| [`iam-helper-for-policy-management`](external/googlecloud-base/skills/cloud/iam-helper-for-policy-management/SKILL.md) | Streamlines the creation, modification, and management of IAM allow policies (v1) and... | [`external/googlecloud-base/skills/cloud/iam-helper-for-policy-management`](external/googlecloud-base/skills/cloud/iam-helper-for-policy-management) |
| [`iam-helper-for-policy-simulator`](external/googlecloud-base/skills/cloud/iam-helper-for-policy-simulator/SKILL.md) | Safely simulates and applies Google Cloud IAM v1 (Allow) policy changes. Uses the Pol... | [`external/googlecloud-base/skills/cloud/iam-helper-for-policy-simulator`](external/googlecloud-base/skills/cloud/iam-helper-for-policy-simulator) |
| [`iam-helper-for-privileged-access-management`](external/googlecloud-base/skills/cloud/iam-helper-for-privileged-access-management/SKILL.md) | Manages the end-to-end lifecycle of on-demand, temporary access using Privileged Acce... | [`external/googlecloud-base/skills/cloud/iam-helper-for-privileged-access-management`](external/googlecloud-base/skills/cloud/iam-helper-for-privileged-access-management) |
| [`iam-helper-for-troubleshooting`](external/googlecloud-base/skills/cloud/iam-helper-for-troubleshooting/SKILL.md) | Diagnoses, remediates, and manages Google Cloud Identity and Access Management (IAM) ... | [`external/googlecloud-base/skills/cloud/iam-helper-for-troubleshooting`](external/googlecloud-base/skills/cloud/iam-helper-for-troubleshooting) |
| [`managed-airflow-dag-authoring`](external/googlecloud-base/skills/cloud/managed-airflow-dag-authoring/SKILL.md) | Provides guidance for authoring Apache Airflow DAGs in Managed Service for Apache Air... | [`external/googlecloud-base/skills/cloud/managed-airflow-dag-authoring`](external/googlecloud-base/skills/cloud/managed-airflow-dag-authoring) |
| [`managed-airflow-dag-troubleshooting`](external/googlecloud-base/skills/cloud/managed-airflow-dag-troubleshooting/SKILL.md) | Provides guidance for troubleshooting Apache Airflow DAGs (failed DAG runs and task i... | [`external/googlecloud-base/skills/cloud/managed-airflow-dag-troubleshooting`](external/googlecloud-base/skills/cloud/managed-airflow-dag-troubleshooting) |
| [`managed-airflow-migrations`](external/googlecloud-base/skills/cloud/managed-airflow-migrations/SKILL.md) | Provides guidance for migrating Apache Airflow DAGs in Managed Service for Apache Air... | [`external/googlecloud-base/skills/cloud/managed-airflow-migrations`](external/googlecloud-base/skills/cloud/managed-airflow-migrations) |
| [`secops-cases`](external/googlecloud-base/skills/cloud/secops-cases/SKILL.md) | Manage Google Security Operations (SecOps) SOAR cases throughout their lifecycle. Use... | [`external/googlecloud-base/skills/cloud/secops-cases`](external/googlecloud-base/skills/cloud/secops-cases) |
| [`secops-detection-engineering`](external/googlecloud-base/skills/cloud/secops-detection-engineering/SKILL.md) | Author, validate, test, and deploy YARA-L 2.0 detection rules and evaluate end-to-end... | [`external/googlecloud-base/skills/cloud/secops-detection-engineering`](external/googlecloud-base/skills/cloud/secops-detection-engineering) |
| [`secops-hunt`](external/googlecloud-base/skills/cloud/secops-hunt/SKILL.md) | Expert guidance for proactive threat hunting in Google SecOps. Use when proactively h... | [`external/googlecloud-base/skills/cloud/secops-hunt`](external/googlecloud-base/skills/cloud/secops-hunt) |
| [`secops-investigate`](external/googlecloud-base/skills/cloud/secops-investigate/SKILL.md) | Expert guidance for deep security incident and entity investigations in Google SecOps... | [`external/googlecloud-base/skills/cloud/secops-investigate`](external/googlecloud-base/skills/cloud/secops-investigate) |
| [`secops-triage`](external/googlecloud-base/skills/cloud/secops-triage/SKILL.md) | Expert guidance for security alert triage in Google SecOps. Use when investigating an... | [`external/googlecloud-base/skills/cloud/secops-triage`](external/googlecloud-base/skills/cloud/secops-triage) |
| [`spanner-basics`](external/googlecloud-base/skills/cloud/spanner-basics/SKILL.md) | Assists in provisioning instances and databases, designing performant schemas, and qu... | [`external/googlecloud-base/skills/cloud/spanner-basics`](external/googlecloud-base/skills/cloud/spanner-basics) |
| [`workload-manager-basics`](external/googlecloud-base/skills/cloud/workload-manager-basics/SKILL.md) | Use this skill to manage Google Cloud Workload Manager evaluations, rules, scanned re... | [`external/googlecloud-base/skills/cloud/workload-manager-basics`](external/googlecloud-base/skills/cloud/workload-manager-basics) |

### external/googlecloud-base/ads (Google Ads API)

Campaign management, reporting, budget optimization, and bidding strategies via the Google Ads API.

*Total skills in this category: **14***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`data-manager-api-audience-ingestion`](external/googlecloud-base/skills/ads/data-manager-api-audience-ingestion/SKILL.md) | Guides developers through managing (adding, removing, and clearing) audience members ... | [`external/googlecloud-base/skills/ads/data-manager-api-audience-ingestion`](external/googlecloud-base/skills/ads/data-manager-api-audience-ingestion) |
| [`data-manager-api-event-ingestion`](external/googlecloud-base/skills/ads/data-manager-api-event-ingestion/SKILL.md) | Guides developers through implementing event and conversion ingestion to Google produ... | [`external/googlecloud-base/skills/ads/data-manager-api-event-ingestion`](external/googlecloud-base/skills/ads/data-manager-api-event-ingestion) |
| [`data-manager-api-setup`](external/googlecloud-base/skills/ads/data-manager-api-setup/SKILL.md) | Guides developers through client library installation and authentication setup steps ... | [`external/googlecloud-base/skills/ads/data-manager-api-setup`](external/googlecloud-base/skills/ads/data-manager-api-setup) |
| [`google-ads-api-account-diagnostics`](external/googlecloud-base/skills/ads/google-ads-api-account-diagnostics/SKILL.md) | Diagnoses Google Ads account performance issues such as conversion loss (value or vol... | [`external/googlecloud-base/skills/ads/google-ads-api-account-diagnostics`](external/googlecloud-base/skills/ads/google-ads-api-account-diagnostics) |
| [`google-ads-api-mcp-setup`](external/googlecloud-base/skills/ads/google-ads-api-mcp-setup/SKILL.md) | Guides developers through downloading, configuring, and installing the official open-... | [`external/googlecloud-base/skills/ads/google-ads-api-mcp-setup`](external/googlecloud-base/skills/ads/google-ads-api-mcp-setup) |
| [`google-ads-api-quickstart`](external/googlecloud-base/skills/ads/google-ads-api-quickstart/SKILL.md) | Guides developers through Google Ads API quickstart: credential setup, choosing from ... | [`external/googlecloud-base/skills/ads/google-ads-api-quickstart`](external/googlecloud-base/skills/ads/google-ads-api-quickstart) |
| [`google-mobile-ads-android-migrate-to-next-gen`](external/googlecloud-base/skills/ads/google-mobile-ads-android-migrate-to-next-gen/SKILL.md) | Migrates Android applications from the old, legacy Google Mobile Ads (GMA) SDK (com.g... | [`external/googlecloud-base/skills/ads/google-mobile-ads-android-migrate-to-next-gen`](external/googlecloud-base/skills/ads/google-mobile-ads-android-migrate-to-next-gen) |
| [`google-mobile-ads-banner`](external/googlecloud-base/skills/ads/google-mobile-ads-banner/SKILL.md) | Provides instructions to implement, integrate, or configure Google Mobile Ads (GMA) b... | [`external/googlecloud-base/skills/ads/google-mobile-ads-banner`](external/googlecloud-base/skills/ads/google-mobile-ads-banner) |
| [`google-mobile-ads-get-started`](external/googlecloud-base/skills/ads/google-mobile-ads-get-started/SKILL.md) | Provides instructions for integrating the Google Mobile Ads (GMA) SDK. Use this skill... | [`external/googlecloud-base/skills/ads/google-mobile-ads-get-started`](external/googlecloud-base/skills/ads/google-mobile-ads-get-started) |
| [`google-mobile-ads-interstitial`](external/googlecloud-base/skills/ads/google-mobile-ads-interstitial/SKILL.md) | Provides instructions for implementing, integrating, or configuring Google Mobile Ads... | [`external/googlecloud-base/skills/ads/google-mobile-ads-interstitial`](external/googlecloud-base/skills/ads/google-mobile-ads-interstitial) |
| [`google-mobile-ads-rewarded`](external/googlecloud-base/skills/ads/google-mobile-ads-rewarded/SKILL.md) | Provides instructions for implementing, integrating, or configuring Google Mobile Ads... | [`external/googlecloud-base/skills/ads/google-mobile-ads-rewarded`](external/googlecloud-base/skills/ads/google-mobile-ads-rewarded) |
| [`google-mobile-ads-validate`](external/googlecloud-base/skills/ads/google-mobile-ads-validate/SKILL.md) | Validates a project's Google Mobile Ads (GMA) SDK integration for iOS, Android, or Un... | [`external/googlecloud-base/skills/ads/google-mobile-ads-validate`](external/googlecloud-base/skills/ads/google-mobile-ads-validate) |
| [`ima-dai-sdk`](external/googlecloud-base/skills/ads/ima-dai-sdk/SKILL.md) | Integrates the Google Interactive Media Ads (IMA) Dynamic Ad Insertion (DAI) SDK into... | [`external/googlecloud-base/skills/ads/ima-dai-sdk`](external/googlecloud-base/skills/ads/ima-dai-sdk) |
| [`ima-sdk-client-side`](external/googlecloud-base/skills/ads/ima-sdk-client-side/SKILL.md) | Supports Interactive Media Ads (IMA) SDK. Use this skill for client-side ad insertion... | [`external/googlecloud-base/skills/ads/ima-sdk-client-side`](external/googlecloud-base/skills/ads/ima-sdk-client-side) |

### external/googlecloud-base/analytics (Google Analytics)

Google Analytics 4 (GA4) administration and data extraction skills.

*Total skills in this category: **2***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`google-analytics-admin-api-basics`](external/googlecloud-base/skills/analytics/google-analytics-admin-api-basics/SKILL.md) | Manages Google Analytics account and property settings, enables the Analytics Admin A... | [`external/googlecloud-base/skills/analytics/google-analytics-admin-api-basics`](external/googlecloud-base/skills/analytics/google-analytics-admin-api-basics) |
| [`google-analytics-data-api-basics`](external/googlecloud-base/skills/analytics/google-analytics-data-api-basics/SKILL.md) | Manages Google Analytics reporting data, enables the Analytics Data API via the Cloud... | [`external/googlecloud-base/skills/analytics/google-analytics-data-api-basics`](external/googlecloud-base/skills/analytics/google-analytics-data-api-basics) |

### external/googlecloud-base/developers (Developer Knowledge)

Meta-guidance skills for searching Google documentation and discovering Google platform skills.

*Total skills in this category: **2***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`finding-google-skills`](external/googlecloud-base/skills/developers/finding-google-skills/SKILL.md) | Google platform decision and setup guidance, loaded on demand from Google's skill cat... | [`external/googlecloud-base/skills/developers/finding-google-skills`](external/googlecloud-base/skills/developers/finding-google-skills) |
| [`retrieving-developer-knowledge`](external/googlecloud-base/skills/developers/retrieving-developer-knowledge/SKILL.md) | Searches, retrieves, and synthesizes official Google developer documentation across G... | [`external/googlecloud-base/skills/developers/retrieving-developer-knowledge`](external/googlecloud-base/skills/developers/retrieving-developer-knowledge) |

### external/googlecloud-base/identity (Identity & Auth)

Security and identity integration skills for OAuth 2.0.

*Total skills in this category: **1***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`dpop-adoption`](external/googlecloud-base/skills/identity/dpop-adoption/SKILL.md) | Implement and debug OAuth 2.0 DPoP (RFC 9449) refresh token sender-constraining for W... | [`external/googlecloud-base/skills/identity/dpop-adoption`](external/googlecloud-base/skills/identity/dpop-adoption) |

### internal/hub-tools (Hub Meta-Tooling)

Internal meta-skills for designing new role clusters and authoring gap skills.

*Total skills in this category: **3***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`agyhub-agent`](internal/hub-tools/skills/agyhub-agent/SKILL.md) | Expert guidance for AI agents to discover, inspect, enable, disable, configure, and troubleshoot Antigravity skills, clusters, groups, and plugins using the agyhub CLI. | [`internal/hub-tools/skills/agyhub-agent`](internal/hub-tools/skills/agyhub-agent) |
| [`agyhub-cluster-role-creation`](internal/hub-tools/skills/agyhub-cluster-role-creation/SKILL.md) | Guides the agent in designing, scoping, and generating new role-based skill clusters ... | [`internal/hub-tools/skills/agyhub-cluster-role-creation`](internal/hub-tools/skills/agyhub-cluster-role-creation) |
| [`agyhub-skills-gap-creator`](internal/hub-tools/skills/agyhub-skills-gap-creator/SKILL.md) | Guides the agent in creating a new, specialized internal skill based on an identified... | [`internal/hub-tools/skills/agyhub-skills-gap-creator`](internal/hub-tools/skills/agyhub-skills-gap-creator) |

### internal/templates (Starter Templates)

Template blueprints for standardizing new skills, plugins, and architectural rules.

*Total skills in this category: **1***

| Skill Name | Description | Path |
| :--- | :--- | :--- |
| [`template-skill`](internal/templates/skills/template-skill/SKILL.md) | A template skill showing the standard structure and best practices for authoring Anti... | [`internal/templates/skills/template-skill`](internal/templates/skills/template-skill) |
