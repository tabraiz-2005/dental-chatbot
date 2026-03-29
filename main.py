# main.py

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from groq import Groq
from dotenv import load_dotenv
import os

from rag import load_clinic_data, search_clinic_data

# Load environment variables
load_dotenv()

app = FastAPI()

# CORS (frontend safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔐 Groq setup
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("⚠️ WARNING: GROQ_API_KEY is missing!")

client = Groq(api_key=GROQ_API_KEY)


# ✅ ROOT → SERVE UI
@app.get("/")
def serve_home():
    if os.path.exists("index.html"):
        return FileResponse("index.html")
    return {"error": "index.html not found"}


# ✅ HEALTH CHECK (important for Render)
@app.get("/health")
def health():
    return {"status": "ok"}


# ✅ STARTUP → LOAD CLINIC DATA
@app.on_event("startup")
async def startup_event():
    try:
        if os.path.exists("clinic_data.txt"):
            count = load_clinic_data("clinic_abc", "clinic_data.txt")
            print(f"✅ Loaded {count} chunks for clinic: clinic_abc")
        else:
            print("⚠️ clinic_data.txt not found")
    except Exception as e:
        print(f"❌ Error loading clinic data: {e}")


# ✅ REQUEST MODEL
class ChatRequest(BaseModel):
    message: str
    clinic_id: str = "clinic_abc"


# ✅ CHAT ENDPOINT
@app.post("/chat")
def chat(request: ChatRequest):

    if not GROQ_API_KEY:
        raise HTTPException(status_code=500, detail="Missing GROQ_API_KEY")

    try:
        relevant_chunks = search_clinic_data(
            request.clinic_id,
            request.message
        )

        if relevant_chunks:
            context = "\n\n".join([
                f"- {chunk}" for chunk in relevant_chunks
            ])

            system_prompt = f"""
You are a professional dental AI receptionist.

You have TWO roles:
1. Answer clinic-specific questions using ONLY provided clinic data
2. Answer general dental questions safely and helpfully

STRICT RULES:
- Never hallucinate clinic details
- If clinic info is missing → say "please contact the clinic directly"
- Keep answers short, clear, and professional

CLINIC DATA:
{context}
"""
        else:
            system_prompt = """
You are a friendly dental clinic receptionist.

Answer general dental questions, give safe advice,
and be warm, polite, and professional.
"""

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": request.message}
            ],
            temperature=0.3,
            max_tokens=500
        )

        reply = response.choices[0].message.content

        return {
            "reply": reply,
            "clinic_id": request.clinic_id
        }

    except Exception as e:
        print(f"❌ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


# ✅ LOAD DATA ENDPOINT (OPTIONAL)
@app.post("/load-data/{clinic_id}")
def load_data(clinic_id: str, file_path: str):
    try:
        count = load_clinic_data(clinic_id, file_path)
        return {"message": f"Loaded {count} chunks for {clinic_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
