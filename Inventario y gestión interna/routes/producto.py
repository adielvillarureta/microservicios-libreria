import os

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import DataError, IntegrityError, StatementError
from werkzeug.utils import secure_filename

from extensions import db
from models.categoria import Categoria
from models.producto import Producto
from models.proveedor import Proveedor
from services.permisos import login_required, solo_gestion

producto_bp = Blueprint('producto', __name__)

CAMPOS_EDITABLES = {
    'nombre', 'descripcion', 'precio', 'precio_oferta', 'costo', 'cantidad',
    'codigo_barras', 'sku', 'imagen', 'destacado', 'estado',
    'stock_minimo', 'stock_maximo', 'id_categoria', 'proveedor_id'
}


def _guardar_imagen():
    archivo = request.files.get('imagen')
    if not archivo or not archivo.filename:
        return None
    nombre = secure_filename(archivo.filename)
    if not nombre:
        return None
    destino = os.path.join(current_app.root_path, 'static', 'img', 'productos')
    os.makedirs(destino, exist_ok=True)
    archivo.save(os.path.join(destino, nombre))
    return nombre


@producto_bp.route('/productos')
@login_required
def listar_productos_html():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template('productos.html', productos=productos, categorias=categorias)


@producto_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@solo_gestion
def nuevo_producto():
    if request.method == 'POST':
        return guardar_producto()
    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    return render_template('producto_form.html', categorias=categorias, proveedores=proveedores)


@producto_bp.route('/productos/guardar', methods=['POST'])
@solo_gestion
def guardar_producto():
    producto = Producto(
        nombre=request.form['nombre'],
        descripcion=request.form.get('descripcion') or '',
        precio=request.form['precio'],
        cantidad=request.form['cantidad'],
        id_categoria=request.form['id_categoria'],
        proveedor_id=request.form.get('proveedor') or None,
        precio_oferta=request.form.get('precio_oferta') or None,
        codigo_barras=request.form.get('codigo_barras') or None,
        destacado='destacado' in request.form
    )
    imagen = _guardar_imagen()
    if imagen:
        producto.imagen = imagen
    try:
        db.session.add(producto)
        db.session.commit()
    except (DataError, IntegrityError, StatementError):
        db.session.rollback()
        flash('No se pudo guardar el producto: datos invalidos', 'danger')
        return redirect(url_for('producto.listar_productos_html'))
    flash(f'Producto "{producto.nombre}" creado correctamente', 'success')
    return redirect(url_for('producto.listar_productos_html'))


@producto_bp.route('/productos/editar/<int:id>')
@solo_gestion
def editar_producto(id):
    producto = db.get_or_404(Producto, id)
    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    return render_template(
        'producto_form.html',
        producto=producto,
        categorias=categorias,
        proveedores=proveedores
    )


@producto_bp.route('/productos/actualizar/<int:id>', methods=['POST'])
@solo_gestion
def actualizar_producto(id):
    producto = db.get_or_404(Producto, id)
    producto.nombre = request.form['nombre']
    producto.descripcion = request.form.get('descripcion') or ''
    producto.id_categoria = request.form['id_categoria']
    producto.cantidad = request.form['cantidad']
    producto.precio = request.form['precio']
    producto.precio_oferta = request.form.get('precio_oferta') or None
    producto.codigo_barras = request.form.get('codigo_barras') or None
    producto.destacado = 'destacado' in request.form
    producto.proveedor_id = request.form.get('proveedor') or None
    imagen = _guardar_imagen()
    if imagen:
        producto.imagen = imagen
    try:
        db.session.commit()
    except (DataError, IntegrityError, StatementError):
        db.session.rollback()
        flash('No se pudo actualizar el producto: datos invalidos', 'danger')
        return redirect(url_for('producto.listar_productos_html'))
    flash(f'Producto "{producto.nombre}" actualizado correctamente', 'success')
    return redirect(url_for('producto.listar_productos_html'))


@producto_bp.route('/productos/eliminar/<int:id>')
@solo_gestion
def eliminar_producto(id):
    producto = db.get_or_404(Producto, id)
    nombre = producto.nombre
    try:
        db.session.delete(producto)
        db.session.commit()
        flash(f'Producto "{nombre}" eliminado', 'success')
    except IntegrityError:
        db.session.rollback()
        producto.estado = False
        db.session.commit()
        flash(
            f'El producto "{nombre}" tiene movimientos registrados: se desactivó en lugar de eliminarlo',
            'warning'
        )
    return redirect(url_for('producto.listar_productos_html'))


