from openai import OpenAI
from app.core.config import settings

# Cliente síncrono → soporta attachments sin errores
client = OpenAI(api_key=settings.OPENAI_API_KEY)

class OpenAIService:

    def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Chat RAG usando Responses API (sin async porque async rompe attachments).
        """

        try:
            response = client.responses.create(
                model="gpt-4.1",
                input=[
                    {
                        "role": "user",
                        "content": message
                    }
                ],
                # Vector store ATTACHMENT CORRECTO
                attachments=[
                    {
                        "vector_store_id": settings.OPENAI_VECTOR_STORE_ID
                    }
                ],
                instructions=(
                    "Usa SIEMPRE retrieval del vector store.\n"
                    "Cita SOLO artículos EXACTOS del documento.\n"
                    "No inventes nada.\n"
                    "Si no encuentras el artículo, responde: "
                    "'no encontrado en la base documental'."
                ),
                temperature=0,
                top_p=0.1,
            )

            return {
                "response": response.output_text,
                "thread_id": None,
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))