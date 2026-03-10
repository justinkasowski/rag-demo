# Version History

This document tracks major milestones and planned future development.

---

## Version 0.9 – Initial Prototype

**Goal:** Deploy a cloud-based CI/CD RAG tool.

Features:
- Docker containerization
- Cloud Run deployment
- Cloud SQL database
- FastAPI backend
- Ollama model inference
- Basic RAG retrieval
- Chroma vector storage
- Web interface
- Firebase authentication and rate limiting
- SQL storage for bug reports and future fine-tuning data
- Slack / Discord integrations
- Custom domain support
- Health monitoring

---

## Version 1.0 – Hosted Vector Database

**Goal:** Production-grade vector storage.

Planned changes:
- Migrate vector storage to PostgreSQL + pgvector
- Keep Chroma for local development runs
- Optional Cloud Storage document storage
- Improved ingestion pipeline

*Timeline:* 1-2 days 

---

## Version 1.1 – Multi-Tenant Support

**Goal:** Support multiple organizations.

Planned changes:
- Switch from `corpus / section / document_type` to `company / corpus / section`
- Corpus management UI with Cloud Storage-backed PDF uploads
- Tenant-specific integrations
- Example vertical support such as healthcare diagnosis-code review workflows


*Timeline:* 5-10 days 

---

## Version 1.2 – Advanced Retrieval

**Goal:** Improve answer accuracy.

Planned changes:
- Ability to specify embedding models and chunking strategies
- Hybrid search using embeddings plus keyword search
- Semantic re-ranking
- Custom prompt definitions


*Timeline:* 5-10 days 


---

## Version 2.0 – Scalable Cloud Structure

**Goal:** Improve scalability and production readiness.

Planned changes:
- Improved scaling architecture
- Better separation of compute, document storage, and vector storage
- More robust monitoring and operational tooling


*Timeline:* 5-10 days 

---

## Version 3.0 – Organization-Specific Model Fine-Tuning

**Goal:** Support fine-tuning LLM models for specific organizations.

Planned changes:
- Fine-tunable LLM models
- LoRA-based fine-tuning with Unsloth
- Organization-specific model variants


*Timeline:* 5-10 days 

---

## Version 3.1 – Fine-Tuning Interface

**Goal:** Provide a UI for managing model fine-tuning workflows.

Planned changes:
- UI for exploring fine-tuning workflows
- Ability to switch between model versions
- SQL interface for viewing reported hallucinations and model bug data

*Timeline:* 5-10 days 
