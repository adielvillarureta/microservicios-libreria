from extensions import db


class Producto(db.Model):
    __tablename__ = 'productos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    precio_oferta = db.Column(db.Numeric(10, 2))
    cantidad = db.Column(db.Integer, default=0)
    codigo_barras = db.Column(db.String(50), unique=True)
    imagen = db.Column(db.String(255))
    destacado = db.Column(db.Boolean, default=False)

    id_categoria = db.Column(db.Integer, db.ForeignKey('categorias.id_categoria'))
    categoria = db.relationship('Categoria')

    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    proveedor = db.relationship('Proveedor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': float(self.precio),
            'precio_oferta': float(self.precio_oferta) if self.precio_oferta else None,
            'cantidad': self.cantidad,
            'codigo_barras': self.codigo_barras,
            'imagen': self.imagen,
            'imagen_url': ('/static/img/productos/' + self.imagen) if self.imagen else None,
            'destacado': self.destacado,
            'id_categoria': self.id_categoria,
            'proveedor_id': self.proveedor_id
        }