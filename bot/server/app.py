from fastapi import FastAPI
from pydantic import BaseModel
from ..api_service import initialize_backend_components, handle_chat_query, reload_knowledge_base

app = FastAPI()

# ✅ 初始化时只加载一次（全局缓存）
@app.on_event("startup")
def startup_event():
    print("🚀 Initializing backend components (only once at startup)...")
    initialize_backend_components()
    print("✅ Backend initialization complete!")

# 请求模型
class QueryRequest(BaseModel):
    query: str

@app.post("/ask")
def ask(request: QueryRequest):
    # ✅ 直接使用已初始化的全局组件
    response = handle_chat_query(request.query)
    return response

@app.post("/reload_kb")
def reload_kb():
    # ✅ 重新加载知识库
    result = reload_knowledge_base()
    return result

@app.get("/status")
def status():
    return {"status": "ok", "message": "Backend is running"}
