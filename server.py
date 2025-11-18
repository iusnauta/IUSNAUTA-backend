from fastapi import FastAPI, Form
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
import os

app = FastAPI()

# Permitir CORS (importante para el frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"

@app.get("/healthz")
def health():
    return {"status": "ok"}

@app.post("/query")
def query_legal(query: str = Form(...)):
    """
    Consulta legal a IUSNAUTA usando Vector Store en OpenAI.
    """
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=query,
            reasoning={"effort": "medium"},
            extra_body={
                "search_contexts": [
                    {
                        "type": "vector_store",
                        "id": VECTOR_STORE_ID
                    }
                ]
            }
        )
        return {"answer": response.output_text}
    except Exception as e:
        return {"error": str(e)}