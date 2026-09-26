from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models.bloqueo import Bloqueo
from services.authService import AuthService

usuario_bp = Blueprint('usuario', __name__)


def _ip_cliente():
    xff = request.headers.get('X-Forwarded-For')
    if xff:
        return xff.split(',')[0].strip()
    return request.remote_addr or 'desconocida'


@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ip = _ip_cliente()
        if Bloqueo.ip_bloqueada(ip):
            return render_template(
                'login.html',
                error='IP bloqueada por intentos fallidos. Espere 10 minutos o contacte al administrador.'
            )

        correo = request.form.get('correo')
        clave = request.form.get('clave')

        usuario = AuthService.authenticate(correo, clave)
        if usuario and usuario.activo:
            Bloqueo.liberar(ip)
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombres
            session['rol'] = usuario.rol
            return redirect(url_for('dashboard'))

        if usuario and not usuario.activo:
            error = "Usuario desactivado, contacte al administrador"
        else:
            Bloqueo.registrar_fallo(ip)
            error = "Credenciales incorrectas"
        return render_template('login.html', error=error)

    return render_template('login.html')


@usuario_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))


@usuario_bp.route('/mi-panel')
def mi_panel():
    if 'usuario_id' not in session:
        return redirect(url_for('usuario.login'))
    if session.get('rol') != 'vendedor':
        flash('El panel del vendedor es exclusivo del rol vendedor', 'warning')
        return redirect(url_for('dashboard'))

    from models.movimientoStock import MovimientoStock
    from models.producto import Producto

    con_stock = Producto.query.filter(Producto.cantidad > 0, Producto.estado.is_(True)).count()
    bajos = Producto.query.filter(
        Producto.cantidad > 0,
        Producto.cantidad <= Producto.stock_minimo,
        Producto.estado.is_(True)
    ).order_by(Producto.cantidad.asc()).all()
    agotados = Producto.query.filter(
        Producto.cantidad == 0,
        Producto.estado.is_(True)
    ).order_by(Producto.nombre.asc()).all()
    movimientos = MovimientoStock.query.order_by(MovimientoStock.fecha.desc()).limit(10).all()

    return render_template(
        'mi_panel.html',
        con_stock=con_stock,
        bajos=bajos,
        agotados=agotados,
        movimientos=movimientos
    )
