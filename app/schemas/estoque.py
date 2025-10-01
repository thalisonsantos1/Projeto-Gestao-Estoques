from pydantic import BaseModel, Field, conint
from typing import Optional
from datetime import datetime
from enum import Enum

class MovimentoTipo(str, Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class EstoqueMovimentoCreate(BaseModel):
    produto_id: int
    tipo: MovimentoTipo
    quantidade: conint(gt=0)  # quantidade > 0
    motivo: Optional[str] = None

class EstoqueMovimentoOut(BaseModel):
    id: int
    produto_id: int
    tipo: MovimentoTipo
    quantidade: int
    motivo: Optional[str]
    criado_em: datetime

    class Config:
        orm_mode = True

class SaldoOut(BaseModel):
    produto_id: int
    saldo: int