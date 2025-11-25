from openai import AsyncOpenAI
from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    async def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Chat RAG usando OpenAI Responses API (formato nuevo) + async correcto.
        """

        try:
            # REAL: Responses API async
            response = await client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                attachments=[
                    {
                        "vector_store_id": settings.OPENAI_VECTOR_STORE_ID,
                        "type": "vector_store"
                    }
                ],
                instructions=(
                    "Usa SIEMPRE retrieval.\n"
                    "Cita SOLO artículos EXACTOS.\n"
                    "No inventes.\n"
                    "Si no encuentras, responde: 'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1
            )

            output = response.output_text

            return {
                "response": output,
                "thread_id": None,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))