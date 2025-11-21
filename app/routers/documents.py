from fastapi import APIRouter, UploadFile, HTTPException
from app.services.openai_handler import openai_service
from app.schemas.chat import UploadResponse

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile):
    """
    Sube un archivo a OpenAI → hace OCR → lo mete al Vector Store → queda listo para consultas.
    """
    if not file:
        raise HTTPException(status_code=400, detail="No se recibió ningún archivo.")

    if not file.filename.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
        raise HTTPException(
            status_code=400,
            detail="Formato no válido. Solo se aceptan PDF o imágenes."
        )

    result = await openai_service.upload_file_to_store(file)

    return UploadResponse(
        filename=result["filename"],
        file_id=result["id"],
        status="indexed"
    )