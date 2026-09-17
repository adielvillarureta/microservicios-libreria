import os
from datetime import datetime, date

import requests
from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from extensions import db
from models.ventas import Venta
from models.clientes import Cliente
from models.usuarioSistema import UsuarioSistema
from services.emailService import enviar_comprobante_email

INVENTARIO_URL = os.getenv('INVENTARIO_API_URL') or os.getenv('INVENTARIO_URL', 'http://localhost:5001')

ventas_bp = Blueprint('ventas', __name__)


def _obtener_productos():
    try:
        response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    return []


def _obtener_vendedores():
    return UsuarioSistema.query.filter_by(activo=True).all()


def _enriquecer_venta(venta):
    venta.producto = venta.producto_nombre
    vendedor = UsuarioSistema.query.get(venta.vendedor_id) if venta.vendedor_id else None
    venta.vendedor_nombres = vendedor.nombres if vendedor else None
    venta.vendedor_apellidos = vendedor.apellidos if vendedor else None
    return venta


@ventas_bp.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    productos = _obtener_productos()
    vendedores = _obtener_vendedores()

    if request.method == 'POST':
        vendedor_id = request.form.get('vendedor_id') or session.get('usuario_id')
        producto_id = request.form.get('producto_id')
        producto = next((p for p in productos if str(p.get('id')) == str(producto_id)), None)
        if not producto:
            return render_template('ventas_form.html', productos=productos, vendedores=vendedores, error='Producto no encontrado')

        try:
            cantidad = int(request.form.get('cantidad', 1))
        except ValueError:
            cantidad = 1
        try:
            precio = float(producto.get('precio', 0))
        except (TypeError, ValueError):
            precio = 0.0
        total_venta = round(precio * cantidad, 2)

        tipo_comprobante = request.form.get('tipo_comprobante', 'boleta')

        venta = Venta(
            vendedor_id=int(vendedor_id) if vendedor_id else None,
            cliente_email=request.form.get('cliente_email'),
            cliente_nombres=request.form.get('cliente_nombres'),
            cliente_apellidos=request.form.get('cliente_apellidos'),
            cliente_documento=request.form.get('cliente_documento'),
            cliente_razon_social=request.form.get('cliente_razon_social'),
            cliente_direccion_fiscal=request.form.get('factura_direccion'),
            producto_nombre=producto.get('nombre'),
            cantidad=cantidad,
            precio_unitario=precio,
            total_venta=total_venta,
            tipo_comprobante=tipo_comprobante
        )
        db.session.add(venta)
        db.session.flush()
        prefijo = 'F' if tipo_comprobante == 'factura' else 'B'
        venta.numero_comprobante = f"{prefijo}{venta.id:06d}"
        db.session.commit()

        if request.form.get('enviar_email') == '1' and venta.cliente_email:
            try:
                enviar_comprobante_email(
                    destinatario=venta.cliente_email,
                    cliente_nombre=f"{venta.cliente_nombres or ''} {venta.cliente_apellidos or ''}".strip() or venta.cliente_razon_social,
                    tipo_comprobante=tipo_comprobante,
                    numero_comprobante=venta.numero_comprobante,
                    fecha=venta.fecha_venta or datetime.utcnow(),
                    productos=[{
                        'nombre': venta.producto_nombre,
                        'cantidad': venta.cantidad,
                        'precio_unitario': float(venta.precio_unitario or 0),
                        'total': float(venta.total_venta or 0)
                    }],
                    total_venta=float(venta.total_venta or 0)
                )
            except Exception:
                pass

        return redirect(url_for('ventas.comprobante', venta_id=venta.id))

    return render_template('ventas_form.html', productos=productos, vendedores=vendedores)


