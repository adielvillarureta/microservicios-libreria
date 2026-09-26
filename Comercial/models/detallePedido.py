from extensions import db


class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedidos'

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), index=True)
    producto_id = db.Column(db.Integer, index=True)
    nombre_producto = db.Column(db.String(200))
    cantidad = db.Column(db.Integer, default=1)
    precio_unitario = db.Column(db.Numeric(10, 2), default=0)
    subtotal = db.Column(db.Numeric(10, 2), default=0)

    pedido = db.relationship('Pedido', back_populates='detalles')
