from extensions import db
from datetime import datetime


class Cliente(db.Model):
    __tablename__ = 'clientes'

    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.String(8), unique=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    telefono = db.Column(db.String(15))
    direccion = db.Column(db.Text)
    clave = db.Column(db.String(255), nullable=False)

    # Fuente del KPI 8: Crecimiento de la base de clientes
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    estado = db.Column(db.Boolean, default=True)
    puntos = db.Column(db.Integer, default=0)

    token_recuperacion = db.Column(db.String(100))
    token_expiracion = db.Column(db.DateTime)

    pedidos = db.relationship('Pedido', back_populates='cliente')

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}".strip()

    # La columna en la base de datos se llama `correo`, pero historicamente el
    # codigo y las plantillas usan `email`. Este alias evita romper los dos.
    @property
    def email(self):
        return self.correo

    @email.setter
    def email(self, valor):
        self.correo = valor

    def to_dict(self):
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'email': self.correo,
            'telefono': self.telefono,
            'dni': self.dni,
            'direccion': self.direccion,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }
