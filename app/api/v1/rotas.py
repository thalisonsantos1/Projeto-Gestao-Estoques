from fastapi import APIRouter
from app.api.v1 import produto, categoria

api_rotas = APIRouter()
api_rotas.include_router(produto.rotas)
api_rotas.include_router(categoria.rotas)