@producto_bp.route('/productos', methods=['GET'])
@producto_bp.route('/api/productos', methods=['GET'])
def api_listar_productos():
    return jsonify([p.to_dict() for p in Producto.query.all()])


@producto_bp.route('/productos/<int:id>', methods=['GET'])
@producto_bp.route('/api/productos/<int:id>', methods=['GET'])
def api_obtener_producto(id):
    return jsonify(db.get_or_404(Producto, id).to_dict())


@producto_bp.route('/productos', methods=['POST'])
@producto_bp.route('/api/productos', methods=['POST'])
def api_crear_producto():
    data = request.get_json(silent=True) or {}
    if not str(data.get('nombre') or '').strip():
        return jsonify({'error': 'El nombre es obligatorio'}), 400
    if not data.get('sku'):
        data.pop('sku', None)
    nuevo = Producto(**{k: v for k, v in data.items() if k in CAMPOS_EDITABLES})
    try:
        db.session.add(nuevo)
        db.session.commit()
    except (DataError, IntegrityError, StatementError):
        db.session.rollback()
        return jsonify({'error': 'Datos invalidos para el producto'}), 400
    return jsonify(nuevo.to_dict()), 201


@producto_bp.route('/productos/<int:id>', methods=['PUT'])
@producto_bp.route('/api/productos/<int:id>', methods=['PUT'])
def api_actualizar_producto(id):
    producto = db.get_or_404(Producto, id)
    data = request.get_json(silent=True) or {}
    if 'nombre' in data and not str(data.get('nombre') or '').strip():
        return jsonify({'error': 'El nombre no puede estar vacio'}), 400
    for key, value in data.items():
        if key in CAMPOS_EDITABLES:
            setattr(producto, key, value)
    try:
        db.session.commit()
    except (DataError, IntegrityError, StatementError):
        db.session.rollback()
        return jsonify({'error': 'Datos invalidos para el producto'}), 400
    return jsonify(producto.to_dict())


@producto_bp.route('/productos/<int:id>', methods=['DELETE'])
@producto_bp.route('/api/productos/<int:id>', methods=['DELETE'])
def api_eliminar_producto(id):
    producto = db.get_or_404(Producto, id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})


@producto_bp.route('/productos/<int:id>/stock', methods=['GET'])
@producto_bp.route('/api/productos/<int:id>/stock', methods=['GET'])
def api_obtener_stock(id):
    producto = db.get_or_404(Producto, id)
    return jsonify({'stock': producto.cantidad, 'nombre': producto.nombre})


@producto_bp.route('/productos/<int:id>/stock', methods=['PUT'])
@producto_bp.route('/api/productos/<int:id>/stock', methods=['PUT'])
def api_actualizar_stock(id):
    producto = db.get_or_404(Producto, id)
    data = request.get_json(silent=True) or {}
    if 'cantidad' in data:
        try:
            cantidad = int(data['cantidad'])
        except (TypeError, ValueError):
            return jsonify({'error': 'cantidad debe ser un numero entero'}), 400
        if cantidad < 0:
            return jsonify({'error': 'cantidad no puede ser negativa'}), 400
        producto.cantidad = cantidad
    try:
        db.session.commit()
    except (DataError, StatementError):
        db.session.rollback()
        return jsonify({'error': 'Datos invalidos'}), 400
    return jsonify({'stock': producto.cantidad})


@producto_bp.route('/api/categorias', methods=['GET'])
def api_listar_categorias():
    return jsonify([c.to_dict() for c in Categoria.query.all()]), 200


@producto_bp.route('/api/productos/catalogo', methods=['GET'])
def api_catalogo_productos():
    q = request.args.get('q', '')
    categoria_id = request.args.get('categoria', type=int)

    query = Producto.query.filter(Producto.cantidad > 0)

    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))
    if categoria_id:
        query = query.filter(Producto.id_categoria == categoria_id)

    return jsonify([p.to_dict() for p in query.all()]), 200