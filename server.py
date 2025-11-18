from fastapi import FastAPI, Form
import chromadb
from openai import OpenAI

app = FastAPI()

# ---------------------------
# 1. Conectar con tu base legal
# ---------------------------
chroma_client = chromadb.PersistentClient(path="./legal_db")
collection = chroma_client.get_collection("honduras_legal")

# ---------------------------
# 2. Cliente OpenAI (nuevo SDK)
# ---------------------------
client = OpenAI()  # Usa OPENAI_API_KEY de Windows automáticamente


def search_legal(query: str):
    """Busca los 5 fragmentos más relevantes de la base hondureña."""
    results = collection.query(
        query_texts=[query],
        n_results=5
    )
    return "\n\n---\n\n".join(results["documents"][0])


@app.post("/query")
async def legal_query(query: str = Form(...)):
    # 1. Recuperar contexto legal
    context = search_legal(query)

    # 2. Llamar a OpenAI usando el endpoint correcto del SDK 2024+
    response = client.chat.completions.create(
        model="gpt-4.1",      # usa el modelo que tengas disponible
        messages=[
            {
                "role": "system",
                "content": "Eres IUSNAUTA, analista jurídico hondureño experto."
            },
            {
                "role": "user",
                "content": f"""
Consulta jurídica: {query}

Contexto legal hondureño encontrado:
{context}

Produce un análisis jurídico claro, estructurado y fundamentado.
"""
            }
        ]
    )

    return {
        "respuesta": response.choices[0].message["content"],
        "base_usada": context
    }