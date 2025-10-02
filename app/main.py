from fastapi import FastAPI
from app.routers import produto, estoque

app = FastAPI(title="Gestão de Estoques API")

app.include_router(produto.router)
app.include_router(estoque.router)