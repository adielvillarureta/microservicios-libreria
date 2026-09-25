from extensions import db


class DetalleVenta(db.Model):
    """Detalle de venta con snapshot de precio y costo.
    Es la fuente de los KPIs 3 (margen real) y 6 (rotacion de inventario).
    """
    __tablename__ = 'detalle_ventas'

    id = db.Column(db.Integer, primary_key=True)
    venta_id = db.Column(db.Integer, db.ForeignKey('ventas.id'), index=True)
    producto_id = db.Column(db.Integer, index=True)
    nombre_producto = db.Column(db.String(200))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), default=0)
    costo_unitario = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), default=0)
    costo_total = db.Column(db.Numeric(10, 2), default=0)

    venta = db.relationship('Venta', back_populates='detalles')
