from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from extensions import db
from models.proveedor import Proveedor
from services.permisos import login_required, solo_gestion

proveedores_bp = Blueprint('proveedores', __name__)

CAMPOS_EDITABLES = {'nombre', 'empresa', 'email', 'contacto', 'direccion', 'activo'}


@proveedores_bp.route('/proveedores')
@login_required
def listar_proveedores_html():
    return render_template('proveedores.html', proveedores=Proveedor.query.all())


@proveedores_bp.route('/proveedores/nuevo', methods=['GET', 'POST'])
@solo_gestion
def nuevo_proveedor():
    if request.method == 'POST':
        return guardar_proveedor()
    return render_template('proveedor_form.html', proveedor=None)


@proveedores_bp.route('/proveedores/guardar', methods=['POST'])
@solo_gestion
def guardar_proveedor():
    proveedor = Proveedor(
        nombre=request.form['nombre'],
        empresa=request.form['empresa'],
        email=request.form['email'],
        contacto=request.form['contacto']
    )
    db.session.add(proveedor)
    db.session.commit()
    flash(f'Proveedor "{proveedor.nombre}" registrado correctamente', 'success')
    return redirect(url_for('proveedores.listar_proveedores_html'))


@proveedores_bp.route('/proveedores/editar/<int:id>')
@solo_gestion
def editar_proveedor(id):
    proveedor = db.get_or_404(Proveedor, id)
    return render_template('proveedor_form.html', proveedor=proveedor)


@proveedores_bp.route('/proveedores/actualizar/<int:id>', methods=['POST'])
@solo_gestion
def actualizar_proveedor(id):
    proveedor = db.get_or_404(Proveedor, id)
    proveedor.nombre = request.form['nombre']
    proveedor.empresa = request.form['empresa']
    proveedor.email = request.form['email']
    proveedor.contacto = request.form['contacto']
    db.session.commit()
    flash(f'Proveedor "{proveedor.nombre}" actualizado correctamente', 'success')
    return redirect(url_for('proveedores.listar_proveedores_html'))


@proveedores_bp.route('/proveedores/eliminar/<int:id>')
@solo_gestion
def eliminar_proveedor(id):
    proveedor = db.get_or_404(Proveedor, id)
    nombre = proveedor.nombre
    try:
        db.session.delete(proveedor)
        db.session.commit()
        flash(f'Proveedor "{nombre}" eliminado', 'success')
    except IntegrityError:
        db.session.rollback()
        proveedor.activo = False
        db.session.commit()
        flash(
            f'El proveedor "{nombre}" tiene productos asignados: se desactivó en lugar de eliminarlo',
            'warning'
        )
    return redirect(url_for('proveedores.listar_proveedores_html'))


@proveedores_bp.route('/ver_productos_proveedor')
@proveedores_bp.route('/ver_producto_proveedor')
@login_required
def ver_productos_por_proveedor():
    """Catalogo de productos asignado a un proveedor.

    Las unidades vendidas por producto se sacan de movimientos_stock, que es
    el libro de movimientos de inventario. No se consulta comercial_db.
    """
    from models.producto import Producto
    from sqlalchemy import text

    proveedores = Proveedor.query.filter_by(activo=True).all()
    proveedor_id = request.args.get('proveedor_id', type=int)
    proveedor_seleccionado = None
    productos = []

    if proveedor_id:
        proveedor_seleccionado = db.session.get(Proveedor, proveedor_id)
        if proveedor_seleccionado:
            productos = Producto.query.filter_by(proveedor_id=proveedor_id).all()
            vendidos = {
                int(r.producto_id): int(r.n or 0)
                for r in db.session.execute(text("""
                    SELECT producto_id, SUM(cantidad) AS n
                    FROM movimientos_stock
                    WHERE tipo = 'SALIDA'
                    GROUP BY producto_id
                """)).fetchall()
            }
            for p in productos:
                p.total_ventas = vendidos.get(p.id, 0)

    return render_template(
        'ver_producto_proveedor.html',
        proveedores=proveedores,
        proveedor_id=proveedor_id,
        proveedor_seleccionado=proveedor_seleccionado,
        productos=productos
    )


@proveedores_bp.route('/proveedores', methods=['GET'])
@proveedores_bp.route('/api/proveedores', methods=['GET'])
def api_listar_proveedores():
    return jsonify([p.to_dict() for p in Proveedor.query.all()])


@proveedores_bp.route('/proveedores/<int:id>', methods=['GET'])
@proveedores_bp.route('/api/proveedores/<int:id>', methods=['GET'])
def api_obtener_proveedor(id):
    return jsonify(Proveedor.query.get_or_404(id).to_dict())


@proveedores_bp.route('/proveedores', methods=['POST'])
@proveedores_bp.route('/api/proveedores', methods=['POST'])
def api_crear_proveedor():
    data = request.get_json(silent=True) or {}
    nuevo = Proveedor(**{k: v for k, v in data.items() if k in CAMPOS_EDITABLES})
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201


@proveedores_bp.route('/proveedores/<int:id>', methods=['PUT'])
@proveedores_bp.route('/api/proveedores/<int:id>', methods=['PUT'])
def api_actualizar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    data = request.get_json(silent=True) or {}
    for key, value in data.items():
        if key in CAMPOS_EDITABLES:
            setattr(proveedor, key, value)
    db.session.commit()
    return jsonify(proveedor.to_dict())


@proveedores_bp.route('/proveedores/<int:id>', methods=['DELETE'])
@proveedores_bp.route('/api/proveedores/<int:id>', methods=['DELETE'])
def api_eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return jsonify({'message': 'Proveedor eliminado'})