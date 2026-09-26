from extensions import db
from datetime import datetime


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    sku = db.Column(db.String(50), unique=True)
    codigo_barras = db.Column(db.String(50), unique=True)

    precio = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    precio_oferta = db.Column(db.Numeric(10, 2))
    # costo -> fuente del KPI 3 (margen de ganancia real) junto a comercial_db
    costo = db.Column(db.Numeric(10, 2), nullable=False, default=0)

    cantidad = db.Column(db.Integer, default=0, index=True)
    stock_minimo = db.Column(db.Integer, default=5)
    stock_maximo = db.Column(db.Integer, default=200)

    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'), index=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))

    imagen = db.Column(db.String(255))
    destacado = db.Column(db.Boolean, default=False)
    estado = db.Column(db.Boolean, default=True, index=True)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    categoria = db.relationship('Categoria')
    proveedor = db.relationship('Proveedor')

    @property
    def agotado(self):
        return (self.cantidad or 0) == 0

    @property
    def stock_bajo(self):
        return 0 < (self.cantidad or 0) <= (self.stock_minimo or 5)

    @property
    def margen_unitario(self):
        return round(float(self.precio or 0) - float(self.costo or 0), 2)

    @property
    def margen_porcentaje(self):
        p = float(self.precio or 0)
        return round((p - float(self.costo or 0)) / p * 100, 2) if p else 0.0

    @property
    def precio_efectivo(self):
        """Precio con oferta aplicada, si la hay."""
        return float(self.precio_oferta) if self.precio_oferta else float(self.precio or 0)

    @property
    def tiene_oferta(self):
        return bool(self.precio_oferta) and float(self.precio_oferta) < float(self.precio or 0)

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'sku': self.sku,
            'precio': float(self.precio),
            'costo': float(self.costo or 0),
            'margen_porcentaje': self.margen_porcentaje,
            'precio_oferta': float(self.precio_oferta) if self.precio_oferta else None,
            'cantidad': self.cantidad,
            'stock_minimo': self.stock_minimo,
            'codigo_barras': self.codigo_barras,
            'imagen': self.imagen,
            'imagen_url': ('/static/img/productos/' + self.imagen) if self.imagen else None,
            'destacado': self.destacado,
            'estado': self.estado,
            'id_categoria': self.id_categoria,
            'proveedor_id': self.proveedor_id
        }
