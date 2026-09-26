from datetime import datetime, timedelta

from extensions import db

INTENTOS_MAX = 3
MINUTOS_BLOQUEO = 10


class Bloqueo(db.Model):
    """Bloqueo de IP por intentos fallidos de login."""

    __tablename__ = 'bloqueos_ip'

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), unique=True, nullable=False, index=True)
    intentos = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=False)
    motivo = db.Column(db.String(200), default='Intentos de login fallidos')
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    expira_en = db.Column(db.DateTime, nullable=True)

    @classmethod
    def refrescar_expirados(cls):
        ahora = datetime.utcnow()
        expirados = cls.query.filter(
            cls.activo.is_(True),
            cls.expira_en.isnot(None),
            cls.expira_en <= ahora
        ).all()
        for bloqueo in expirados:
            bloqueo.activo = False
            bloqueo.expira_en = None
            bloqueo.intentos = 0
        if expirados:
            db.session.commit()

    @classmethod
    def ip_bloqueada(cls, ip):
        cls.refrescar_expirados()
        return cls.query.filter_by(ip=ip, activo=True).first() is not None

    @classmethod
    def registrar_fallo(cls, ip):
        bloqueo = cls.query.filter_by(ip=ip).first()
        if bloqueo is None:
            bloqueo = Bloqueo(ip=ip, intentos=1)
            db.session.add(bloqueo)
        else:
            bloqueo.intentos = (bloqueo.intentos or 0) + 1
            bloqueo.activo = False
            bloqueo.expira_en = None
        if bloqueo.intentos >= INTENTOS_MAX:
            bloqueo.activo = True
            bloqueo.motivo = f'{bloqueo.intentos} intentos de login fallidos'
            bloqueo.expira_en = datetime.utcnow() + timedelta(minutes=MINUTOS_BLOQUEO)
        db.session.commit()
        return bloqueo

    @classmethod
    def liberar(cls, ip):
        bloqueo = cls.query.filter_by(ip=ip).first()
        if bloqueo:
            db.session.delete(bloqueo)
            db.session.commit()

    def expirado(self):
        if not self.activo:
            return True
        if self.expira_en and datetime.utcnow() > self.expira_en:
            return True
        return False

    def to_dict(self):
        return {
            'id': self.id,
            'ip': self.ip,
            'intentos': self.intentos,
            'activo': self.activo,
            'motivo': self.motivo,
            'creado_en': self.creado_en.isoformat() if self.creado_en else None,
            'expira_en': self.expira_en.isoformat() if self.expira_en else None,
        }
