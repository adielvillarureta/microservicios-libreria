from extensions import db
from datetime import datetime


class Notificacion(db.Model):
    __tablename__ = 'notificaciones'

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, index=True)
    tipo = db.Column(db.String(40), default='info')
    titulo = db.Column(db.String(150))
    mensaje = db.Column(db.Text)
    leida = db.Column(db.Boolean, default=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
