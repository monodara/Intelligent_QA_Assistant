import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

def check_backend_health():
    """
    Check backend readiness (via HTTP).
    """
    print("🔄 Checking backend readiness via FastAPI...")
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is ready!")
            return True
        else:
            print(f"⚠️ Backend not ready: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False


def load_knowledge_base():
    """
    Request backend to reload knowledge base.
    """
    with st.spinner("Loading knowledge base from backend..."):
        try:
            response = requests.post(f"{BACKEND_URL}/reload_kb", timeout=300)
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    st.success("✅ Knowledge base loaded successfully!")
                    return True
                else:
                    st.error(f"Knowledge base loading failed: {result.get('message', 'Unknown error')}")
                    return False
            else:
                st.error(f"Backend returned error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Knowledge base loading failed: {e}")
            st.error(f"Knowledge base loading failed: {e}")
            return False


def get_kb_status():
    """
    Get knowledge base status from backend.
    """
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {"is_loaded": False, "error": f"HTTP {response.status_code}"}
    except Exception as e:
        print(f"❌ Failed to get KB status: {e}")
        return {"is_loaded": False, "error": str(e)}


def ensure_backend_ready():
    """
    Ensure the backend service is running.
    """
    try:
        return check_backend_health()
    except Exception as e:
        print(f"❌ Failed to ensure backend is ready: {e}")
        return False
