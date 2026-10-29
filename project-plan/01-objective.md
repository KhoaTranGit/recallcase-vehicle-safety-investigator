# RecallCase — Vehicle Safety Investigator

> **One-line objective:** Build an evidence-aware RAG application that investigates U.S. vehicle safety complaints and reconstructs how reported problems relate to official investigations and recalls.

## The problem
Official vehicle-safety information is fragmented across complaint narratives, investigation records, and recall notices. A keyword search can find individual documents, but it does not easily show **what was reported, what was investigated, what was officially established, and when**.

## What the application does
A user selects a vehicle (make, model, model year), describes a suspected problem, and optionally sets a historical cutoff date. RecallCase:

1. Finds relevant complaints using hybrid lexical + semantic search.
2. Retrieves related investigations and recalls using exact identifiers and structured filters.
3. Builds a dated evidence timeline, labeling **consumer allegation**, **official investigation**, and **official recall** separately.
4. Produces a concise, cited case report with explicit uncertainties and links to original records.

**Example question:** “For this SUV, what reports about unexpected power loss preceded any related official investigation or recall?”

## What makes it interesting
The central feature is **time-aware evidence reconstruction**, not merely chatting with documents. Every claim must be traceable to a record; the system must not mistake similarity for causation or consumer allegations for confirmed defects.

## Solo MVP boundaries
- **Data:** U.S. National Highway Traffic Safety Administration (NHTSA) complaints, investigations, and recalls.
- **Scope:** Three carefully chosen vehicle/model-year case studies; a fourth unrelated case to test false matches. Select cases *after* inspecting available records.
- **Stack:** Python, Polars, DuckDB, Qdrant/BM25, EmbeddingGemma 2 (text), LangGraph, Streamlit.
- **Deliverable:** A reproducible ingestion pipeline, retrieval/agent evaluation, a cited investigation report, and a working local demo.
- **Not included:** VIN-specific recall status, diagnosis, prediction of future defects, causal claims, or a production-scale service.

## Success
The finished system produces a correct, source-traceable timeline, handles missing or ambiguous evidence without inventing connections, and demonstrates measurable retrieval performance against simpler baselines.

**Safety note:** RecallCase is an investigative research tool—not a diagnostic tool or an official recall checker. For a specific vehicle's open recalls, use [NHTSA's VIN lookup](https://www.nhtsa.gov/recalls).

**Primary data source:** [NHTSA Datasets & APIs](https://www.nhtsa.gov/nhtsa-datasets-and-apis).
