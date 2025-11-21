from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    # --- Subir documentos y meterlos al Vector Store ---
    async def upload_pdf(self, file_bytes: bytes, filename: str):
        uploaded = client.files.create(
            file=(filename, file_bytes),
            purpose="assistants"
        )

        # Añadir al Vector Store
        client.vector_stores.files.create(
            vector_store_id=settings.OPENAI_VECTOR_STORE_ID,
            file_id=uploaded.id
        )

        return {
            "filename": filename,
            "file_id": uploaded.id,
            "status": "indexed"
        }

    # --- Chat principal con RAG ---
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

        # Ejecutar assistant
        run = client.threads.runs.create(
            thread_id=thread_id,
            assistant_id=settings.OPENAI_ASSISTANT_ID
        )

        # Esperar a que termine
        while True:
            status = client.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if status.status in ["completed", "failed"]:
                break

        # Obtener respuesta final
        messages = client.threads.messages.list(thread_id=thread_id)

        # La última respuesta del assistant
        answer = messages.data[0].content[0].text.value

        # Obtener fuentes si existen
        sources = []
        for m in messages.data:
            if m.role == "assistant" and hasattr(m, "annotations"):
                for ann in m.annotations:
                    if hasattr(ann, "file_citation"):
                        file_name = ann.file_citation.file_id
                        citation = ann.file_citation.quote or ""
                        sources.append({
                            "file_name": file_name,
                            "citation": citation
                        })

        return {
            "response": answer,
            "thread_id": thread_id,
            "sources": sources
        }


# Instancia global importable
openai_service = OpenAIService()