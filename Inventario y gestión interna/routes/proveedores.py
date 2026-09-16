from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from app import db
from models.proveedor import Proveedor
from models.producto import Producto

proveedores_bp = Blueprint('proveedores', __name__)

# ============== RUTAS PARA LA VISTA (HTML) ==============
@proveedores_bp.route('/proveedores')
def listar_proveedores_html():
    proveedores = Proveedor.query.all()
    return render_template('proveedores.html', proveedores=proveedores)

@proveedores_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    if request.method == 'POST':
        proveedor = Proveedor(
            nombre=request.form['nombre'],
            empresa=request.form['empresa'],
            email=request.form['email'],
            contacto=request.form['contacto']
        )
        db.session.add(proveedor)
        db.session.commit()
        return redirect(url_for('proveedores.listar_proveedores_html'))
    return render_template('proveedor_form.html')

# ============== RUTAS PARA API (JSON) ==============
@proveedores_bp.route('/proveedores', methods=['GET'])
def api_listar_proveedores():
    proveedores = Proveedor.query.all()
    return jsonify([p.to_dict() for p in proveedores])

@proveedores_bp.route('/proveedores/<int:id>', methods=['GET'])
def api_obtener_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    return jsonify(proveedor.to_dict())

@proveedores_bp.route('/proveedores', methods=['POST'])
def api_crear_proveedor():
    data = request.get_json()
    nuevo = Proveedor(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201

@proveedores_bp.route('/proveedores/<int:id>', methods=['PUT'])

def api_actualizar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(proveedor, key, value)
    db.session.commit()
    return jsonify(proveedor.to_dict())

@proveedores_bp.route('/proveedores/<int:id>', methods=['DELETE'])
def api_eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({'message': 'Proveedor eliminado'})