from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VECTOR_STORE_ID = "vs_691c4e07f84c8191b366aa54cfe795a1"  # tu store real

class OpenAIService:

    async def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Envía pregunta + retrieval al assistant
        """

        try:
            if thread_id is None:
                thread = client.beta.threads.create()
                thread_id = thread.id

            response = client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
                attachments=[
                    {
                        "vector_store_id": VECTOR_STORE_ID,
                        "type": "vector_store"
                    }
                ]
            )

            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.ASSISTANT_ID,
                model="gpt-4.1",
                instructions=(
                    "Usa SIEMPRE retrieval. "
                    "Cita los artículos EXACTOS. "
                    "No inventes. "
                    "Si no encuentras, responde 'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1,
                retrieval={"tool_choice": "required"}
            )

            result = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )

            return {
                "response": result.output_text,
                "thread_id": thread_id,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))