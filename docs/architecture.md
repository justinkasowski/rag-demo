```text
CI/CD With Cloud Run build triggers (Github synchronyzation)
Deploys using cloudbuild.yaml

User
  |                   | <-------> Google Monitoring
  v                   | <-------> Firebase Authentication/Backend
FastAPI API   --------|
  |                   | --------> Cloud SQL Postgres Data/Vector Storage
  v                   
RAG Pipeline
  |      ----------|
  v                v
Chroma/pgvector   Ollama
  |
  v
PDF Documents
```

```                         
|-- README.md                     Project overview 
|-- cloudbuild.yaml               Cloud Run configuration  
|--docker-compose.yml             Defines Ollama and FastAPI containers to run locally
|-- Dockerfile                    Project dockerfile for cloud deployment

|-- docs/                         |=== Project documentation ===|
   
|-- data/                         |===  Persistent runtime data ===|
  |-- pdfs/                       |== Source documents used for RAG indexing ==|
  |-- chroma/                     |== Persisted local vector database storage ==|
    
|-- services/                     |===  Application services === |
 |-- api/                         |== FastAPI backend service ==|      
   |-- config.py                  Project Configuration
   |-- main.py                    FastAPI API endpoints
   |-- requirements.txt           Python dependencies
   |-- start.sh                   Start script for deployed container
        
   |-- integrations               |= Integration with webhooks =|
     |-- integrations_handler.py  Handles planning and calling the correct integration
     |-- schemas.py               Structures for integration plans and messages
     
       |-- planners               | Integration Planners |
         |-- llm_planner.py       Calls the LLM to determine which integration/channel
         |-- rules_planner.py     Rule based planner to reduce total LLM traffic
         
     |-- rag/                     | RAG pipeline components |
       |-- rag_store.py           Initializes vector store
       |-- ingest.py              PDF ingestion and embedding
       |-- retrieve.py            Retrieval and prompt construction
       
    |-- sql/                      |= SQL client utilities =|
      |-- bug_reports.py          SQL method for bug reports
      |-- database.py             Database initialization
      
   |-- static/                    |= HTML UI / Frontend =|
      |-- app.js                  Javascript functions/Firebase authentication
      |-- index.html              Webpage UI
      |-- style.css               Styling for UI
```