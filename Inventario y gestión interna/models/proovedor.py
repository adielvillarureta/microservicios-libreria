from app import db

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(200), nullable=False)
    empresa = db.Column(db.String(200))
    email = db.Column(db.String(100))
    contacto = db.Column(db.String(50))
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='proveedor')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'empresa': self.empresa,
            'email': self.email,
            'contacto': self.contacto
        }