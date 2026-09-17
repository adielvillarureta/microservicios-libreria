from extensions import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    empresa = db.Column(db.String(150))
    email = db.Column(db.String(100))
    contacto = db.Column(db.String(50))
    direccion = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'empresa': self.empresa,
            'email': self.email,
            'contacto': self.contacto,
            'direccion': self.direccion,
            'activo': self.activo
        }