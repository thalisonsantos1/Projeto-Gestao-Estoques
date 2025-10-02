from fastapi import FastAPI
from app.api.v1 import produto, estoque

app = FastAPI(title="Gestão de Estoques API")

# registrando rotas versão 1
app.include_router(produto.router, prefix="/api/v1")
app.include_router(estoque.router, prefix="/api/v1")