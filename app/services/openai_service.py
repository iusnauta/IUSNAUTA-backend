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

            # Añadir mensaje + vector store
            client.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=message,
                attachments=[
                    {
                        "type": "vector_store",
                        "vector_store_id": settings.OPENAI_VECTOR_STORE_ID
                    }
                ]
            )

            # Ejecutar el asistente
            run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=settings.OPENAI_ASSISTANT_ID,
            )

            # Esperar respuesta
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