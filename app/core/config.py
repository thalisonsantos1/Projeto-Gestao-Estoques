from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME:str = "API Loja"
    DATABASE_URL:str = "sqlite:///./banco_de_dados.db" 

# objeto settings da classe Settings
settings = Settings() 
