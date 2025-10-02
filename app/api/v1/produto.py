from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app import models, schemas
from app.db.session import get_db

router = APIRouter(prefix="/produtos", tags=["produtos"])

@router.post("/", response_model=schemas.ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    novo = models.Produto(**produto.dict())
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo

@router.get("/", response_model=List[schemas.ProdutoOut])
def listar_produtos(db: Session = Depends(get_db)):
    return db.query(models.Produto).all()

@router.get("/abaixo-minimo", response_model=List[schemas.SaldoOut])
def listar_abaixo_minimo(db: Session = Depends(get_db)):
    produtos = db.query(models.Produto).filter(models.Produto.ativo == True).all()
    resultado = []

    for produto in produtos:
        entradas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
            models.EstoqueMovimento.produto_id == produto.id,
            models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
        ).scalar()

        saidas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
            models.EstoqueMovimento.produto_id == produto.id,
            models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
        ).scalar()

        saldo = (entradas or 0) - (saidas or 0)
        if saldo < produto.estoque_minimo:
            resultado.append(schemas.SaldoOut(produto_id=produto.id, saldo=saldo))

    return resultado