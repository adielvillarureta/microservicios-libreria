# Comercial/models/ventas.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class Venta(db.Model):
    __tablename__ = "ventas"
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, nullable=False)  
    vendedor_id = db.Column(db.Integer, nullable=False)  
    fecha_venta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    cantidad = db.Column(db.Integer, default=1)
    tipo_comprobante = db.Column(db.String(20), default="boleta")
    numero_comprobante = db.Column(db.String(50), nullable=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey("clientes.id"), nullable=True)
    estado = db.Column(db.Integer, default=1)
       
    cliente_nombres = db.Column(db.String(100), nullable=True)
    cliente_apellidos = db.Column(db.String(100), nullable=True)
    cliente_documento = db.Column(db.String(20), nullable=True)
    cliente_email = db.Column(db.String(150), nullable=True)
    cliente_direccion = db.Column(db.Text, nullable=True)
    cliente_direccion_fiscal = db.Column(db.Text, nullable=True)
    cliente_razon_social = db.Column(db.String(200), nullable=True)
    cliente = db.relationship("Cliente", back_populates="ventas", lazy=True)
        @property
    def cliente_nombre_completo(self):
        if self.cliente_nombres and self.cliente_apellidos:
            return f"{self.cliente_nombres} {self.cliente_apellidos}"
        return self.cliente_nombres or ""