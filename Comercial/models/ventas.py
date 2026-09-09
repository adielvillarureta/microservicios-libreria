from extensions import db
from datetime import datetime

class Venta(db.Model):
    __tablename__ = 'ventas'
    
    id = db.Column(db.Integer, primary_key=True)
    vendedor_id = db.Column(db.Integer)
    cliente_email = db.Column(db.String(100))
    cliente_nombres = db.Column(db.String(100))
    cliente_apellidos = db.Column(db.String(100))
    cliente_documento = db.Column(db.String(20))
    cliente_razon_social = db.Column(db.String(200))
    cliente_direccion_fiscal = db.Column(db.String(255))
    producto_nombre = db.Column(db.String(200))
    cantidad = db.Column(db.Integer)
    precio_unitario = db.Column(db.Numeric(10, 2))
    total_venta = db.Column(db.Numeric(10, 2))
    tipo_comprobante = db.Column(db.String(20), default='boleta')
    numero_comprobante = db.Column(db.String(50))
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow)