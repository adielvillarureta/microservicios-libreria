from extensions import db
from datetime import datetime

class IntentosLogin(db.Model):
    __tablename__ = 'intentos_login'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    ip = db.Column(db.String(50))
    intentos = db.Column(db.Integer, default=0)
    intentos_totales = db.Column(db.Integer, default=0)
    email_bloqueado = db.Column(db.DateTime, nullable=True)
    ip_bloqueado = db.Column(db.DateTime, nullable=True)
    fecha_ultimo_intento = db.Column(db.DateTime, default=datetime.now)

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'intentos': self.intentos,
            'intentos_totales': self.intentos_totales
        }