from extensions import db
from datetime import datetime

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    fecha_pedido = db.Column(db.DateTime, default=datetime.utcnow)
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.String(20), default='pendiente')
    tipo_entrega = db.Column(db.String(20), default='recojo')
    direccion_entrega = db.Column(db.String(255))
    
    cliente = db.relationship('Cliente', back_populates='pedidos')
    detalles = db.relationship('DetallePedido', back_populates='pedido')
    
    def to_dict(self):
        return {
            'id': self.id,
            'cliente_id': self.cliente_id,
            'fecha_pedido': self.fecha_pedido.isoformat() if self.fecha_pedido else None,
            'total': float(self.total) if self.total else 0,
            'estado': self.estado,
            'tipo_entrega': self.tipo_entrega,
            'direccion_entrega': self.direccion_entrega
        }