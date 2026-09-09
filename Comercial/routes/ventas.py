# Comercial/routes/ventas.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db
from models.ventas import Venta
from models.clientes import Cliente
from services.emailService import enviar_comprobante_email
from datetime import datetime
import requests
import os

ventas_bp = Blueprint('ventas', __name__, template_folder='../templates')

INVENTARIO_URL = os.getenv('INVENTARIO_URL', 'http://localhost:8002')

@ventas_bp.route("/")
def ver_ventas():
    """Listar ventas del cliente"""
    ventas = Venta.query.filter_by(cliente_id=session.get("cliente_id")).order_by(Venta.fecha_venta.desc()).all()
    return render_template("ventas_cliente.html", ventas=ventas)

@ventas_bp.route("/comprobante/<int:venta_id>")
def ver_comprobante(venta_id):
    """Ver comprobante de una venta"""
    venta = Venta.query.get_or_404(venta_id)

    if venta.cliente_id != session.get("cliente_id"):
        flash("❌ No tienes permiso para ver este comprobante", "danger")
        return redirect(url_for("ventas.ver_ventas"))
    
    try:
        response = requests.get(f"{INVENTARIO_URL}/api/productos/{venta.producto_id}", timeout=5)
        if response.status_code == 200:
            producto = response.json()
        else:
            producto = {"nombre": f"Producto #{venta.producto_id}", "precio": 0}
    except:
        producto = {"nombre": f"Producto #{venta.producto_id}", "precio": 0}
    
    total = venta.cantidad * float(producto.get("precio", 0))
    
    return render_template("comprobante.html", venta=venta, producto=producto, total=total)