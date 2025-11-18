from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
import os

app = FastAPI()

# CORS para permitir tu frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # más seguro luego definimos tu dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"   # ← tu vector store real

class Query(BaseModel):
    question: str

@app.post("/query")
async def legal_query(body: Query):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Eres un asistente legal experto en leyes de Honduras."},
            {"role": "user", "content": body.question}
        ],
        extra_body={
            "vector_store_id": VECTOR_STORE_ID,
            "search": True
        }
    )

    return {
        "answer": response.choices[0].message.content
    }

@app.get("/")
def root():
    return {"status": "IUSNAUTA backend OK"}