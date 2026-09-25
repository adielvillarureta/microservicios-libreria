from extensions import db
from datetime import datetime


class Venta(db.Model):
    __tablename__ = 'ventas'

    id = db.Column(db.Integer, primary_key=True)
    fecha_venta = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # --- KPI 9: Tiempo de atencion al cliente ---
    hora_llegada = db.Column(db.DateTime)
    tiempo_atencion_min = db.Column(db.Numeric(8, 2))

    vendedor_id = db.Column(db.Integer, index=True)
    cliente_id = db.Column(db.Integer, index=True)
    cliente_nombres = db.Column(db.String(100))
    cliente_apellidos = db.Column(db.String(100))
    cliente_documento = db.Column(db.String(20))
    cliente_email = db.Column(db.String(150))
    cliente_direccion = db.Column(db.Text)
    cliente_direccion_fiscal = db.Column(db.Text)
    cliente_razon_social = db.Column(db.String(200))

    tipo_comprobante = db.Column(db.String(20), default='boleta')
    numero_comprobante = db.Column(db.String(50))
    metodo_pago = db.Column(db.String(30))
    monto_recibido = db.Column(db.Numeric(10, 2))
    vuelto = db.Column(db.Numeric(10, 2))

    subtotal = db.Column(db.Numeric(10, 2), default=0)
    descuento = db.Column(db.Numeric(10, 2), default=0)
    total_venta = db.Column(db.Numeric(10, 2), default=0)

    pedido_id = db.Column(db.Integer, index=True)
    estado = db.Column(db.Boolean, default=True, index=True)

    detalles = db.relationship('DetalleVenta', back_populates='venta',
                               cascade='all, delete-orphan')

    @property
    def unidades_totales(self):
        return sum(d.cantidad for d in self.detalles)

    @property
    def precio_promedio(self):
        """Precio unitario promedio ponderado de la venta.

        Antes el precio unitario era una columna de ventas. Ahora vive en
        detalle_ventas (una fila por producto), asi que las plantillas que
        muestran "precio unitario" usan este promedio.
        """
        unidades = self.unidades_totales
        if not unidades:
            return 0.0
        return round(float(self.total_venta or 0) / unidades, 2)

    @property
    def precio_unitario(self):
        return self.precio_promedio

    @property
    def nombre_producto_texto(self):
        nombres = [d.nombre_producto for d in self.detalles]
        return ', '.join(nombres) if nombres else 'Sin detalle'

    def to_dict(self):
        return {
            'id': self.id,
            'fecha_venta': self.fecha_venta.isoformat() if self.fecha_venta else None,
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'cliente_nombres': self.cliente_nombres,
            'cliente_apellidos': self.cliente_apellidos,
            'producto_nombre': ', '.join(d.nombre_producto for d in self.detalles[:3]),
            'cantidad': sum(d.cantidad for d in self.detalles),
            'total_venta': float(self.total_venta or 0),
            'tipo_comprobante': self.tipo_comprobante,
            'numero_comprobante': self.numero_comprobante,
            'metodo_pago': self.metodo_pago
        }
