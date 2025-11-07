from fastapi import FastAPI
from pydantic import BaseModel
from ..api_service import initialize_backend_components, handle_chat_query, reload_knowledge_base

app = FastAPI()

# global objects initialized once
@app.on_event("startup")
async def startup_event():
    print("🚀 Initializing backend components (only once at startup)...")
    await initialize_backend_components()
    print("✅ Backend initialization complete!")

class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
async def ask(request: QueryRequest):
    # Use the global components initialized at startup
    response = await handle_chat_query(request.query)
    return response

@app.post("/reload_kb")
async def reload_kb():
    # Reload knowledge base
    result = await reload_knowledge_base()
    return result

@app.get("/status")
async def status():
    return {"status": "ok", "message": "Backend is running"}
