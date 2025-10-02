from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Gestão de Estoques API"
    ALLOW_NEGATIVE_STOCK: bool = False  # se True, permite saldo negativo

settings = Settings()