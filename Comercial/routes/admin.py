from flask import Blueprint, render_template, session, redirect, url_for, request
from extensions import db
from models.pedidos import Pedido
from models.ventas import Venta
from models.clientes import Cliente
from models.usuarioSistema import UsuarioSistema
from werkzeug.security import check_password_hash

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('admin.login'))
    
    pedidos = Pedido.query.count()
    ventas = Venta.query.count()
    clientes = Cliente.query.count()
    
    return render_template('dashboard.html', 
                           total_pedidos=pedidos, 
                           total_ventas=ventas, 
                           total_clientes=clientes)

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        clave = request.form.get('clave')
        usuario = UsuarioSistema.query.filter_by(correo=correo).first()
        
        if usuario and check_password_hash(usuario.clave, clave):
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombres
            session['rol'] = usuario.rol
            return redirect(url_for('admin.dashboard'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    
    return render_template('login.html')

@admin_bp.route('/pedidos')
def pedidos():
    pedidos = Pedido.query.order_by(Pedido.fecha_pedido.desc()).all()
    return render_template('pedidos.html', pedidos=pedidos)

@admin_bp.route('/pedidos/detalle/<int:pedido_id>')
def detalle_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    detalles = pedido.detalles
    venta = Venta.query.filter_by(id=pedido.id).first()
    return render_template('pedido_detalle.html', pedido=pedido, detalles=detalles, venta=venta)