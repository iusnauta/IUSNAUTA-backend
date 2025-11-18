from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import openai
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.vector_stores.opensearch import OpenSearchVectorStore
from llama_index.core import StorageContext
import os
import uvicorn

# ===========================
# CONFIG
# ===========================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("ERROR: OPENAI_API_KEY no está configurada en Render")
    raise SystemExit

openai.api_key = OPENAI_API_KEY

app = FastAPI()

# Permitir CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===========================
# RUTA DE PRUEBA
# ===========================
@app.get("/")
def root():
    return {"status": "IUSNAUTA backend funcionando correctamente 🚀"}

# ===========================
# CHAT BÁSICO
# ===========================
@app.post("/chat")
async def chat_endpoint(payload: dict):
    question = payload.get("question", "")

    if not question:
        return {"error": "Falta 'question' en el JSON"}

    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": question}],
        )
        answer = completion.choices[0].message["content"]

        return {"answer": answer}

    except Exception as e:
        return {"error": str(e)}

# ===========================
# HEALTHCHECK (Render lo usa)
# ===========================
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# ===========================
# EJECUCIÓN LOCAL (Render NO usa esto)
# ===========================
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=10000, reload=True)