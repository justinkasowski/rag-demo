from pathlib import Path
from typing import Optional

import requests

import firebase_admin
from firebase_admin import auth
from google.cloud import firestore
from google.cloud.firestore_v1 import Increment

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel


from config import AVAILABLE_CORPORA, MODEL, OLLAMA_KEEP_ALIVE, OLLAMA_URL, LOCAL_RUN
from integrations.integrationsHandler import plan_message, send_message
from integrations.schemas import MessagePlan, SendMessageRequest, SendMessageResponse, IntegrationPlanRequest
from rag.ingest import ingest_corpus
from rag.retrieve import corpus_has_documents, rag_answer

QUERY_LIMIT = 100
runCount=0

db = None

if not LOCAL_RUN:
    firebase_admin.initialize_app()
    db = firestore.Client()


class PromptRequest(BaseModel):
    prompt: str
    keep_alive: Optional[str] = None


class DirectQueryResponse(BaseModel):
    model: str
    response: str
    prompt: str


class QueryRequest(BaseModel):
    corpus: str
    question: str
    k: int = 4
    section: Optional[str] = None
    document_type: Optional[str] = None
    keep_alive: Optional[str] = None

class IngestRequest(BaseModel):
    corpus: str
    clean_rebuild: bool = False

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/firestore-test")
def firestore_test():
    doc = db.collection("test").document("ping")
    doc.set({"ok": True})
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def home():
    html = Path("static/index.html").read_text()
    html = html.replace("__LOCAL_RUN__", str(LOCAL_RUN).lower())
    return HTMLResponse(html)


@app.post("/warmup")
def warmup():
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": "",
            "stream": False,
            "keep_alive": OLLAMA_KEEP_ALIVE,
        },
        timeout=300,
    )
    r.raise_for_status()
    return {"status": "warmed", "model": MODEL}


@app.post("/rag/ingest")
def rag_ingest(req: IngestRequest):
    try:
        corpus = req.corpus.strip().lower()

        if corpus == "all":
            results = {}
            for name in AVAILABLE_CORPORA:
                results[name] = ingest_corpus(name, clean_rebuild=req.clean_rebuild)
            return {
                "corpus": "all",
                "clean_rebuild": req.clean_rebuild,
                "results": results,
            }

        return ingest_corpus(corpus, clean_rebuild=req.clean_rebuild)

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/directQuery", response_model=DirectQueryResponse)
def direct_query(req: PromptRequest, authorization: Optional[str] = Header(None)):
    if not LOCAL_RUN:
        uid = get_uid_from_auth_header(authorization)
        run_count = increment_user_run_count(uid)

        if run_count > 100:
            raise HTTPException(
                status_code=403,
                detail="Users limited to 100 queries, contact Justin (justin.kasowski@gmail.com)"
            )

    r = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": req.prompt,
            "stream": False,
            "keep_alive": req.keep_alive or OLLAMA_KEEP_ALIVE,
        },
        timeout=300,
    )
    r.raise_for_status()
    data = r.json()

    response_payload = {
        "model": MODEL,
        "response": data.get("response", "").strip(),
        "prompt": req.prompt,
    }

    return response_payload


@app.post("/rag/query")
def rag_query(req: QueryRequest, authorization: Optional[str] = Header(None)):
    if not LOCAL_RUN:
        uid = get_uid_from_auth_header(authorization)
        run_count = increment_user_run_count(uid)

        if run_count > 100:
            raise HTTPException(
                status_code=403,
                detail="Users limited to 100 queries, contact Justin (justin.kasowski@gmail.com)"
            )

    try:
        corpus = req.corpus.strip().lower()
        auto_ingested = False
        ingest_result = None

        if corpus == "all":
            missing = []
            for name in AVAILABLE_CORPORA:
                if not corpus_has_documents(name):
                    missing.append(name)

            if missing:
                auto_ingested = True
                ingest_result = {}
                for name in missing:
                    ingest_result[name] = ingest_corpus(name, clean_rebuild=False)
        else:
            if not corpus_has_documents(corpus):
                auto_ingested = True
                ingest_result = ingest_corpus(corpus, clean_rebuild=False)

        response_payload = rag_answer(
            corpus=corpus,
            question=req.question,
            k=req.k,
            section=req.section,
            document_type=req.document_type,
            keep_alive=req.keep_alive or OLLAMA_KEEP_ALIVE,
            include_prompt=True,
        )

        response_payload["auto_ingested"] = auto_ingested
        response_payload["ingest_result"] = ingest_result

        return response_payload

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/integrations/plan")
def integrations_plan(req: IntegrationPlanRequest):
    try:
        result = plan_message(
            instruction=req.instruction,
            keep_alive=req.keep_alive or OLLAMA_KEEP_ALIVE,
        )
        return {
            "plan": result["plan"],
            "prompt": result["prompt"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/integrations/send", response_model=SendMessageResponse)
def integrations_send(req: SendMessageRequest):
    try:
        result = send_message(req.plan, req.message)
        return SendMessageResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/rag/status")
def rag_status():
    status = {}

    for corpus in ["hr", "policy", "sales"]:
        try:
            status[corpus] = corpus_has_documents(corpus)
        except Exception:
            status[corpus] = False

    return {"corpus_status": status}

@app.get("/health")
def health():
    return {
        "status": "ok",
        "model": MODEL,
        "ollama_url": OLLAMA_URL,
        "corpora": AVAILABLE_CORPORA,
    }

def get_uid_from_auth_header(authorization: Optional[str]) -> Optional[str]:
    if LOCAL_RUN:
        return "local-dev-user"

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing auth token")

    token = authorization.split("Bearer ", 1)[1].strip()

    try:
        decoded = auth.verify_id_token(token)
        return decoded["uid"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid auth token")


def increment_user_run_count(uid: str) -> int | None:
    if LOCAL_RUN or (db is None):
        return None

    user_ref = db.collection("users").document(uid)
    user_ref.set(
        {
            "run_count": Increment(1),
            "last_run_at": firestore.SERVER_TIMESTAMP,
        },
        merge=True,
    )
    snap = user_ref.get()
    return snap.to_dict().get("run_count", 0)