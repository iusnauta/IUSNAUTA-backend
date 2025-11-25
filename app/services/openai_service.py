from openai import OpenAI
from app.core.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)

VECTOR_STORE_ID = settings.OPENAI_VECTOR_STORE_ID  # el real

class OpenAIService:

    def chat_with_rag(self, message: str, thread_id: str = None):
        """
        Nuevo sistema con Responses API.
        Retrieval directo desde el vector store.
        Sin threads, sin runs, sin API beta.
        """

        try:
            response = client.responses.create(
                model="gpt-4.1",
                input=message,
                retrieval={
                    "vector_store_ids": [VECTOR_STORE_ID]
                },
                # Parámetros para ser MÁS EXACTO y NO inventar:
                temperature=0,
                top_p=0.1,
                max_output_tokens=800,
                # Esto fuerza a usar retrieval siempre
                reasoning={"force": True}
            )

            # Extraer texto final
            output_text = response.output_text

            return {
                "response": output_text,
                "thread_id": "N/A",
                "sources": []
            }

        except Exception as e:
            raise Exception(str(e))