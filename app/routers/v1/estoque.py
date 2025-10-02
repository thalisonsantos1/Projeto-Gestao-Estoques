from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from app.db.session import get_db
from app.core.config import settings

router = APIRouter(prefix="/estoque", tags=["estoque"])

# rotas básicas (Etapa 1 e 2)

@router.post("/movimentos", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def criar_movimento(mov: schemas.EstoqueMovimentoCreate, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).filter(models.Produto.id == mov.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not produto.ativo:
        raise HTTPException(status_code=400, detail="Produto inativo")

    entradas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == mov.produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
    ).scalar()

    saidas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == mov.produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
    ).scalar()

    saldo_atual = (entradas or 0) - (saidas or 0)

    if mov.tipo == models.MovimentoTipo.SAIDA:
        if not settings.ALLOW_NEGATIVE_STOCK and mov.quantidade > saldo_atual:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para saída")

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
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    entradas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
    ).scalar()

    saidas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
    ).scalar()

    saldo = (entradas or 0) - (saidas or 0)
    return schemas.SaldoOut(produto_id=produto_id, saldo=saldo)

@router.post("/venda", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def registrar_venda(produto_id: int, quantidade: int, db: Session = Depends(get_db)):
    """Registra uma saída de estoque por venda"""
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not produto.ativo:
        raise HTTPException(status_code=400, detail="Produto inativo")

    # calcula saldo atual
    entradas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
    ).scalar()

    saidas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
        models.EstoqueMovimento.produto_id == produto_id,
        models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
    ).scalar()

    saldo = (entradas or 0) - (saidas or 0)
    if not settings.ALLOW_NEGATIVE_STOCK and quantidade > saldo:
        raise HTTPException(status_code=400, detail="Saldo insuficiente para venda")

    mv = models.EstoqueMovimento(
        produto_id=produto_id,
        tipo=models.MovimentoTipo.SAIDA,
        quantidade=quantidade,
        motivo="venda"
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


@router.post("/devolucao", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def registrar_devolucao(produto_id: int, quantidade: int, db: Session = Depends(get_db)):
    """Registra uma entrada de estoque por devolução"""
    produto = db.query(models.Produto).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not produto.ativo:
        raise HTTPException(status_code=400, detail="Produto inativo")

    mv = models.EstoqueMovimento(
        produto_id=produto_id,
        tipo=models.MovimentoTipo.ENTRADA,
        quantidade=quantidade,
        motivo="devolucao"
    )
    db.add(mv)
    db.commit()
    db.refresh(mv)
    return mv


@router.post("/ajuste", response_model=schemas.EstoqueMovimentoOut, status_code=status.HTTP_201_CREATED)
def registrar_ajuste(mov: schemas.EstoqueMovimentoCreate, db: Session = Depends(get_db)):
    """Registra um ajuste de estoque (entrada ou saída, motivo obrigatório)"""
    produto = db.query(models.Produto).filter(models.Produto.id == mov.produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    if not produto.ativo:
        raise HTTPException(status_code=400, detail="Produto inativo")

    if not mov.motivo:
        raise HTTPException(status_code=400, detail="Motivo é obrigatório para ajuste")

    # checar saldo em caso de saída
    if mov.tipo == models.MovimentoTipo.SAIDA:
        entradas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
            models.EstoqueMovimento.produto_id == mov.produto_id,
            models.EstoqueMovimento.tipo == models.MovimentoTipo.ENTRADA
        ).scalar()

        saidas = db.query(func.coalesce(func.sum(models.EstoqueMovimento.quantidade), 0)).filter(
            models.EstoqueMovimento.produto_id == mov.produto_id,
            models.EstoqueMovimento.tipo == models.MovimentoTipo.SAIDA
        ).scalar()

        saldo = (entradas or 0) - (saidas or 0)
        if not settings.ALLOW_NEGATIVE_STOCK and mov.quantidade > saldo:
            raise HTTPException(status_code=400, detail="Saldo insuficiente para ajuste")

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