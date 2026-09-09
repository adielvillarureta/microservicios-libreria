from models.usuarioSistema import UsuarioSistema
from werkzeug.security import check_password_hash

class AuthService:
    @staticmethod
    def authenticate(correo, clave):
        usuario = UsuarioSistema.query.filter_by(correo=correo).first()
        if usuario and check_password_hash(usuario.clave, clave):
            return usuario
        return None