# Comercial/models/detallePedido.py
from flask_sqlalchemy import SQLAlchemy
from app import db

class DetallePedido(db.Model):
    __tablename__ = "detalle_pedido"
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, nullable=False)  # Referencia al inventario
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    
    pedido = db.relationship("Pedido", back_populates="detalles", lazy=True)