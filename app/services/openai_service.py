from openai import OpenAI
from app.core.config import settings
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"


class OpenAIService:

    async def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Chat legal con retrieval REAL y correcto.
        - Usa tu assistant configurado en OpenAI
        - Usa el vector store
        - Espera a que el run termine
        - Devuelve el mensaje FINAL del assistant
        """

        try:
            # 1. Crear thread si no existe
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            # 2. Crear el mensaje del usuario (sin attachments manuales)
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # 3. Crear el RUN con retrieval forzado
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.ASSISTANT_ID,
                model="gpt-4.1",
                temperature=0,
                top_p=0.1,
                instructions=(
                    "Obligatorio: Usa retrieval SIEMPRE.\n"
                    "Cita el ARTÍCULO EXACTO de las leyes subidas.\n"
                    "Si no existe, responde: 'no encontrado en la base documental'."
                ),
                tools=[
                    {
                        "type": "file_search",
                        "file_search": {
                            "vector_store_ids": [VECTOR_STORE_ID]
                        }
                    }
                ],
                tool_choice="file_search"  # Forzar que SIEMPRE use búsqueda
            )

            # 4. Esperar a que el run termine
            while True:
                current = client.beta.threads.runs.retrieve(
                    thread_id=thread_id,
                    run_id=run.id,
                )

                if current.status == "completed":
                    break

                if current.status in ["failed", "cancelled", "expired"]:
                    raise Exception(f"Run failed: {current.status}")

                time.sleep(1)

            # 5. Leer el último mensaje del assistant
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            final_message = messages.data[0].content[0].text.value

            return {
                "response": final_message,
                "thread_id": thread_id,
                "sources": []  # si quieres, luego te muestro cómo extraerlas
            }

        except Exception as e:
            raise Exception(str(e))