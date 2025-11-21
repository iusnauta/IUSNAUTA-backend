from openai import OpenAI
from app.config import settings

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.assistant_id = settings.OPENAI_ASSISTANT_ID

    async def chat_with_rag(self, message: str, thread_id: str | None):
        """
        Envía un mensaje al Assistant de OpenAI usando su Thread RAG.
        Si no existe thread, se crea uno nuevo.
        """
        # Crear thread si no existe todavía
        if thread_id is None:
            thread = self.client.beta.threads.create()
            thread_id = thread.id

        # Enviar mensaje al thread
        self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=message
        )

        # Lanzar el run contra tu assistant configurado
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id
        )

        # Esperar a que termine
        while True:
            run_check = self.client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            if run_check.status == "completed":
                break

            if run_check.status in ["failed", "cancelled", "expired"]:
                raise Exception(f"Run failed: {run_check.status}")

        # Obtener la respuesta final
        messages = self.client.beta.threads.messages.list(thread_id=thread_id)
        last = messages.data[0]

        return {
            "response": last.content[0].text.value,
            "thread_id": thread_id,
            "sources": []
        }