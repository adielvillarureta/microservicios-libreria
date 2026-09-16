from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from extensions import db
from models.producto import Producto
from models.categoria import Categoria
from models.proveedor import Proveedor

producto_bp = Blueprint('producto', __name__)

# ============== RUTAS PARA LA VISTA (HTML) ==============
@producto_bp.route('/productos')
def listar_productos_html():
    productos = Producto.query.all()
    categorias = Categoria.query.all()
    return render_template('productos.html', productos=productos, categorias=categorias)

@producto_bp.route('/productos/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    if request.method == 'POST':
        producto = Producto(
            nombre=request.form['nombre'],
            descripcion=request.form['descripcion'],
            precio=request.form['precio'],
            cantidad=request.form['cantidad'],
            id_categoria=request.form['id_categoria'],
            proveedor_id=request.form['proveedor']
        )
        db.session.add(producto)
        db.session.commit()
        return redirect(url_for('producto.listar_productos_html'))
    
    categorias = Categoria.query.all()
    proveedores = Proveedor.query.all()
    return render_template('producto_form.html', categorias=categorias, proveedores=proveedores)

# ============== RUTAS PARA API (JSON) ==============
@producto_bp.route('/productos', methods=['GET'])
def api_listar_productos():
    productos = Producto.query.all()
    return jsonify([p.to_dict() for p in productos])

@producto_bp.route('/productos/<int:id>', methods=['GET'])
def api_obtener_producto(id):
    producto = Producto.query.get_or_404(id)
    return jsonify(producto.to_dict())

@producto_bp.route('/productos', methods=['POST'])
def api_crear_producto():
    data = request.get_json()
    nuevo = Producto(**data)
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201

@producto_bp.route('/productos/<int:id>', methods=['PUT'])
def api_actualizar_producto(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    for key, value in data.items():
        setattr(producto, key, value)
    db.session.commit()
    return jsonify(producto.to_dict())

@producto_bp.route('/productos/<int:id>', methods=['DELETE'])
def api_eliminar_producto(id):
    producto = Producto.query.get_or_404(id)
    db.session.delete(producto)
    db.session.commit()
    return jsonify({'message': 'Producto eliminado'})

# ============== API DE STOCK ==============
@producto_bp.route('/productos/<int:id>/stock', methods=['GET'])
def api_obtener_stock(id):
    producto = Producto.query.get_or_404(id)
    return jsonify({'stock': producto.cantidad, 'nombre': producto.nombre})

@producto_bp.route('/productos/<int:id>/stock', methods=['PUT'])
def api_actualizar_stock(id):
    producto = Producto.query.get_or_404(id)
    data = request.get_json()
    producto.cantidad = data.get('cantidad', producto.cantidad)
    db.session.commit()
    return jsonify({'stock': producto.cantidad})
@producto_bp.route('/api/productos/catalogo', methods=['GET'])
def api_catalogo_productos():
    """Endpoint para que Comercial consulte productos disponibles"""
    q = request.args.get('q', '')
    categoria_id = request.args.get('categoria', type=int)
    
    query = Producto.query.filter(Producto.cantidad > 0)
    
    if q:
        query = query.filter(Producto.nombre.ilike(f'%{q}%'))
    if categoria_id:
        query = query.filter(Producto.id_categoria == categoria_id)
    
    productos = query.all()
    return jsonify([p.to_dict() for p in productos]), 200