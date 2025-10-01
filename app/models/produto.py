from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.base import Base

class Produto(Base):
    __tablename__ = "produtos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    descricao = Column(String, nullable=True)
    preco = Column(Float, nullable=True)
    estoque_minimo = Column(Integer, nullable=False, default=0)
    ativo = Column(Boolean, nullable=False, default=True)
    categoria_id = Column(
        Integer, 
        ForeignKey("categorias.id", ondelete="CASCADE"),
        nullable=False
    )
    categoria = relationship("Categoria", back_populates="produtos")
