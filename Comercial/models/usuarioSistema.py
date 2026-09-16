from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class UsuarioSistema(db.Model):
    __tablename__ = 'usuarios_sistema'
    
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    clave = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(30), default='vendedor')
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    def set_password(self, password):
        self.clave = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.clave, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'correo': self.correo,
            'rol': self.rol,
            'activo': self.activo
        }