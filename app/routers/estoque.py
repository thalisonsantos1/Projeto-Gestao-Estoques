from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.db.session import get_db  # ajuste ao seu projeto

router = APIRouter(prefix="/api/v1/estoque", tags=["estoque"])

@router.post("/movimentos", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def criar_movimento(mov: schemas.EstoqueMovimentoCreate, db: Session = Depends(get_db)):
    # validar produto existe e ativo
    produto = db.query(models.Produto).filter(models.Produto.id == mov.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not produto.ativo:
        raise HTTPException(status_code=400, detail="Produto inativo")

    # criar movimento
    mv = models.EstoqueMovimento(
        produto_id=mov.produto_id,
        tipo=mov.tipo,
        quantidade=mov.quantidade,
        motivo=mov.motivo
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv

@router.get("/saldo/{produto_id}", response_model=schemas.SaldoOut)
def obter_saldo(produto_id: int, db: Session = Depends(get_db)):
    # validar produto existe
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    entradas = db.query(models.EstoqueMovimento).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
    ).with_entities(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).scalar()

    saidas = db.query(models.EstoqueMovimento).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
    ).with_entities(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).scalar()

    saldo = (entradas or 0) - (saidas or 0)
    return schemas.SaldoOut(produto_id=produto_id, saldo=saldo)