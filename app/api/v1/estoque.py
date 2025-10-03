from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app import models
from app.db.deps import get_db
from app.schemas.estoque import SaldoOut, EstoqueMovimentoCreate, EstoqueMovimentoOut

router = APIRouter(prefix="/estoque", tags=["estoque"])

# ----------------------------
# Etapa 1 e 2: Criar movimento
# ----------------------------
@router.post("/movimentos", response_model=EstoqueMovimentoOut)
def criar_movimento(movimento: EstoqueMovimentoCreate, db: Session = Depends(get_db)):
    # Verifica se o produto existe
    produto = db.query(models.Produto).filter(models.Produto.id == movimento.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    # Busca o saldo atual do produto
    saldo_atual = db.query(func.sum(models.Movimento.quantidade)).filter(
        models.Movimento.produto_id == movimento.produto_id
    ).scalar() or 0

    # Se for saída, checa se há estoque suficiente
    if movimento.tipo == "saida" and saldo_atual < movimento.quantidade:
        raise HTTPException(status_code=400, detail="Estoque insuficiente")

    # Cria o movimento
    novo_movimento = models.Movimento(
        produto_id=movimento.produto_id,
        quantidade=movimento.quantidade if movimento.tipo == "entrada" else -movimento.quantidade,
        tipo=movimento.tipo
    )
    db.add(novo_movimento)
    db.commit()
    db.refresh(novo_movimento)

    return novo_movimento

# ----------------------------
# Etapa 3: Listar todos os movimentos
# ----------------------------
@router.get("/movimentos", response_model=List[EstoqueMovimentoOut])
def listar_movimentos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    movimentos = db.query(models.Movimento).offset(skip).limit(limit).all()
    return movimentos

# ----------------------------
# Etapa 4: Consultar saldo por produto
# ----------------------------
@router.get("/saldo/{produto_id}", response_model=SaldoOut)
def consultar_saldo(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    saldo = db.query(func.sum(models.Movimento.quantidade)).filter(
        models.Movimento.produto_id == produto_id
    ).scalar() or 0

    return {"produto_id": produto_id, "saldo": saldo}