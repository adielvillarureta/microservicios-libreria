from extensions import db
from datetime import datetime


class ItemCarrito(db.Model):
    __tablename__ = 'carrito_items'

    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, nullable=False, index=True)
    producto_id = db.Column(db.Integer, nullable=False, index=True)
    nombre_producto = db.Column(db.String(200), nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False, default=1)
    imagen = db.Column(db.String(255))
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id_item': self.id,
            'id_producto': self.producto_id,
            'nombre': self.nombre_producto,
            'precio_unitario': float(self.precio_unitario),
            'cantidad': self.cantidad,
            'subtotal': round(float(self.precio_unitario) * self.cantidad, 2),
            'imagen': self.imagen
        }