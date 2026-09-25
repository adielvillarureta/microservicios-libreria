from extensions import db


class MovimientoCaja(db.Model):
    __tablename__ = 'movimientos_caja'

    id = db.Column(db.Integer, primary_key=True)
    caja_id = db.Column(db.Integer, db.ForeignKey('cajas.id'), index=True)
    tipo = db.Column(db.String(20))
    monto = db.Column(db.Numeric(10, 2), default=0)
    concepto = db.Column(db.String(200))
    referencia = db.Column(db.String(50))
    creado_en = db.Column(db.DateTime)

    caja = db.relationship('Caja')
