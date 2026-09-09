from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from app import db
from models.venta import Venta

ventas_bp = Blueprint('ventas', __name__)

@ventas_bp.route('/ventas/nueva', methods=['GET', 'POST'])
def nueva_venta():
    if request.method == 'POST':
        venta = Venta(
            vendedor_id=session.get('usuario_id'),
            cliente_email=request.form.get('cliente_email'),
            cliente_nombres=request.form.get('cliente_nombres'),
            cliente_apellidos=request.form.get('cliente_apellidos'),
            cliente_documento=request.form.get('cliente_documento'),
            cliente_razon_social=request.form.get('cliente_razon_social'),
            cliente_direccion_fiscal=request.form.get('factura_direccion'),
            producto_nombre=request.form.get('producto_nombre'),
            cantidad=request.form.get('cantidad'),
            precio_unitario=request.form.get('precio'),
            total_venta=float(request.form.get('precio')) * int(request.form.get('cantidad')),
            tipo_comprobante=request.form.get('tipo_comprobante', 'boleta')
        )
        db.session.add(venta)
        db.session.commit()
        return redirect(url_for('comprobante', venta_id=venta.id))
    return render_template('ventas_form.html')

@ventas_bp.route('/ventas')
def listar_ventas():
    ventas = Venta.query.all()
    return render_template('ventas.html', ventas=ventas)

@ventas_bp.route('/comprobante/<int:venta_id>')
def comprobante(venta_id):
    venta = Venta.query.get_or_404(venta_id)
    return render_template('comprobante.html', venta=venta)