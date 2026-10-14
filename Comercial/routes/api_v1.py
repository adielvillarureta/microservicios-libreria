import os
from urllib.parse import urlsplit

import jwt
import requests
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request

from extensions import db, bcrypt
from models.clientes import Cliente
from models.carrito import ItemCarrito

api_v1_bp = Blueprint('api_v1_bp', __name__)

INVENTARIO_URL = os.getenv('INVENTARIO_API_URL') or os.getenv('INVENTARIO_URL') or 'http://localhost:5000'


def _secret_key():
    return os.getenv('SECRET_KEY') or os.getenv('JWT_SECRET_KEY') or 'clave_secreta'


def _validar_token(authorization_header=None):
    header = authorization_header or request.headers.get('Authorization', '')
    if not header.startswith('Bearer '):
        return None, 'Falta el token de autenticación'
    token = header[7:].strip()
    if not token:
        return None, 'Token vacío'
    try:
        payload = jwt.decode(token, _secret_key(), algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, 'El token ha expirado'
    except jwt.InvalidTokenError:
        return None, 'Token inválido'
    cliente_id = payload.get('sub') or payload.get('id_usuario')
    cliente = Cliente.query.get(cliente_id) if cliente_id else None
    if not cliente:
        return None, 'Cliente no encontrado'
    return cliente, None


def _catalogo_inventario():
    try:
        response = requests.get(f"{INVENTARIO_URL}/api/productos", timeout=10)
        if response.status_code != 200:
            return []
        return response.json() or []
    except Exception:
        return []


def _categorias_inventario():
    try:
        response = requests.get(f"{INVENTARIO_URL}/api/categorias", timeout=10)
        if response.status_code != 200:
            return {}
        data = response.json() or []
        return {c.get('id_categoria'): c.get('nombre', '') for c in data}
    except Exception:
        return {}


def _map_producto(producto, categorias=None):
    cantidad = int(producto.get('cantidad') or 0)
    precio = float(producto.get('precio') or 0)
    imagen = producto.get('imagen_url') or producto.get('imagen')
    if imagen and not isinstance(imagen, str):
        imagen = None
    if imagen and not isinstance(imagen, str):
        imagen = None
    if imagen:
        parsed = urlsplit(str(imagen))
        ruta_relativa = parsed.path if parsed.scheme else str(imagen)
        if not ruta_relativa.startswith('/'):
            ruta_relativa = '/' + ruta_relativa
        imagen = '/img/inventario/' + ruta_relativa.lstrip('/')
    return {
        'id_producto': producto.get('id'),
        'titulo': producto.get('nombre', ''),
        'descripcion': producto.get('descripcion') or '',
        'sku': producto.get('sku'),
        'precio': precio,
        'stock': cantidad,
        'estado_stock': 'En stock' if cantidad > 0 else 'Agotado',
        'categoria': (categorias or {}).get(producto.get('id_categoria')) if 'id_categoria' in producto else None,
        'id_categoria': producto.get('id_categoria'),
        'imagen_url': imagen,
        'destacado': producto.get('destacado', False)
    }


def _map_filtrado(producto, categorias=None):
    mapped = _map_producto(producto, categorias)
    # Compatibilidad con el ejemplo de especificación.
    return {
        'id_producto': mapped['id_producto'],
        'titulo': mapped['titulo'],
        'precio': mapped['precio'],
        'stock': mapped['stock'],
        'descripcion': mapped['descripcion'],
        'estado_stock': mapped['estado_stock'],
        'categoria': mapped['categoria'],
        'imagen_url': mapped['imagen_url']
    }


@api_v1_bp.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json(silent=True) or {}
    correo = (data.get('correo') or '').strip().lower()
    contrasena = data.get('contrasena') or ''

    if not correo or not contrasena:
        return jsonify({'status': False, 'mensaje': 'Correo y contraseña son obligatorios'}), 400

    cliente = Cliente.query.filter_by(correo=correo).first()
    if not cliente or not bcrypt.check_password_hash(cliente.clave, contrasena):
        return jsonify({'status': False, 'mensaje': 'Credenciales inválidas'}), 401

    payload = {
        'sub': cliente.id,
        'email': cliente.correo,
        'role': 'Cliente',
        'exp': datetime.utcnow() + timedelta(hours=8),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, _secret_key(), algorithm='HS256')

    return jsonify({
        'status': True,
        'token': token,
        'usuario': {
            'id_usuario': cliente.id,
            'nombre': cliente.nombre_completo,
            'rol': 'Cliente',
            'email': cliente.correo,
            'telefono': cliente.telefono
        }
    }), 200


@api_v1_bp.route('/auth/register', methods=['POST'])
def auth_register():
    data = request.get_json(silent=True) or {}
    nombre_completo = (data.get('nombre_completo') or '').strip()
    correo = (data.get('correo') or '').strip().lower()
    contrasena = data.get('contrasena') or ''
    telefono = (data.get('telefono') or '').strip() or None

    if not nombre_completo:
        return jsonify({'status': False, 'mensaje': 'El nombre completo es obligatorio'}), 400
    if not correo or '@' not in correo:
        return jsonify({'status': False, 'mensaje': 'Correo inválido'}), 400
    if len(contrasena) < 6:
        return jsonify({'status': False, 'mensaje': 'La contraseña debe tener al menos 6 caracteres'}), 400

    partes = nombre_completo.split()
    nombres = partes[0]
    apellidos = ' '.join(partes[1:]) if len(partes) > 1 else ''

    existente = Cliente.query.filter_by(correo=correo).first()
    if existente or Cliente.query.filter(Cliente.correo.ilike(correo)).first():
        return jsonify({'status': False, 'mensaje': 'El correo ya está registrado'}), 409

    cliente = Cliente(
        nombres=nombres,
        apellidos=apellidos,
        email=correo,
        telefono=telefono,
        clave=bcrypt.generate_password_hash(contrasena).decode('utf-8')
    )
    try:
        db.session.add(cliente)
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'status': False, 'mensaje': 'No se pudo registrar el usuario'}), 400

    return jsonify({
        'status': True,
        'mensaje': 'Usuario registrado exitosamente',
        'id_usuario': cliente.id
    }), 201


