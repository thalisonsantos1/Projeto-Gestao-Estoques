from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str = 'secret'
    APP_NAME: str = "Gestão de Estoques API"
    ALLOW_NEGATIVE_STOCK: bool = False  # se True, permite saldo negativo

class config:
    env_file = ".env"
    case_sensitive = True

settings = Settings()