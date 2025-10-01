from sqlalchemy import Column, Integer, String, ForeignKey, Enum, DateTime, func, Boolean
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base  # ajuste conforme seu projeto

class MovimentoTipo(str, enum.Enum):
    ENTRADA = "ENTRADA"
    SAIDA = "SAIDA"

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Integer, nullable=True)
    estoque_minimo = Column(Integer, nullable=False, default=0)  # >= 0
    ativo = Column(Boolean, nullable=False, default=True)

    movimentos = relationship("EstoqueMovimento", back_populates="produto")

class EstoqueMovimento(Base):
    __tablename__ = "estoque_movimentos"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id", ondelete="CASCADE"), nullable=False)
    tipo = Column(Enum(MovimentoTipo), nullable=False)
    quantidade = Column(Integer, nullable=False)  # > 0 validated no schema
    motivo = Column(String, nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    produto = relationship("Produto", back_populates="movimentos")