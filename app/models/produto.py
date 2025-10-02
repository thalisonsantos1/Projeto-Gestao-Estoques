from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Integer, nullable=True)

    # novos campos
    estoque_minimo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False, default=True)

    movimentos = relationship("EstoqueMovimento", back_populates="produto")