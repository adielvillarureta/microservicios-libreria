import os

import requests
from flask import Blueprint, jsonify, render_template, redirect, request, session

from extensions import db
from models.clientes import Cliente
from models.detallePedido import DetallePedido
from models.pedidos import Pedido
from models.ventas import Venta
from utils import login_required_cliente, obtener_categorias

pedidos_bp = Blueprint('pedidos_bp', __name__)

API_TOKEN = os.getenv('API_PERU_TOKEN') or os.getenv('API_TOKEN') or '1a6fa9efa854259ed29a4c5fa8401bb9d61d7863170d97c798822b5cf377'


@pedidos_bp.route('/carrito')
def carrito():
    return render_template('carrito.html', categorias=obtener_categorias())


@pedidos_bp.route('/checkout')
def checkout():
    cliente = None
    if session.get('cliente_id'):
        cliente = Cliente.query.get(session['cliente_id'])
    return render_template('checkout.html', cliente=cliente, categorias=obtener_categorias())


@pedidos_bp.route('/pago')
def pago():
    cliente = None
    if session.get('cliente_id'):
        cliente = Cliente.query.get(session['cliente_id'])
    return render_template('pago.html', cliente=cliente, categorias=obtener_categorias())


@pedidos_bp.route('/acerca-de')
def acerca_de():
    return render_template('acerca_de.html', categorias=obtener_categorias())


@pedidos_bp.route('/mis-pedidos')
@login_required_cliente
def mis_pedidos():
    pedidos = Pedido.query.filter_by(cliente_id=session['cliente_id']).order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('mis_pedidos.html', pedidos=pedidos, categorias=obtener_categorias())


@pedidos_bp.route('/mis-pedidos/detalle/<int:pedido_id>')
@login_required_cliente
def detalle_pedido_cliente(pedido_id):
    pedido = Pedido.query.filter_by(id=pedido_id, cliente_id=session['cliente_id']).first()
    if not pedido:
        return redirect('/mis-pedidos')

    detalles = db.session.query(
        DetallePedido.nombre_producto.label('producto_nombre'),
        DetallePedido
    ).filter(DetallePedido.pedido_id == pedido.id).all()

    cliente = Cliente.query.get(pedido.cliente_id)
    venta = Venta.query.filter_by(cliente_email=cliente.email if cliente else None).order_by(Venta.id.desc()).first()

    return render_template(
        'cliente_pedido_detalle.html',
        pedido=pedido,
        detalles=detalles,
        cliente=cliente,
        venta=venta,
        categorias=obtener_categorias()
    )


@pedidos_bp.route('/api/cliente/direccion')
def api_cliente_direccion():
    direccion = session.get('cliente_direccion')
    return jsonify({'success': True, 'direccion': direccion or ''})


@pedidos_bp.route('/api/pedidos/crear', methods=['POST'])
def crear_pedido():
    data = request.get_json(silent=True) or {}
    cliente_data = data.get('cliente') or {}
    items = data.get('items') or []
    tipo_entrega = data.get('tipo_entrega', 'recojo')
    metodo_pago = data.get('metodo_pago', '').strip()

    if not items:
        return jsonify({'success': False, 'error': 'El carrito está vacío'}), 400

    nombre = cliente_data.get('nombres', '').strip()
    apellido = cliente_data.get('apellidos', '').strip()
    email = cliente_data.get('email', '').strip()
    telefono = cliente_data.get('telefono', '').strip()
    documento = cliente_data.get('documento', '').strip()
    direccion = cliente_data.get('direccion', '').strip()

    if not nombre or not email:
        return jsonify({'success': False, 'error': 'Completa tus datos de facturación'}), 400

    cliente = Cliente.query.filter_by(email=email).first()
    if not cliente and session.get('cliente_id'):
        cliente = Cliente.query.get(session['cliente_id'])

    if not cliente:
        dni_valido = documento if (len(documento) == 8 and not Cliente.query.filter_by(dni=documento).first()) else None
        cliente = Cliente(
            nombres=nombre,
            apellidos=apellido,
            email=email,
            telefono=telefono,
            dni=dni_valido,
            direccion=direccion,
            clave=os.urandom(24).hex()
        )
        db.session.add(cliente)
        db.session.flush()

    if len(documento) == 8 and cliente.dni != documento:
        duplicado_dni = Cliente.query.filter(Cliente.dni == documento, Cliente.id != cliente.id).first()
        if not duplicado_dni:
            cliente.dni = documento
    if not cliente.telefono and telefono:
        cliente.telefono = telefono
    if not cliente.direccion and direccion:
        cliente.direccion = direccion

    total = 0.0
    for item in items:
        cantidad = int(item.get('cantidad', 1))
        precio = float(item.get('precio', 0))
        total += cantidad * precio

    if tipo_entrega == 'delivery':
        total += 5.0

    if metodo_pago == 'contraentrega' and tipo_entrega == 'delivery':
        total += 3.0

    pedido = Pedido(
        cliente_id=cliente.id,
        total=total,
        estado='pendiente',
        tipo_entrega=tipo_entrega,
        direccion_entrega=direccion,
        metodo_pago=metodo_pago or None
    )
    db.session.add(pedido)
    db.session.flush()

    for item in items:
        cantidad = int(item.get('cantidad', 1))
        precio = float(item.get('precio', 0))
        detalle = DetallePedido(
            pedido_id=pedido.id,
            producto_id=item.get('id'),
            nombre_producto=item.get('nombre', ''),
            cantidad=cantidad,
            precio_unitario=precio,
            subtotal=cantidad * precio
        )
        db.session.add(detalle)

    tipo_comprobante = (data.get('comprobante') or {}).get('tipo', 'boleta')
    venta = Venta(
        vendedor_id=None,
        cliente_email=email,
        cliente_nombres=nombre,
        cliente_apellidos=apellido,
        cliente_documento=documento,
        cliente_razon_social=cliente_data.get('razon_social', ''),
        cliente_direccion_fiscal=direccion,
        producto_nombre=items[0].get('nombre', ''),
        cantidad=int(items[0].get('cantidad', 1)),
        precio_unitario=float(items[0].get('precio', 0)),
        total_venta=total,
        tipo_comprobante=tipo_comprobante,
        numero_comprobante=f"P{pedido.id:06d}"
    )
    db.session.add(venta)
    db.session.commit()

    return jsonify({'success': True, 'pedido_id': pedido.id, 'total': total})


