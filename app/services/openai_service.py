from openai import OpenAI
from app.core.config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.OPENAI_ASSISTANT_ID
        self.vector_store_id = settings.OPENAI_VECTOR_STORE_ID

    def chat_with_rag(self, message: str, thread_id: str | None):

        # STEP 1: File search (retrieval manual)
        search = self.client.files.search(
            vector_store_id=self.vector_store_id,
            query=message,
            max_results=5
        )

        # If no chunks found → return STRICT grounding response
        if not search.data or len(search.data) == 0:
            return {
                "response": (
                    "⚠️ No se encontró ninguna referencia legal en los documentos "
                    "indexados. Reformula tu pregunta o asegúrate de que la ley "
                    "esté cargada en el sistema."
                ),
                "thread_id": thread_id or "null",
                "sources": []
            }

        # Extract sources
        sources = []
        for hit in search.data:
            sources.append({
                "filename": hit.filename,
                "score": hit.score,
            })

        # Create thread if needed
        if thread_id is None:
            thread = self.client.beta.threads.create()
            thread_id = thread.id

        # Send message to the thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=f"""
PREGUNTA:
{message}

REGLAS OBLIGATORIAS:
1. SOLO puedes responder usando información que provenga de mis documentos cargados.
2. Cita SIEMPRE el artículo exacto, con número de artículo.
3. Si la información no está en los documentos proporcionados, responde:
   "No existe referencia en los documentos indexados."

AQUÍ ESTÁN LOS FRAGMENTOS RELEVANTES ENCONTRADOS:
{sources}
"""
        )

        # Run assistant
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        # Wait for completion
        while True:
            run_check = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_check.status == "completed":
                break

            if run_check.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed: {run_check.status}")

        # Get final message
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        last = messages.data[0]

        answer = last.content[0].text.value

        return {
            "response": answer,
            "thread_id": thread_id,
            "sources": sources
        }