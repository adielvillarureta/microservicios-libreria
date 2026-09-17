from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from extensions import db
from models.proveedor import Proveedor

proveedores_bp = Blueprint('proveedores', __name__)

CAMPOS_EDITABLES = {'nombre', 'empresa', 'email', 'contacto', 'direccion', 'activo'}


@proveedores_bp.route('/proveedores')
def listar_proveedores_html():
    return render_template('proveedores.html', proveedores=Proveedor.query.all())


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


@proveedores_bp.route('/proveedores', methods=['GET'])
def api_listar_proveedores():
    return jsonify([p.to_dict() for p in Proveedor.query.all()])


@proveedores_bp.route('/proveedores/<int:id>', methods=['GET'])
def api_obtener_proveedor(id):
    return jsonify(Proveedor.query.get_or_404(id).to_dict())


@proveedores_bp.route('/proveedores', methods=['POST'])
def api_crear_proveedor():
    data = request.get_json(silent=True) or {}
    nuevo = Proveedor(**{k: v for k, v in data.items() if k in CAMPOS_EDITABLES})
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@proveedores_bp.route('/proveedores/<int:id>', methods=['PUT'])
def api_actualizar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    for key, value in data.items():
        if key in CAMPOS_EDITABLES:
            setattr(proveedor, key, value)
    db.session.commit()
    return jsonify(proveedor.to_dict())


@proveedores_bp.route('/proveedores/<int:id>', methods=['DELETE'])
def api_eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({'message': 'Proveedor eliminado'})