# Internal Chatbot with FastAPI and React

This project provides a simple RAG chatbot using a FastAPI backend and a React frontend.

## Requirements
- **Python** 3.10+
- **Node** 18+

## Setup

### Backend
```bash
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```
The React app runs on `http://localhost:5173` by default and expects the backend at `http://localhost:8000`.

## Environment Variables
Copy `.env.example` to `.env` and adjust if necessary:
- `OLLAMA_URL` – base URL of your Ollama instance
- `OLLAMA_MODEL` – model name to use (e.g. `mistral`)
- `CHROMA_DIR` – where the Chroma database is stored

## Data and Embeddings
Edit `data/catalog.csv` to update product info. Remove the folder specified by `CHROMA_DIR` to regenerate embeddings on next start.

## Smoke Test
With the backend running, try:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"prompt":"vreau rolete maro pentru baie"}'
```
Example response:
```json
{"reply":"Roletele din material rezistent la umiditate potrivite pentru bai."}
```

## Docker
You can run the backend in Docker:
```bash
docker-compose up --build
```
