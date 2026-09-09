# Comercial/routes/pedidos.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from models.clientes import Cliente
from models.pedidos import Pedido
from models.detallePedido import DetallePedido
from models.ventas import Venta
from services.emailService import enviar_comprobante_email
from functools import wraps
from datetime import datetime
import requests
import os

pedidos_bp = Blueprint('pedidos', __name__, template_folder='../templates')

INVENTARIO_URL = os.getenv('INVENTARIO_URL', 'http://localhost:8002')

def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cliente_id" not in session:
            flash("Debes iniciar sesión para continuar", "warning")
            return redirect(url_for("clientes.login_cliente"))
        return f(*args, **kwargs)
    return decorated_function

@pedidos_bp.route("/mis-pedidos")
@login_required_cliente
def mis_pedidos():
    pedidos = Pedido.query.filter_by(cliente_id=session["cliente_id"]).order_by(Pedido.fecha_pedido.desc()).all()
    return render_template("mis_pedidos.html", pedidos=pedidos)

@pedidos_bp.route("/detalle/<int:pedido_id>")
@login_required_cliente
def detalle_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    
    if pedido.cliente_id != session.get("cliente_id"):
        flash("❌ No tienes permiso para ver este pedido", "danger")
        return redirect(url_for("pedidos.mis_pedidos"))
    
    detalles = DetallePedido.query.filter_by(pedido_id=pedido_id).all()
    
    # Obtener nombres de productos del microservicio de inventario
    for detalle in detalles:
        try:
            response = requests.get(f"{INVENTARIO_URL}/api/productos/{detalle.producto_id}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                detalle.producto_nombre = data.get('nombre', f'Producto #{detalle.producto_id}')
            else:
                detalle.producto_nombre = f'Producto #{detalle.producto_id}'
        except:
            detalle.producto_nombre = f'Producto #{detalle.producto_id}'
    
    cliente = Cliente.query.get(pedido.cliente_id)
    
    return render_template("cliente_pedido_detalle.html", 
                          pedido=pedido, 
                          detalles=detalles, 
                          cliente=cliente)

@pedidos_bp.route("/api/crear", methods=["POST"])
@login_required_cliente
def crear_pedido():
    """Crear un nuevo pedido desde el carrito"""
    data = request.get_json()
    
    try:
        # Verificar stock en el microservicio de inventario
        for item in data["items"]:
            response = requests.post(
                f"{INVENTARIO_URL}/api/verificar-stock",
                json={"producto_id": item["id"], "cantidad": item["cantidad"]},
                timeout=5
            )
            if response.status_code != 200 or not response.json().get("disponible"):
                return jsonify({
                    "success": False, 
                    "error": f'Stock insuficiente: {item["nombre"]}'
                })
        
        cliente_data = data.get("cliente", {})
        cliente = Cliente.query.get(session["cliente_id"])
        
        # Crear pedido
        pedido = Pedido(
            cliente_id=session["cliente_id"],
            total=float(data["total"]),
            tipo_entrega=data["tipo_entrega"],
            direccion_entrega=data.get("direccion", ""),
            nota=data.get("nota", "")
        )
        db.session.add(pedido)
        db.session.flush()
        
        productos_para_correo = []
        
        for item in data["items"]:
            subtotal = float(item["precio"]) * int(item["cantidad"])
            
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=item["id"],
                cantidad=int(item["cantidad"]),
                precio_unitario=float(item["precio"]),
                subtotal=subtotal
            )
            db.session.add(detalle)
            
            # Registrar venta
            venta = Venta(
                producto_id=item["id"],
                cantidad=int(item["cantidad"]),
                vendedor_id=1,  # Vendedor por defecto
                fecha_venta=datetime.now(),
                tipo_comprobante=data.get("comprobante", {}).get("tipo", "boleta"),
                numero_comprobante=f"ONLINE-{pedido.id}",
                cliente_id=session["cliente_id"],
                cliente_nombres=cliente.nombres,
                cliente_apellidos=cliente.apellidos,
                cliente_documento=cliente.dni or "",
                cliente_email=cliente.correo,
                cliente_direccion=cliente.direccion or "",
                cliente_direccion_fiscal=data.get("cliente", {}).get("direccion_fiscal", ""),
                cliente_razon_social=data.get("cliente", {}).get("razon_social", "")
            )
            db.session.add(venta)
            
            productos_para_correo.append({
                'nombre': item["nombre"],
                'cantidad': int(item["cantidad"]),
                'precio_unitario': float(item["precio"]),
                'total': subtotal
            })
        
        db.session.commit()
        
        # Notificar al microservicio de inventario para actualizar stock
        for item in data["items"]:
            requests.post(
                f"{INVENTARIO_URL}/api/actualizar-stock",
                json={"producto_id": item["id"], "cantidad": item["cantidad"]},
                timeout=5
            )
        
        # Enviar comprobante por email
        try:
            from services.emailService import enviar_comprobante_email
            enviar_comprobante_email(
                destinatario=cliente.correo,
                cliente_nombre=f"{cliente.nombres} {cliente.apellidos}",
                tipo_comprobante=data.get("comprobante", {}).get("tipo", "boleta"),
                numero_comprobante=f"ONLINE-{pedido.id}",
                fecha=datetime.now(),
                productos=productos_para_correo,
                total_venta=float(data["total"])
            )
        except Exception as e:
            print(f"⚠️ Error al enviar correo: {e}")
        
        return jsonify({"success": True, "pedido_id": pedido.id})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error en crear_pedido: {e}")
        return jsonify({"success": False, "error": str(e)})