@api_v1_bp.route('/productos', methods=['GET'])
def productos_listar():
    try:
        limite = request.args.get('limite', type=int, default=20)
        pagina = request.args.get('pagina', type=int, default=1)
    except Exception:
        limite, pagina = 20, 1

    if limite <= 0:
        limite = 20
    if pagina <= 0:
        pagina = 1

    productos = _catalogo_inventario()
    categorias = _categorias_inventario()
    mapped = [_map_producto(p, categorias) for p in productos]

    total = len(mapped)
    inicio = (pagina - 1) * limite
    fin = inicio + limite
    pagina_productos = mapped[inicio:fin]

    return jsonify({
        'total_registros': total,
        'pagina': pagina,
        'limite': limite,
        'total_paginas': (total + limite - 1) // limite if total else 0,
        'productos': pagina_productos
    }), 200


@api_v1_bp.route('/productos/filtrar', methods=['POST'])
def productos_filtrar():
    data = request.get_json(silent=True) or {}
    termino = (data.get('termino_busqueda') or '').strip().lower()
    categoria = (data.get('categoria') or '').strip()
    precio_min = data.get('precio_minimo')
    precio_max = data.get('precio_maximo')
    disponibilidad = (data.get('disponibilidad') or '').strip().lower()
    ordenar_por = (data.get('ordenar_por') or '').strip().lower()

    productos = _catalogo_inventario()
    categorias = _categorias_inventario()
    # Map category name -> id
    categoria_id = None
    if categoria:
        if str(categoria).isdigit():
            categoria_id = int(categoria)
        else:
            for cid, name in categorias.items():
                if (name or '').lower() == str(categoria).lower():
                    categoria_id = cid
                    break

    filtrados = []
    for producto in productos:
        nombre = (producto.get('nombre') or '').lower()
        descripcion = (producto.get('descripcion') or '').lower()
        cantidad = int(producto.get('cantidad') or 0)
        precio = float(producto.get('precio') or 0)

        if termino and termino not in nombre and termino not in descripcion:
            continue
        if categoria_id is not None and producto.get('id_categoria') != categoria_id:
            continue
        if precio_min is not None:
            try:
                if precio < float(precio_min):
                    continue
            except (TypeError, ValueError):
                pass
        if precio_max is not None:
            try:
                if precio > float(precio_max):
                    continue
            except (TypeError, ValueError):
                pass
        if disponibilidad == 'en_stock' and cantidad <= 0:
            continue
        if disponibilidad in ('agotado', 'sin_stock', 'sin stock') and cantidad > 0:
            continue

        filtrados.append(producto)

    if ordenar_por == 'precio_asc':
        filtrados.sort(key=lambda p: float(p.get('precio') or 0))
    elif ordenar_por == 'precio_desc':
        filtrados.sort(key=lambda p: float(p.get('precio') or 0), reverse=True)
    elif ordenar_por == 'nombre_asc':
        filtrados.sort(key=lambda p: (p.get('nombre') or '').lower())
    elif ordenar_por in ('mas_vendidos', 'destacados'):
        filtrados.sort(key=lambda p: (not p.get('destacado', False), p.get('nombre') or ''))

    mapped = [_map_filtrado(p, categorias) for p in filtrados]

    return jsonify({
        'resultados_encontrados': len(mapped),
        'productos': mapped
    }), 200


