from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    async def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Chat RAG usando OpenAI Responses API (formato nuevo).
        """

        try:
            # Responses API no usa threads. Los ignoramos.
            response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                # 🔥 Aquí va el vector store
                attachments=[
                    {
                        "vector_store_id": settings.OPENAI_VECTOR_STORE_ID
                    }
                ],
                # 🔥 Instrucciones súper estrictas al modelo
                instructions=(
                    "Usa SIEMPRE retrieval del vector store.\n"
                    "Cita SOLO artículos EXACTOS.\n"
                    "No inventes.\n"
                    "Si no encuentras el artículo, responde: 'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1
            )

            # Responses API devuelve texto así:
            output_text = response.output_text

            return {
                "response": output_text,
                "thread_id": None,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))