@ventas_bp.route('/ventas')
def listar_ventas():
    rol = session.get('rol')
    vendedor_id = request.args.get('vendedor_id', type=int)
    if rol == 'vendedor':
        vendedor_id = session.get('usuario_id')

    query = Venta.query
    if vendedor_id:
        query = query.filter(Venta.vendedor_id == vendedor_id)
    ventas = [ _enriquecer_venta(v) for v in query.order_by(Venta.fecha_venta.desc()).all() ]
    return render_template(
        'ventas.html',
        ventas=ventas,
        vendedores=_obtener_vendedores(),
        vendedor_id_actual=vendedor_id,
        rol_usuario=rol
    )


@ventas_bp.route('/comprobante/<int:venta_id>')
def comprobante(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    venta = _enriquecer_venta(venta)
    total = float(venta.precio_unitario) * int(venta.cantidad)
    return render_template('comprobante.html', venta=venta, total=total)


@ventas_bp.route('/ver_ventas', methods=['GET', 'POST'])
def ver_ventas():
    fecha_seleccionada = None
    ventas = []
    total_productos = 0
    total_precio = 0.0

    if request.method == 'POST':
        fecha_str = request.form.get('fecha')
        if fecha_str:
            try:
                fecha_seleccionada = fecha_str
                fecha_obj = datetime.strptime(fecha_str, '%Y-%m-%d').date()
                registros = Venta.query.filter(
                    db.func.date(Venta.fecha_venta) == fecha_obj
                ).all()
                ventas = [ _enriquecer_venta(v) for v in registros ]
                ventas.sort(key=lambda v: v.fecha_venta or datetime.utcnow())
                total_productos = sum(int(v.cantidad) for v in ventas)
                total_precio = sum(float(v.total_venta) for v in ventas)
            except ValueError:
                pass

    return render_template(
        'ver_ventas.html',
        fecha_seleccionada=fecha_seleccionada,
        ventas=ventas,
        totalProductos=total_productos,
        totalPrecio=total_precio
    )


@ventas_bp.route('/api/buscar_producto')
def api_buscar_producto():
    q = request.args.get('q', '')
    if not q:
        return jsonify({'error': 'Parámetro q requerido'}), 400
    try:
        response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", params={'q': q}, timeout=5)
        if response.status_code == 200:
            resultados = response.json()
            if resultados:
                p = resultados[0]
                return jsonify({
                    'id': p.get('id'),
                    'nombre': p.get('nombre'),
                    'precio': p.get('precio'),
                    'stock': p.get('cantidad', 0)
                })
        return jsonify({'error': 'Producto no encontrado'}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'El microservicio de Inventario no está disponible'}), 503
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@ventas_bp.route('/api/ventas/rapida', methods=['POST'])
def api_venta_rapida():
    data = request.get_json(silent=True) or {}
    items = data.get('items') or []
    if not items:
        return jsonify({'success': False, 'error': 'Carrito vacío'})

    cliente_dni = data.get('cliente_dni')
    cliente = Cliente.query.filter_by(dni=cliente_dni).first() if cliente_dni else None

    cantidad_total = sum(int(i.get('cantidad', 1)) for i in items)
    total_venta = round(sum(float(i.get('precio', 0)) * int(i.get('cantidad', 1)) for i in items), 2)
    nombres_items = ', '.join(i.get('nombre', '') for i in items[:3])
    if len(items) > 3:
        nombres_items += f" y {len(items) - 3} más"

    venta = Venta(
        vendedor_id=session.get('usuario_id'),
        cliente_email=cliente.email if cliente else None,
        cliente_nombres=cliente.nombres if cliente else None,
        cliente_apellidos=cliente.apellidos if cliente else None,
        cliente_documento=cliente_dni,
        producto_nombre=nombres_items,
        cantidad=cantidad_total,
        precio_unitario=0,
        total_venta=total_venta,
        tipo_comprobante=data.get('tipo_comprobante', 'boleta')
    )
    db.session.add(venta)
    db.session.flush()
    venta.numero_comprobante = f"B{venta.id:06d}"
    db.session.commit()

    return jsonify({'success': True, 'venta_id': venta.id, 'total': total_venta})