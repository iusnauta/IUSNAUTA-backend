from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"  # tu store real


class OpenAIService:

    def chat_with_rag(self, message: str, thread_id: str = None):

        try:
            # Crear thread si no existe
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            # Enviar mensaje con retrieval obligatorio
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
                attachments=[
                    {
                        "type": "vector_store",
                        "vector_store_id": VECTOR_STORE_ID
                    }
                ]
            )

            # Ejecutar run
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,  # ← FIX
                model="gpt-4.1",
                instructions=(
                    "Usa SIEMPRE retrieval real.\n"
                    "Cita SIEMPRE el artículo exacto.\n"
                    "Si no existe, responde: 'no encontrado en la base documental'.\n"
                    "No inventes nada bajo ninguna circunstancia."
                ),
                temperature=0,
                top_p=0.1,
                retrieval={"tool_choice": "required"}
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

            # Leer mensajes
            messages = client.beta.threads.messages.list(thread_id=thread_id)
            last = messages.data[0]

            return {
                "response": last.content[0].text.value,
                "thread_id": thread_id,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))