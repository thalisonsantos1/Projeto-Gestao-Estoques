from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ProdutoBase(BaseModel):
    nome: str
    descricao: Optional[str] = None
    preco: Optional[int] = None
    estoque_minimo: int = Field(0, ge=0)  # valor mínimo 0
    ativo: bool = True

class ProdutoCreate(ProdutoBase):
    pass

class ProdutoUpdate(ProdutoBase):
    pass

class ProdutoOut(ProdutoBase):
    id: int

    class Config:
        orm_mode = True