from openai import OpenAI
from app.core.config import settings
import time


client = OpenAI(api_key=settings.OPENAI_API_KEY)


class OpenAIService:

    # ======================================================
    #   1. SUBIR PDF Y ENVIARLO AL VECTOR STORE
    # ======================================================
    async def upload_pdf(self, file_bytes: bytes, filename: str):
        uploaded = client.files.create(
            file=(filename, file_bytes),
            purpose="assistants"
        )

        client.vector_stores.files.create(
            vector_store_id=settings.OPENAI_VECTOR_STORE_ID,
            file_id=uploaded.id
        )

        return {
            "filename": filename,
            "file_id": uploaded.id,
            "status": "indexed"
        }

    # ======================================================
    #   2. CHAT PRINCIPAL CON RAG (THREADS + RUNS)
    # ======================================================
    async def chat(self, message: str, thread_id: str | None):

        # Crear thread si no existe
        if thread_id is None:
            thread = client.threads.create()
            thread_id = thread.id

        # Añadir mensaje del usuario
        client.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Crear ejecución del assistant
        run = client.threads.runs.create(
            thread_id=thread_id,
            assistant_id=settings.OPENAI_ASSISTANT_ID
        )

        # Polling hasta que termine
        while True:
            status = client.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if status.status in ["completed", "failed"]:
                break

            time.sleep(0.5)

        # Obtener los mensajes del thread
        messages = client.threads.messages.list(thread_id=thread_id)

        # Último mensaje del assistant
        answer = messages.data[0].content[0].text.value

        # Extraer citas del vector store (si existen)
        sources = []
        for msg in messages.data:
            if msg.role == "assistant":
                if hasattr(msg, "annotations"):
                    for ann in msg.annotations:
                        if hasattr(ann, "file_citation"):
                            sources.append({
                                "file_name": ann.file_citation.file_id,
                                "quote": ann.file_citation.quote or ""
                            })

        return {
            "response": answer,
            "thread_id": thread_id,
            "sources": sources
        }


# Instancia global
openai_service = OpenAIService()