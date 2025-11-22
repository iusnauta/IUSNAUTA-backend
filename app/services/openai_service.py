from openai import OpenAI
from app.core.config import settings
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    async def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Envía un mensaje al Assistant REAL que ya tiene el Vector Store conectado.
        NO usamos attachments manuales.
        NO usamos retrieval manual.
        NO metemos parámetros inexistentes.
        """

        try:
            # Crear thread si no existe
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            # Enviar mensaje del usuario
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # Ejecutar el assistant configurado en OpenAI
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,
                model="gpt-4.1",
                instructions=(
                    "Usa SIEMPRE el File Search. "
                    "Cita los artículos EXACTOS de las leyes hondureñas. "
                    "No inventes nada. "
                    "Si no lo encuentras en los documentos, responde: "
                    "'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1
            )

            # Esperar a que termine
            while True:
                run_check = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id
                )

                if run_check.status == "completed":
                    break

                if run_check.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed: {run_check.last_error}")

                time.sleep(0.5)

            # Recuperar la respuesta final textual
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            last_msg = messages.data[0]

            text = last_msg.content[0].text.value

            # Si hay referencias de File Search, extraerlas
            sources = []
            for item in last_msg.content[0].text.annotations:
                if hasattr(item, "file_id"):
                    sources.append(item.file_id)

            return {
                "response": text,
                "thread_id": thread_id,
                "sources": sources
            }

        except Exception as e:
            raise Exception(f"Error en Assistant: {str(e)}")