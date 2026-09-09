# Comercial/models/pedidos.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Pedido(db.Model):
    __tablename__ = "pedidos"
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=False)
    fecha_pedido = db.Column(db.DateTime, default=datetime.now)
    estado = db.Column(db.String(20), default="pendiente")
    total = db.Column(db.Float)
    direccion_entrega = db.Column(db.Text)
    tipo_entrega = db.Column(db.String(20), default="recojo")
    nota = db.Column(db.Text)
    
    cliente = db.relationship("Cliente", back_populates="pedidos", lazy=True)
    detalles = db.relationship("DetallePedido", back_populates="pedido", lazy=True, cascade="all, delete-orphan")