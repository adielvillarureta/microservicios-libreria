from extensions import db
from datetime import datetime


class MovimientoStock(db.Model):
    """Historial de entradas y salidas de stock.
    Alimenta el KPI 6 (rotacion de inventario) con unidades vendidas.
    """
    __tablename__ = 'movimientos_stock'

    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), index=True)
    tipo = db.Column(db.String(20), index=True)
    cantidad = db.Column(db.Integer, default=0)
    stock_anterior = db.Column(db.Integer, default=0)
    stock_resultante = db.Column(db.Integer, default=0)
    costo_unitario = db.Column(db.Numeric(10, 2), default=0)
    motivo = db.Column(db.String(200))
    referencia = db.Column(db.String(50))
    usuario_id = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    producto = db.relationship('Producto')
