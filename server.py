from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS (permite que un frontend pueda llamar a tu backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend IUSNAUTA funcionando."}

@app.get("/healthz")
def health():
    return {"status": "healthy"}