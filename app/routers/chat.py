from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.openai_handler import openai_service

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat_with_lex(request: ChatRequest):
    """
    Endpoint principal de RAG: mensaje → vectores → respuesta legal citada.
    """

    try:
        result = openai_service.chat_with_rag(
            message=request.message,
            thread_id=request.thread_id
        )

        return ChatResponse(
            response=result["response"],
            thread_id=result["thread_id"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error procesando la consulta: {str(e)}")