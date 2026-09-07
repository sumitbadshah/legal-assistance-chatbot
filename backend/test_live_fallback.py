import os
import time
from fastapi.testclient import TestClient

os.environ["DATABASE_URL"] = "sqlite:///./legal_assistant.db"

from app.main import app
from app.database import engine, Base

# Set up testclient
client = TestClient(app)

def run_test():
    out = []
    try:
        Base.metadata.create_all(bind=engine)
        username = f"testuser_{int(time.time())}@example.com"
        pwd = "password123!"

        out.append(f"[*] Registering test user: {username}...")
        res = client.post("/auth/register", json={"email": username, "password": pwd})
        if res.status_code not in (200, 201):
            out.append(f"Registration failed: {res.json()}")
            return
        
        # In this backend's register route, it directly logs you in and returns the token!
        token = res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        out.append("\n[*] Sending OUT-OF-CORPUS question: 'How do I bake a chocolate cake?'")
        chat_res = client.post("/chat", json={"message": "How do I bake a chocolate cake?", "language": "English"}, headers=headers)
        if chat_res.status_code != 200:
            out.append(f"Chat failed: {chat_res.json()}")
        else:
            data = chat_res.json()
            messages = data["messages"]
            last_msg = messages[-1]
            
            out.append("\n=== GEMINI RESPONSE ===")
            out.append(last_msg["content"])
            out.append("=======================")
            out.append(f"\nSources: {last_msg.get('sources')}")
            if last_msg.get("sources") and last_msg["sources"][0].get("fallback"):
                out.append("\n✅ SUCCESS: The chatbot successfully fell back to general knowledge (marked as fallback)!")
            else:
                out.append("\n❌ FAILED: Did not see fallback flag.")
    except Exception as e:
        out.append(f"Exception happened: {e}")
    finally:
        with open("test_result.log", "w", encoding="utf-8") as f:
            f.write("\n".join(out))

if __name__ == "__main__":
    run_test()
