from extensions import db
from datetime import datetime


class Caja(db.Model):
    """Modulo de caja - Fuente del KPI 7 (precision en el cierre de caja)."""
    __tablename__ = 'cajas'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, index=True)
    fecha_apertura = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    fecha_cierre = db.Column(db.DateTime)
    monto_inicial = db.Column(db.Numeric(10, 2), default=0)
    monto_esperado = db.Column(db.Numeric(10, 2))
    monto_real = db.Column(db.Numeric(10, 2))
    diferencia = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.String(20), default='abierta', index=True)
    observaciones = db.Column(db.String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'fecha_apertura': self.fecha_apertura.isoformat() if self.fecha_apertura else None,
            'fecha_cierre': self.fecha_cierre.isoformat() if self.fecha_cierre else None,
            'monto_inicial': float(self.monto_inicial or 0),
            'monto_esperado': float(self.monto_esperado or 0) if self.monto_esperado else None,
            'monto_real': float(self.monto_real or 0) if self.monto_real else None,
            'diferencia': float(self.diferencia or 0) if self.diferencia is not None else None,
            'estado': self.estado
        }
