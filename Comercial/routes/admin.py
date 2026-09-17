from datetime import datetime
from functools import wraps

from flask import (
    Blueprint, flash, redirect, render_template,
    request, session
)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from models.bloqueos import Bloqueo
from models.clientes import Cliente
from models.intentos_login import IntentosLogin
from models.pedidos import Pedido
from models.detallePedido import DetallePedido
from models.usuarioSistema import UsuarioSistema
from models.ventas import Venta
from utils import obtener_ip_cliente, registrar_intento_fallido

admin_bp = Blueprint('admin', __name__)

ESTADOS_PEDIDO = ['pendiente', 'confirmado', 'preparando', 'enviado', 'entregado', 'listo_tienda', 'recogido', 'cancelado']


def _login_requerido(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo', '').strip()
        clave = request.form.get('clave', '')
        ip = obtener_ip_cliente()

        usuario = UsuarioSistema.query.filter_by(correo=correo).first()

        if usuario and not usuario.activo:
            flash('Tu cuenta está bloqueada. Contacta a otro administrador.', 'danger')
            return render_template('login.html')

        bloqueo_permanente = Bloqueo.query.filter_by(
            email=correo, tipo_usuario='sistema', estado=1, permanente=1
        ).first()
        if bloqueo_permanente:
            flash('Cuenta bloqueada permanentemente.', 'danger')
            return render_template('login.html')

        registro = IntentosLogin.query.filter_by(email=correo).first()
        if registro and registro.email_bloqueado and registro.email_bloqueado > datetime.now():
            minutos = (registro.email_bloqueado - datetime.now()).seconds // 60
            flash(f'Cuenta bloqueada temporalmente. Espera {minutos} minutos.', 'danger')
            return render_template('login.html')

        if usuario and check_password_hash(usuario.clave, clave):
            if registro:
                registro.intentos = 0
                registro.email_bloqueado = None
                db.session.commit()
            session['usuario_id'] = usuario.id
            session['nombre'] = f"{usuario.nombres} {usuario.apellidos}".strip()
            session['rol'] = usuario.rol
            return redirect('/dashboard')

        if usuario or registro:
            registrar_intento_fallido(correo, ip, es_cliente=False)
        flash('Credenciales incorrectas', 'danger')

    return render_template('login.html')


@admin_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


@admin_bp.route('/cambiar_clave', methods=['GET', 'POST'])
@_login_requerido
def cambiar_clave():
    if request.method == 'POST':
        actual = request.form.get('actual')
        nueva = request.form.get('nueva')
        confirmar = request.form.get('confirmar')

        if not actual or not nueva or not confirmar:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('cambiar_clave.html')

        if nueva != confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('cambiar_clave.html')

        if len(nueva) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'danger')
            return render_template('cambiar_clave.html')

        usuario = UsuarioSistema.query.get(session['usuario_id'])
        if not check_password_hash(usuario.clave, actual):
            flash('La contraseña actual es incorrecta', 'danger')
            return render_template('cambiar_clave.html')

        usuario.clave = generate_password_hash(nueva)
        db.session.commit()
        flash('Contraseña actualizada correctamente', 'success')
        return redirect('/dashboard')

    return render_template('cambiar_clave.html')


@admin_bp.route('/dashboard')
@_login_requerido
def dashboard():
    return render_template('vendedor_dashboard.html')


