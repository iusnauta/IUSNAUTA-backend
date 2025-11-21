from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IUSNAUTA API"

    OPENAI_API_KEY: str
    OPENAI_VECTOR_STORE_ID: str
    OPENAI_ASSISTANT_ID: str = ""

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()