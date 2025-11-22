from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    def chat_with_rag(self, message: str, thread_id: str = None):

        try:
            # Crear thread si no existe
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            # Enviar solo el mensaje (SIN attachments)
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Ejecutar run con retrieval requerido (lo hace el assistant)
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,
                model="gpt-4.1",
                instructions=(
                    "Usa SIEMPRE recuperación documental del vector store.\n"
                    "Cita el artículo exacto del documento.\n"
                    "Si no existe, responde: 'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1
            )

            # Esperar run
            while True:
                result = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if result.status == "completed":
                    break
                if result.status in ["failed", "expired"]:
                    raise Exception("El run falló.")

            # Obtener respuesta
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            last = messages.data[0]

            return {
                "response": last.content[0].text.value,
                "thread_id": thread_id,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))