def _resumen_carrito(cliente_id):
    items = ItemCarrito.query.filter_by(cliente_id=cliente_id).all()
    total_items = sum(item.cantidad for item in items)
    monto_total = round(sum(float(item.precio_unitario) * item.cantidad for item in items), 2)
    return {
        'items': [item.to_dict() for item in items],
        'total_items': total_items,
        'monto_total': monto_total
    }


@api_v1_bp.route('/carrito', methods=['GET'])
def carrito_obtener():
    cliente, error = _validar_token()
    if error:
        return jsonify({'status': False, 'mensaje': error}), 401
    resumen = _resumen_carrito(cliente.id)
    return jsonify({
        'status': True,
        'mensaje': 'Carrito obtenido correctamente',
        'resumen_carrito': {
            'total_items': resumen['total_items'],
            'monto_total': resumen['monto_total']
        },
        'items': resumen['items']
    }), 200


@api_v1_bp.route('/carrito', methods=['POST'])
def carrito_agregar():
    cliente, error = _validar_token()
    if error:
        return jsonify({'status': False, 'mensaje': error}), 401

    data = request.get_json(silent=True) or {}
    try:
        producto_id = int(data.get('id_producto'))
        cantidad = int(data.get('cantidad', 1))
    except (TypeError, ValueError):
        return jsonify({'status': False, 'mensaje': 'id_producto y cantidad deben ser números enteros'}), 400

    if cantidad <= 0:
        return jsonify({'status': False, 'mensaje': 'La cantidad debe ser mayor que cero'}), 400
    if cantidad > 1000:
        return jsonify({'status': False, 'mensaje': 'La cantidad solicitada es demasiado alta'}), 400

    productos = _catalogo_inventario()
    producto = next((p for p in productos if int(p.get('id')) == producto_id), None)
    if not producto:
        return jsonify({'status': False, 'mensaje': 'Producto no encontrado o no disponible'}), 404
    if int(producto.get('cantidad') or 0) < cantidad:
        return jsonify({'status': False, 'mensaje': 'Stock insuficiente'}), 400

    precio = float(producto.get('precio') or 0)
    nombre = producto.get('nombre') or 'Producto'
    imagen = producto.get('imagen') or producto.get('imagen_url')

    item = ItemCarrito.query.filter_by(cliente_id=cliente.id, producto_id=producto_id).first()
    if item:
        item.cantidad += cantidad
        item.precio_unitario = precio
        item.nombre_producto = nombre
        item.imagen = imagen
    else:
        item = ItemCarrito(
            cliente_id=cliente.id,
            producto_id=producto_id,
            nombre_producto=nombre,
            precio_unitario=precio,
            cantidad=cantidad,
            imagen=imagen
        )
        db.session.add(item)

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({'status': False, 'mensaje': 'No se pudo actualizar el carrito'}), 500

    resumen = _resumen_carrito(cliente.id)
    return jsonify({
        'status': True,
        'mensaje': 'Producto agregado al carrito',
        'resumen_carrito': {
            'total_items': resumen['total_items'],
            'monto_total': resumen['monto_total']
        }
    }), 201


@api_v1_bp.route('/carrito', methods=['DELETE'])
def carrito_eliminar():
    cliente, error = _validar_token()
    if error:
        return jsonify({'status': False, 'mensaje': error}), 401

    producto_id = request.args.get('id_producto', type=int)
    if producto_id is None:
        return jsonify({'status': False, 'mensaje': 'Debes indicar id_producto'}), 400

    item = ItemCarrito.query.filter_by(cliente_id=cliente.id, producto_id=producto_id).first()
    if not item:
        return jsonify({'status': False, 'mensaje': 'El producto no está en el carrito'}), 404
    db.session.delete(item)
    db.session.commit()
    resumen = _resumen_carrito(cliente.id)
    return jsonify({
        'status': True,
        'mensaje': 'Producto eliminado del carrito',
        'resumen_carrito': {
            'total_items': resumen['total_items'],
            'monto_total': resumen['monto_total']
        }
    }), 200
