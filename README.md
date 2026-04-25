# RAG-HL/CDC Reference Implementation

Minimal methodological reference for RAG-HL/CDC (Retrieval-Augmented Generation with Human-in-the-Loop for Contextual Data Correction).  
This repository contains reproducible scripts, synthetic case definitions, prompt evolution history, and anonymized intervention logs to support the empirical claims of the associated journal submission.

# Purpose
- Demonstrate routing logic (`hitl_router.py`)
- Show RAG retrieval & recommendation generation (`rag_pipeline.py`)
- Track prompt refinement across iterations
- Provide anonymized HITL logs & evaluation metrics
- Ensure full traceability & reproducibility

# Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt  # (empty: uses only stdlib)
python code/rag_pipeline.py
python code/hitl_router.py

##  Data structure

### Main files (`data/`)

- `interventions_anonymized.json`: Consolidated logs from the 4 case studies (healthcare, finance, recruitment, education)
- `generated_rules.json`: Business rules automatically learned after HITL validation
- `evaluation_metrics.csv`: Quantitative performance metrics of the RAG-HL/CDC framework
- `synthetic_cases/`: Individual files per domain (`healthcare.json`, `fraude.json`, etc.)


###  Metadata (`metadata/`)
- `data_dictionary.csv`: Complete schema of JSON fields (including `rag_component`, `hitl_intervention`, `audit_trail`)
- `retrieval_sources.md`: Verifiable external sources (HAS 2024, OSMP 2024, French Labor Code 2026, MENFP Circular 2025 087X25)  
- `ethical_statement.md`: GDPR compliance, Moroccan Law 09-08, academic fair use


##  Validation
Before submission, run:
```bash
python code/validate_synthetic_data.py