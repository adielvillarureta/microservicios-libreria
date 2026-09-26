from extensions import db


class InventarioDiario(db.Model):
    """Foto diaria del stock. Alimenta el KPI 5 (ventas perdidas por
    falta de stock) con historico de productos agotados."""
    __tablename__ = 'inventario_diario'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, index=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'))
    stock = db.Column(db.Integer, default=0)
    agotado = db.Column(db.Boolean, default=False)
