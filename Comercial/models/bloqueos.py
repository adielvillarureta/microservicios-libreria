from extensions import db
from datetime import datetime


class Bloqueo(db.Model):
    __tablename__ = 'bloqueos'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100))
    ip = db.Column(db.String(45))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    tipo_usuario = db.Column(db.String(20), default='cliente')
    motivo = db.Column(db.String(255))
    permanente = db.Column(db.Integer, default=0)
    estado = db.Column(db.Integer, default=1)
    fecha_bloqueo = db.Column(db.DateTime, default=datetime.now)
    fecha_desbloqueo = db.Column(db.DateTime)
