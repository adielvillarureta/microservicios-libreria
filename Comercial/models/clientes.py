from extensions import db


class Cliente(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    telefono = db.Column(db.String(20))
    dni = db.Column(db.String(8), unique=True)
    direccion = db.Column(db.String(255))
    clave = db.Column(db.String(255), nullable=False)
    
    pedidos = db.relationship('Pedido', back_populates='cliente')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombres': self.nombres,
            'apellidos': self.apellidos,
            'email': self.email,
            'telefono': self.telefono,
            'dni': self.dni,
            'direccion': self.direccion
        }