# RecallCase — Vehicle Safety Investigator

**Project type:** Solo portfolio project · Agentic retrieval-augmented generation (RAG) · Public-data investigation  
**Status:** Implementation blueprint · **Last revised:** October 29, 2026  
**Objective in one sentence:** Reconstruct evidence-backed timelines connecting vehicle safety complaints, formal investigations, and recalls—without confusing allegations, similarities, or dates with verified facts.

![RecallCase build stages](diagrams/build-stages.svg)

## 1. The user experience

1. **Select a vehicle:** make, model, and model year; optionally enter a symptom and an *as-of* date.
2. **Investigate:** ask a question such as “What power-loss complaints were recorded before this vehicle's recall?”
3. **Explore findings:** view a short answer, chronological events, categorized evidence, and source identifiers/links.
4. **Inspect uncertainty:** distinguish complaint allegations, formal investigations, recall findings, possible matches, and unavailable evidence.

**Main output:** a **case file** with (a) answer, (b) event timeline, (c) evidence cards and source links, and (d) uncertainties. See [UI example](ui/interactive-demo.html) and [preview](ui/ui-preview.png). The UI example uses explicitly **fictional** records.

## 2. Why this is not ordinary document chat

**Core research question:** Does temporally constrained, evidence-aware *agentic* retrieval produce better sourced investigation answers than dense-only RAG?

Three distinctive design features:
- **Evidence-level distinctions:** consumer complaint = allegation; investigation = official agency action; recall = formal notice. Do not present them as equivalent.
- **Historical cutoff:** filter on appropriate event/received/opened/announced dates, preserve ingestion timestamps, and disclose when true historical publication visibility cannot be proven.
- **Conservative cross-record matching:** combine exact vehicle/component metadata with semantic similarity; label inferred links as **possible**, never **officially linked**, without authoritative evidence.

## 3. Public data and access