@admin_bp.route('/pedidos')
@_login_requerido
def ver_pedidos():
    search = request.args.get('search', '').strip()
    estado = request.args.get('estado', '').strip()
    fecha_desde = request.args.get('fecha_desde', '').strip()
    fecha_hasta = request.args.get('fecha_hasta', '').strip()

    query = Pedido.query

    if search:
        like = f"%{search}%"
        filtros = [Cliente.nombres.like(like), Cliente.apellidos.like(like), Cliente.email.like(like)]
        if search.isdigit():
            filtros.append(Pedido.id == int(search))
        query = query.join(Cliente).filter(db.or_(*filtros))

    if estado in ESTADOS_PEDIDO:
        query = query.filter(Pedido.estado == estado)

    if fecha_desde:
        try:
            desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
            query = query.filter(Pedido.fecha_pedido >= desde)
        except ValueError:
            pass

    if fecha_hasta:
        try:
            hasta = datetime.strptime(fecha_hasta + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
            query = query.filter(Pedido.fecha_pedido <= hasta)
        except ValueError:
            pass

    pedidos = query.order_by(Pedido.fecha_pedido.desc()).all()

    for p in pedidos:
        cliente = p.cliente
        p.cliente_nombre_completo = f"{cliente.nombres} {cliente.apellidos}" if cliente else 'Cliente eliminado'
        p.cliente_email = cliente.email if cliente else ''
        p.cliente_telefono = cliente.telefono if cliente else ''

    lista = pedidos
    total_pedidos = len(lista)
    pedidos_pendientes = sum(1 for p in lista if p.estado == 'pendiente')
    pedidos_en_proceso = sum(1 for p in lista if p.estado in ('confirmado', 'preparando', 'enviado', 'listo_tienda'))
    pedidos_completados = sum(1 for p in lista if p.estado in ('entregado', 'recogido'))

    return render_template('pedidos.html',
                           pedidos=pedidos,
                           estados=ESTADOS_PEDIDO,
                           search=search,
                           estado_filter=estado,
                           fecha_desde=fecha_desde,
                           fecha_hasta=fecha_hasta,
                           total_pedidos=total_pedidos,
                           pedidos_pendientes=pedidos_pendientes,
                           pedidos_completados=pedidos_completados,
                           pedidos_en_proceso=pedidos_en_proceso,
                           es_admin=True)


@admin_bp.route('/pedidos/detalle/<int:pedido_id>')
@_login_requerido
def detalle_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    cliente = pedido.cliente
    detalles = db.session.query(
        DetallePedido.nombre_producto.label('producto_nombre'),
        DetallePedido
    ).filter(DetallePedido.pedido_id == pedido_id).all()
    venta = Venta.query.filter(Venta.numero_comprobante == f"P{pedido_id:06d}").first()
    return render_template('pedido_detalle.html',
                           pedido=pedido,
                           detalles=detalles,
                           cliente=cliente,
                           venta=venta,
                           es_admin=True)


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@_login_requerido
def nuevo_usuario():
    if request.method == 'POST':
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        correo = request.form.get('correo', '').strip()
        rol = request.form.get('rol', 'vendedor')
        clave = request.form.get('clave', '')

        if not nombres or not apellidos or not correo or not clave:
            flash('Todos los campos son obligatorios', 'danger')
            return render_template('usuarios_sistema_form.html')

        if UsuarioSistema.query.filter_by(correo=correo).first():
            flash('Ya existe un usuario con ese correo', 'danger')
            return render_template('usuarios_sistema_form.html')

        if len(clave) < 8:
            flash('La contraseña debe tener al menos 8 caracteres', 'danger')
            return render_template('usuarios_sistema_form.html')

        usuario = UsuarioSistema(
            nombres=nombres,
            apellidos=apellidos,
            correo=correo,
            rol=rol
        )
        usuario.set_password(clave)
        db.session.add(usuario)
        db.session.commit()
        flash('Usuario registrado correctamente', 'success')
        return redirect('/usuarios-sistema')

    return render_template('usuarios_sistema_form.html')


@admin_bp.route('/usuarios-sistema')
@_login_requerido
def gestion_usuarios():
    usuarios = []
    bloqueos = Bloqueo.query.filter_by(tipo_usuario='sistema', estado=1).all()
    bloqueo_por_email = {b.email: b for b in bloqueos}
    intentos = IntentosLogin.query.filter(
        IntentosLogin.email_bloqueado.isnot(None)
    ).all()
    intento_por_email = {i.email: i for i in intentos}

    for usuario in UsuarioSistema.query.order_by(UsuarioSistema.id.asc()).all():
        bloqueo = bloqueo_por_email.get(usuario.correo)
        intento = intento_por_email.get(usuario.correo)
        bloqueado = bool(bloqueo) or bool(intento)

        usuario.bloqueado = bloqueado
        usuario.bloqueo_id = bloqueo.id if bloqueo else None
        usuario.bloqueo_motivo = bloqueo.motivo if bloqueo else None
        usuario.bloqueo_automatico = bool(intento)
        usuario.bloqueo_automatico_motivo = 'Bloqueo automático por múltiples intentos fallidos' if intento else None
        usuario.estado_badge = 'danger' if bloqueado else ('success' if usuario.activo else 'secondary')
        usuario.estado_texto = 'Bloqueado' if bloqueado else ('Activo' if usuario.activo else 'Inactivo')
        usuarios.append(usuario)

    return render_template('usuarios_sistema_gestion.html', usuarios=usuarios)


@admin_bp.route('/usuarios-sistema/bloquear/<int:usuario_id>', methods=['POST'])
@_login_requerido
def bloquear_usuario_sistema(usuario_id):
    usuario = UsuarioSistema.query.get_or_404(usuario_id)
    motivo = request.form.get('motivo', 'Bloqueo manual por administrador')
    Bloqueo.query.filter_by(
        email=usuario.correo, tipo_usuario='sistema', estado=1
    ).update({'estado': 0, 'fecha_desbloqueo': datetime.now()})
    db.session.add(Bloqueo(
        email=usuario.correo,
        tipo_usuario='sistema',
        motivo=motivo,
        permanente=1,
        estado=1
    ))
    usuario.activo = False
    db.session.commit()
    flash(f'Usuario {usuario.nombres} bloqueado', 'success')
    return redirect('/usuarios-sistema')


@admin_bp.route('/usuarios-sistema/desbloquear/<int:usuario_id>', methods=['POST'])
@_login_requerido
def desbloquear_usuario_sistema(usuario_id):
    usuario = UsuarioSistema.query.get_or_404(usuario_id)
    Bloqueo.query.filter_by(
        email=usuario.correo, tipo_usuario='sistema', estado=1
    ).update({'estado': 0, 'fecha_desbloqueo': datetime.now()})
    registro = IntentosLogin.query.filter_by(email=usuario.correo).first()
    if registro:
        registro.email_bloqueado = None
        registro.intentos = 0
    usuario.activo = True
    db.session.commit()
    flash(f'Usuario {usuario.nombres} desbloqueado', 'success')
    return redirect('/usuarios-sistema')


def _componer_bloqueo(bloqueo):
    cliente = Cliente.query.filter(
        db.or_(
            Cliente.id == bloqueo.cliente_id if bloqueo.cliente_id else False,
            Cliente.email == (bloqueo.email or '')
        )
    ).first() if bloqueo.cliente_id or bloqueo.email else None
    usuario = UsuarioSistema.query.filter_by(correo=bloqueo.email).first() if bloqueo.email else None

    if usuario:
        nombre_completo = f"{usuario.nombres} {usuario.apellidos}".strip()
        tipo = 'Sistema'
        rol = usuario.rol
    elif cliente:
        nombre_completo = f"{cliente.nombres} {cliente.apellidos}".strip()
        tipo = 'Cliente'
        rol = None
    else:
        nombre_completo = bloqueo.email or 'N/A'
        tipo = 'Sistema' if bloqueo.tipo_usuario == 'sistema' else 'Cliente'
        rol = None

    return {
        'id_bloqueo': bloqueo.id,
        'tipo': tipo,
        'rol': rol,
        'nombre_completo': nombre_completo,
        'email': bloqueo.email or 'N/A',
        'motivo': bloqueo.motivo or 'Sin motivo',
        'origen': 'Bloqueo manual',
        'fecha_bloqueo': bloqueo.fecha_bloqueo,
        'bloqueado_por': 'Administrador',
        'tipo_origen': 'bloqueos'
    }


def _componer_intento(registro, tipo='Cliente'):
    cliente = Cliente.query.filter_by(email=registro.email).first()
    usuario = UsuarioSistema.query.filter_by(correo=registro.email).first()
    if usuario:
        nombre_completo = f"{usuario.nombres} {usuario.apellidos}".strip()
        rol = usuario.rol
    elif cliente:
        nombre_completo = f"{cliente.nombres} {cliente.apellidos}".strip()
        rol = None
    else:
        nombre_completo = registro.email or 'N/A'
        rol = None

    return {
        'id_bloqueo': None,
        'tipo': 'Sistema' if usuario else tipo,
        'rol': rol,
        'nombre_completo': nombre_completo,
        'email': registro.email or 'N/A',
        'motivo': 'Múltiples intentos fallidos de login',
        'origen': 'Bloqueo automático',
        'fecha_bloqueo': registro.email_bloqueado,
        'bloqueado_por': 'Sistema',
        'tipo_origen': 'intentos'
    }


@admin_bp.route('/bloqueos')
@_login_requerido
def ver_bloqueos():
    lista = []
    for b in Bloqueo.query.filter_by(estado=1).all():
        lista.append(_componer_bloqueo(b))
    registros = IntentosLogin.query.filter(
        IntentosLogin.email_bloqueado.isnot(None)
    ).all()
    for r in registros:
        lista.append(_componer_intento(r))
    return render_template('bloqueos.html', bloqueos=lista)


@admin_bp.route('/bloqueos/desbloquear', methods=['POST'])
@_login_requerido
def desbloquear_usuario_form():
    bloqueo_id = request.form.get('bloqueo_id', type=int)
    if bloqueo_id:
        bloqueo = Bloqueo.query.get(bloqueo_id)
        if bloqueo:
            bloqueo.estado = 0
            bloqueo.fecha_desbloqueo = datetime.now()
            if bloqueo.tipo_usuario == 'sistema' and bloqueo.email:
                UsuarioSistema.query.filter_by(correo=bloqueo.email).update({'activo': True})
        db.session.commit()
    flash('Usuario desbloqueado', 'success')
    return redirect('/bloqueos')


@admin_bp.route('/bloqueos/desbloquear-intento', methods=['POST'])
@_login_requerido
def desbloquear_intento_login():
    email = request.form.get('email', '').strip()
    if email:
        registro = IntentosLogin.query.filter_by(email=email).first()
        if registro:
            registro.email_bloqueado = None
            registro.intentos = 0
        db.session.commit()
    flash('Bloqueo por intentos eliminado', 'success')
    return redirect('/bloqueos')


@admin_bp.route('/bloqueos-sistema')
@_login_requerido
def ver_bloqueos_sistema():
    lista = []
    for b in Bloqueo.query.filter_by(tipo_usuario='sistema', estado=1).all():
        item = _componer_bloqueo(b)
        item['origen'] = 'Manual' if item['origen'] == 'Bloqueo manual' else item['origen']
        lista.append(item)

    correos_sistema = {u.correo for u in UsuarioSistema.query.all()}
    registros = IntentosLogin.query.filter(
        IntentosLogin.email_bloqueado.isnot(None)
    ).all()
    for r in registros:
        if r.email in correos_sistema:
            item = _componer_intento(r, tipo='Sistema')
            item['origen'] = 'Automático'
            lista.append(item)

    return render_template('bloqueos_sistema.html', bloqueos=lista)


@admin_bp.route('/bloqueos-sistema/desbloquear/<int:bloqueo_id>', methods=['POST'])
@_login_requerido
def desbloquear_usuario_admin(bloqueo_id):
    bloqueo = Bloqueo.query.get_or_404(bloqueo_id)
    bloqueo.estado = 0
    bloqueo.fecha_desbloqueo = datetime.now()
    if bloqueo.email:
        UsuarioSistema.query.filter_by(correo=bloqueo.email).update({'activo': True})
        registro = IntentosLogin.query.filter_by(email=bloqueo.email).first()
        if registro:
            registro.email_bloqueado = None
            registro.intentos = 0
    db.session.commit()
    flash('Usuario del sistema desbloqueado', 'success')
    return redirect('/bloqueos-sistema')


@admin_bp.route('/ips-bloqueadas')
@_login_requerido
def ver_ips_bloqueadas():
    registros = IntentosLogin.query.filter(
        IntentosLogin.ip_bloqueado.isnot(None)
    ).all()
    ips = []
    for r in registros:
        mismo_ip = IntentosLogin.query.filter_by(ip=r.ip).all()
        em = {x.email for x in mismo_ip if x.email}
        ips.append({
            'ip': r.ip,
            'email': r.email,
            'usuarios_distintos': len(em),
            'intentos': sum(x.intentos_totales or 0 for x in mismo_ip),
            'ips_bloqueadas': r.ip_bloqueado
        })
    return render_template('ips_bloqueadas.html', ips=ips)


@admin_bp.route('/desbloquear-ip/<ip>')
@_login_requerido
def desbloquear_ip(ip):
    registros = IntentosLogin.query.filter_by(ip=ip).all()
    for r in registros:
        r.ip_bloqueado = None
    db.session.commit()
    flash(f'IP {ip} desbloqueada', 'success')
    return redirect('/ips-bloqueadas')