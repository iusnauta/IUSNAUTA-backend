from openai import OpenAI
from app.core.config import settings
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"


class OpenAIService:

    def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Implementación síncrona correcta (igual que test_rag.py)
        """

        try:
            # 1. Crear thread si no viene en request
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            # 2. Crear mensaje
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message
            )

            # 3. Crear run con retrieval forzado
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.ASSISTANT_ID,
                model="gpt-4.1",
                temperature=0,
                top_p=0.1,
                instructions=(
                    "Usa SIEMPRE retrieval. "
                    "Cita artículos EXACTOS. "
                    "Si no está en los PDFs, responde: 'no encontrado en la base documental'."
                ),
                tools=[
                    {
                        "type": "file_search",
                        "file_search": {
                            "vector_store_ids": [VECTOR_STORE_ID]
                        }
                    }
                ],
                tool_choice="file_search"
            )

            # 4. Esperar a que termine
            while True:
                r = client.beta.threads.runs.retrieve(
                    thread_id=thread_id, run_id=run.id
                )
                if r.status == "completed":
                    break
                if r.status in ["failed", "cancelled"]:
                    raise Exception(f"Run failed: {r.status}")
                time.sleep(1)

            # 5. Leer respuesta final del assistant
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            final_text = messages.data[0].content[0].text.value

            return {
                "response": final_text,
                "thread_id": thread_id,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))