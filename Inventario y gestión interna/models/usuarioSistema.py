from app import db
from flask_login import UserMixin

class UsuarioSistema(db.Model, UserMixin):
    __tablename__ = 'usuarios_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), default='vendedor')
    activo = db.Column(db.Boolean, default=True)
    
    def get_id(self):
        return str(self.id)