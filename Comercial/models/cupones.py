from extensions import db
from datetime import datetime

class Cupon(db.Model):
    __tablename__ = 'cupones'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    tipo = db.Column(db.String(20), default='porcentaje')
    valor = db.Column(db.Float, default=0.0)
    minimo_compra = db.Column(db.Float, default=0.0)
    usos_maximos = db.Column(db.Integer, default=100)
    usos_actuales = db.Column(db.Integer, default=0)
    fecha_expiracion = db.Column(db.DateTime, nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.now)
    
    def to_dict(self):
        return {
            'id': self.id,
            'codigo': self.codigo,
            'tipo': self.tipo,
            'valor': self.valor,
            'minimo_compra': self.minimo_compra,
            'usos_maximos': self.usos_maximos,
            'usos_actuales': self.usos_actuales,
            'fecha_expiracion': self.fecha_expiracion.isoformat() if self.fecha_expiracion else None,
            'activo': self.activo
        }