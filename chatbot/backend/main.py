import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
import pandas as pd
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import httpx

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")
CHROMA_DIR = os.getenv("CHROMA_DIR", "chroma_db")

app = FastAPI()

# Initialize embedding model and vector store
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.Client(Settings(chroma_db_impl="duckdb+parquet", persist_directory=CHROMA_DIR))
collection = chroma_client.get_or_create_collection("catalog")


def build_index():
    if collection.count() > 0:
        return
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "data", "catalog.csv"))
    texts = (df["name"] + ". " + df["description"]).tolist()
    ids = df["id"].astype(str).tolist()
    embeddings = embedder.encode(texts).tolist()
    collection.add(ids=ids, documents=texts, embeddings=embeddings)
    chroma_client.persist()


build_index()


class ChatRequest(BaseModel):
    prompt: str


class ChatResponse(BaseModel):
    reply: str


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    query_embedding = embedder.encode(req.prompt).tolist()
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    docs = results.get("documents", [[]])[0]
    context = "\n".join(docs)
    final_prompt = (
        "Ești un consultant virtual pentru un magazin de rolete.\n"
        "Ai următoarele informații:\n"
        f"{context}\n"
        "Clientul întreabă:\n"
        f"{req.prompt}"
    )
    try:
        resp = httpx.post(f"{OLLAMA_URL}/api/generate", json={"model": OLLAMA_MODEL, "prompt": final_prompt, "stream": False})
        resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    data = resp.json()
    return {"reply": data.get("response", "")}


@app.get("/health")
async def health():
    return {"status": "ok"}