@pedidos_bp.route('/pedidos/cambiar-estado/<int:pedido_id>', methods=['POST'])
def cambiar_estado_pedido(pedido_id):
    pedido = Pedido.query.get(pedido_id)
    if not pedido:
        response = jsonify({'success': False, 'error': 'Pedido no encontrado'})
        return response if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else redirect('/pedidos')

    estado = request.form.get('estado') or (request.get_json(silent=True) or {}).get('estado')
    if estado and estado in {'pendiente', 'confirmado', 'preparando', 'enviado', 'listo_tienda', 'entregado', 'recogido', 'cancelado'}:
        pedido.estado = estado
        db.session.commit()

    response = jsonify({'success': True, 'message': 'Estado actualizado correctamente'})
    return response if request.headers.get('X-Requested-With') == 'XMLHttpRequest' else redirect('/pedidos/detalle/' + str(pedido.id))


def _consultar_documento(endpoint, payload_key, numero):
    token = API_TOKEN
    if not token:
        return {'success': False, 'error': 'Servicio no configurado'}
    url = f'https://api.apiperu.pe/{endpoint}'
    try:
        resp = requests.post(
            url,
            json={payload_key: numero},
            headers={
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            },
            timeout=10
        )
        if resp.status_code == 200:
            data = resp.json()
            if data.get('success') is False:
                return {'success': False, 'error': data.get('message', 'No encontrado')}
            return {'success': True, 'data': data.get('data', data)}
        return {'success': False, 'error': 'No encontrado'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def _nombre_v1(nombre_completo):
    partes = (nombre_completo or '').split()
    if len(partes) >= 3:
        return ' '.join(partes[2:]), ' '.join(partes[:2])
    if len(partes) == 2:
        return partes[0], partes[1]
    if partes:
        return partes[0], ''
    return '', ''


@pedidos_bp.route('/api/consultar-dni/<documento>')
def consultar_dni(documento):
    resultado = _consultar_documento('dni', 'dni', documento)
    if not resultado['success']:
        return jsonify(resultado)
    data = resultado['data']
    nombres = data.get('nombres') or ''
    apellidos = f"{data.get('apellido_paterno', '')} {data.get('apellido_materno', '')}".strip()
    if not apellidos and data.get('nombre_completo'):
        nombres, apellidos = _nombre_v1(data.get('nombre_completo'))
    if not nombres and data.get('nombre'):
        nombres, apellidos = _nombre_v1(data.get('nombre'))
    return jsonify({'success': True, 'nombres': nombres, 'apellidos': apellidos})


@pedidos_bp.route('/api/consultar-ruc/<documento>')
def consultar_ruc(documento):
    resultado = _consultar_documento('ruc', 'ruc', documento)
    if not resultado['success']:
        return jsonify(resultado)
    data = resultado['data']
    razon = data.get('nombre_o_razon_social') or data.get('razon_social') or data.get('nombre') or data.get('nombre_comercial') or ''
    return jsonify({
        'success': True,
        'razon_social': razon
    })