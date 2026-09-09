# Comercial/models/clientes.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Cliente(db.Model):
    __tablename__ = "clientes"
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8))
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.Text)
    clave = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, default=datetime.now)
    puntos = db.Column(db.Integer, default=0)
    token_recuperacion = db.Column(db.String(100), nullable=True)
    token_expiracion = db.Column(db.DateTime, nullable=True)
    estado = db.Column(db.Integer, default=1)
    
    # Relaciones
    pedidos = db.relationship("Pedido", back_populates="cliente", lazy=True)
    ventas = db.relationship("Venta", back_populates="cliente", lazy=True)