| Source | Useful fields | How to access | MVP use |
|---|---|---|---|
| [NHTSA complaints](https://www.nhtsa.gov/nhtsa-datasets-and-apis) | ODI ID, vehicle, component, dates, narrative | `complaintsByVehicle` API; downloadable files | Main semantic corpus |
| [NHTSA recalls](https://www.nhtsa.gov/nhtsa-datasets-and-apis) | campaign number, vehicle, component, defect/summary, dates | `recallsByVehicle` API; bulk archives | Official recall evidence |
| [NHTSA investigations](https://www.nhtsa.gov/nhtsa-datasets-and-apis) | investigation ID, subject, opening/closing dates, status | downloadable `FLAT_INV` archive | Official investigation events |
| Manufacturer communications (optional) | bulletin ID, date, component, summary | NHTSA downloadable files | Stretch goal only |

**Practical strategy:** start with per-vehicle APIs for complaints/recalls and download the investigation archive once. Read the accompanying NHTSA data dictionaries; do not assume common join IDs or identical date semantics across datasets. Cache raw responses, keep provenance and an ingestion timestamp, and build a small curated corpus rather than ingesting the full national archive. Respect published rate controls.

**Scope:** begin with **three researched case studies** (some with known formal actions) plus **one negative-control vehicle**. Pick actual makes, models, and years *after* verifying record availability. Target hundreds to a few thousand relevant records—not millions. Use only public fields; avoid storing private owner details or raw VINs.

## 4. System architecture

![RecallCase system architecture](diagrams/system-architecture.svg)

**Retrieval:** metadata filtering first (make/model/year, date); then compare **BM25**, **EmbeddingGemma 2 dense search**, and **hybrid search**. Add a reranker only after baselines are measured. Use DuckDB for exact lookups, counts, and timelines; use Qdrant or a small local vector index for narrative retrieval. Index by whole evidence record with smaller passages only when narratives warrant them.

**Bounded LangGraph workflow** (not an autonomous multi-agent swarm):

`parse_question → choose_tools → retrieve_evidence → optionally refine_once → verify → report`

Tools: `find_vehicle_records`, `search_complaints`, `lookup_official_actions`, `build_timeline`, and `check_evidence`. The agent may ask for at most one retrieval refinement; tool outputs are data, never instructions. IDs, dates, counts, and URLs come from deterministic code, **not fabricated by the LLM**. Unverifiable claims are removed or marked unknown.

### Minimum evidence schema

```text
record_id | source_type | source_url | make | model | model_year
component | narrative_or_summary | event_date | received_date
opened_date | announced_date | ingested_at | match_basis
```

Not every record has every date. Preserve missing values, a normalized source ID, and the original raw fields. A cutoff applies to the relevant recorded date and **does not prove the record was publicly available at that time**.

## 5. Implementation stages and exit criteria

| Stage | Build | Done when... |
|---|---|---|
| **1 — Define cases** | Select 3 positive/interesting case studies + 1 negative control; list question types | A documented sample can be fetched and at least one genuine investigation/recall relationship is inspectable |
| **2 — Ingest and clean** | API fetchers + investigation download, local cache, Polars normalization, DuckDB tables | Every record has source ID, original payload/file, source type, and load timestamp |
| **3 — Establish retrieval** | BM25 baseline, EmbeddingGemma 2 text embeddings, hybrid search | A saved test set can retrieve known evidence using exact vehicle filters |
| **4 — Add agentic analysis** | LangGraph tool routing, timeline creation, candidate link logic | Multi-source questions work with bounded tool calls; ambiguous links stay labeled possible |
| **5 — Verify evidence** | Citation validation, date checks, allegation/official-action labels, abstention | Unsupported claims and future-dated items are detected before display |
| **6 — Evaluate and demo** | Ablation table, Streamlit UI, repeatable demo cases | Evaluation runs from one command; user can open evidence behind each finding |

**Indicative effort:** ~35–60 focused hours for a modest prototype; a further round of improvements may be needed. This is a planning target, not a performance claim.

## 6. Evaluation plan

Create **60–100 hand-labeled questions** spanning exact lookup, symptom similarity, multiple-source reasoning, as-of queries, false matches, and no-evidence situations. Use a smaller development set; reserve vehicle cases/questions for final testing to reduce tuning leakage. Include source-record IDs as ground truth.

| System | Main purpose |
|---|---|
| BM25 + answer | Lexical baseline |
| Dense retrieval + answer | Standard semantic RAG baseline |
| Hybrid + answer | Test lexical/semantic complementarity |
| Hybrid + bounded agent + verifier | Full RecallCase system |

**Metrics:** Recall@5 and nDCG@10 for retrieval; claim-level citation validity, source-claim support, date-cutoff violations, false-link rate, abstention quality, median latency, and cost per query for end-to-end answers. Keep fixed test cases and the same candidate corpus across comparisons. Report *observed results*, not predetermined uplift.

**Release gates:** no fabricated source IDs or URLs in the held-out demo set; no post-cutoff events in as-of answers; complaint allegations never labeled confirmed defects; meaningful advantage or clear failure analysis against the simplest baseline.

## 7. Deliverables and proposed repository

```text
recallcase/
├── README.md
├── objective.md
├── plan.md
├── data/
│   ├── fetch_complaints.py       # To implement
│   ├── fetch_recalls.py          # To implement
│   └── fetch_investigations.py   # To implement
├── src/
│   ├── normalize.py             # To implement
│   ├── retrieval.py             # To implement
│   ├── tools.py                 # To implement
│   ├── workflow.py              # To implement
│   └── verify.py                # To implement
├── metrics/
│   ├── evaluate_retrieval.py    # To implement
│   └── evaluate_cases.py        # To implement
├── app/
│   └── streamlit_app.py         # To implement
├── tests/                       # To implement
├── diagrams/
│   ├── build-stages.svg
│   └── system-architecture.svg
└── ui/
    ├── interactive-demo.html   # Design-only, simulated records
    └── ui-preview.png
```

**Deliver this MVP:** working local demo, reproducible ingestion + indexing, cited reports, a structured evaluation set and comparison table, diagrams, short limitations section, and reproducibility instructions.

**Not in MVP:** fault diagnosis, future-defect prediction, automatic causality assessment, VIN-specific repair status, nationwide indexing, autonomous browsing, large-scale training, or production deployment. A vehicle *model-year* record is **not** proof that a particular VIN is affected; refer users to the official [NHTSA VIN lookup](https://www.nhtsa.gov/recalls).

## 8. First three implementation tasks

1. Inspect the [NHTSA data catalog](https://www.nhtsa.gov/nhtsa-datasets-and-apis), choose sample vehicles, test API payloads and the investigation file, record genuine available IDs and date fields.
2. Write a reproducible ingestion/normalization script; export a small DuckDB dataset and a source-preserving complaint corpus.
3. Build 15–20 gold retrieval queries, then run BM25 and EmbeddingGemma 2 independently **before** adding an LLM agent.

**Data attribution:** [NHTSA Datasets & APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis) · [Official recall lookup](https://www.nhtsa.gov/recalls) · [NHTSA vPIC vehicle information](https://vpic.nhtsa.dot.gov/api/) (optional entity normalization).
