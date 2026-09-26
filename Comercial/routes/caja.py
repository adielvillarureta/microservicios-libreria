"""
=============================================================================
 MICROSERVICIO COMERCIAL - Modulo de Caja
 Unidad didactica: Inteligencia de Negocios

 Implementa el ciclo de caja que alimenta el KPI 7
 (Precision en el cierre de caja): abrir turno, registrar movimientos
 y cerrar con arqueo. Al cerrar se calcula automaticamente la diferencia
 entre el monto esperado (inicial + ventas en efectivo - egresos) y el real.
=============================================================================
"""
from datetime import datetime

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for
from sqlalchemy import text

from extensions import db
from models.cajas import Caja
from models.movimientoCaja import MovimientoCaja
from models.usuarioSistema import UsuarioSistema

caja_bp = Blueprint('caja', __name__)


def _login_requerido(f):
    from functools import wraps

    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return wrapper


def _caja_abierta_de(usuario_id):
    return Caja.query.filter_by(usuario_id=usuario_id, estado='abierta').first()


@caja_bp.route('/caja')
@_login_requerido
def ver_caja():
    usuario_id = session['usuario_id']
    abierta = _caja_abierta_de(usuario_id)

    historial = Caja.query.filter_by(usuario_id=usuario_id) \
        .order_by(Caja.fecha_apertura.desc()).limit(30).all()

    total_ventas_efectivo = 0.0
    if abierta:
        fila = db.session.execute(text("""
            SELECT COALESCE(SUM(total_venta),0)
            FROM ventas
            WHERE vendedor_id = :uid AND metodo_pago = 'efectivo' AND estado = 1
              AND fecha_venta >= :apertura
        """), {'uid': usuario_id, 'apertura': abierta.fecha_apertura}).scalar()
        total_ventas_efectivo = float(fila or 0)

    movimientos = []
    if abierta:
        movimientos = MovimientoCaja.query.filter_by(caja_id=abierta.id) \
            .order_by(MovimientoCaja.creado_en.desc()).all()

    return render_template(
        'caja.html',
        caja_abierta=abierta,
        historial=historial,
        movimientos=movimientos,
        total_ventas_efectivo=total_ventas_efectivo,
        monto_esperado=(float(abierta.monto_inicial) + total_ventas_efectivo) if abierta else 0.0
    )


@caja_bp.route('/caja/abrir', methods=['POST'])
@_login_requerido
def abrir_caja():
    usuario_id = session['usuario_id']

    if _caja_abierta_de(usuario_id):
        return jsonify({'success': False, 'error': 'Ya tienes una caja abierta'}), 400

    try:
        monto_inicial = float(request.form.get('monto_inicial', 200))
    except (TypeError, ValueError):
        monto_inicial = 200.0

    caja = Caja(
        usuario_id=usuario_id,
        fecha_apertura=datetime.now(),
        monto_inicial=monto_inicial,
        estado='abierta'
    )
    db.session.add(caja)
    db.session.flush()

    db.session.add(MovimientoCaja(
        caja_id=caja.id, tipo='INGRESO', monto=monto_inicial,
        concepto='Fondo de apertura', creado_en=datetime.now()
    ))
    db.session.commit()

    return jsonify({'success': True, 'caja_id': caja.id, 'monto_inicial': monto_inicial})


@caja_bp.route('/caja/movimiento', methods=['POST'])
@_login_requerido
def registrar_movimiento():
    usuario_id = session['usuario_id']
    caja = _caja_abierta_de(usuario_id)

    if not caja:
        return jsonify({'success': False, 'error': 'No tienes una caja abierta'}), 400

    tipo = request.form.get('tipo', 'EGRESO')
    if tipo not in ('INGRESO', 'EGRESO'):
        return jsonify({'success': False, 'error': 'Tipo de movimiento invalido'}), 400

    try:
        monto = float(request.form.get('monto', 0))
        concepto = request.form.get('concepto', '').strip()
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Monto invalido'}), 400

    if monto <= 0 or not concepto:
        return jsonify({'success': False, 'error': 'Monto y concepto son obligatorios'}), 400

    db.session.add(MovimientoCaja(
        caja_id=caja.id, tipo=tipo, monto=monto, concepto=concepto,
        referencia=request.form.get('referencia'), creado_en=datetime.now()
    ))
    db.session.commit()

    return jsonify({'success': True, 'tipo': tipo, 'monto': monto, 'concepto': concepto})


@caja_bp.route('/caja/cerrar', methods=['POST'])
@_login_requerido
def cerrar_caja():
    usuario_id = session['usuario_id']
    caja = _caja_abierta_de(usuario_id)

    if not caja:
        return jsonify({'success': False, 'error': 'No tienes una caja abierta'}), 400

    try:
        monto_real = float(request.form.get('monto_real', 0))
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Monto real invalido'}), 400

    # Monto esperado = fondo inicial + ventas en efectivo del turno + ingresos - egresos
    ventas_efectivo = float(db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0)
        FROM ventas
        WHERE vendedor_id = :uid AND metodo_pago = 'efectivo' AND estado = 1
          AND fecha_venta >= :apertura
    """), {'uid': usuario_id, 'apertura': caja.fecha_apertura}).scalar() or 0)

    mov = db.session.execute(text("""
        SELECT COALESCE(SUM(CASE WHEN tipo='INGRESO' THEN monto ELSE -monto END),0)
        FROM movimientos_caja WHERE caja_id = :cid
    """), {'cid': caja.id}).scalar()
    netos_movimientos = float(mov or 0) - float(caja.monto_inicial or 0)

    esperado = round(float(caja.monto_inicial or 0) + ventas_efectivo + netos_movimientos, 2)
    diferencia = round(monto_real - esperado, 2)

    caja.fecha_cierre = datetime.now()
    caja.monto_esperado = esperado
    caja.monto_real = monto_real
    caja.diferencia = diferencia
    caja.estado = 'cerrada'
    caja.observaciones = request.form.get('observaciones') or (
        'Arqueo con diferencia' if diferencia != 0 else None
    )

    db.session.add(MovimientoCaja(
        caja_id=caja.id, tipo='CIERRE', monto=monto_real,
        concepto='Arqueo de caja', creado_en=datetime.now()
    ))
    db.session.commit()

    return jsonify({
        'success': True,
        'caja_id': caja.id,
        'ventas_efectivo': round(ventas_efectivo, 2),
        'monto_esperado': esperado,
        'monto_real': monto_real,
        'diferencia': diferencia,
        'cuadra': diferencia == 0
    })


@caja_bp.route('/api/caja/estado')
@_login_requerido
def api_estado_caja():
    usuario_id = session['usuario_id']
    caja = _caja_abierta_de(usuario_id)
    if not caja:
        return jsonify({'abierta': False})

    ventas_efectivo = float(db.session.execute(text("""
        SELECT COALESCE(SUM(total_venta),0)
        FROM ventas
        WHERE vendedor_id = :uid AND metodo_pago = 'efectivo' AND estado = 1
          AND fecha_venta >= :apertura
    """), {'uid': usuario_id, 'apertura': caja.fecha_apertura}).scalar() or 0)

    return jsonify({
        'abierta': True,
        'caja_id': caja.id,
        'monto_inicial': float(caja.monto_inicial or 0),
        'ventas_efectivo': round(ventas_efectivo, 2),
        'esperado': round(float(caja.monto_inicial or 0) + ventas_efectivo, 2),
        'fecha_apertura': caja.fecha_apertura.strftime('%d/%m/%Y %H:%M')
    })


@caja_bp.route('/api/caja/resumen')
@_login_requerido
def api_resumen_caja():
    """Resumen que alimenta el KPI 7 en el tablero de indicadores."""
    fila = db.session.execute(text("""
        SELECT COUNT(*) AS cierres,
               SUM(CASE WHEN diferencia = 0 THEN 1 ELSE 0 END) AS exactos,
               SUM(CASE WHEN diferencia <> 0 THEN 1 ELSE 0 END) AS con_diferencia,
               COALESCE(ABS(SUM(diferencia)),0) AS descuadre
        FROM cajas
        WHERE estado = 'cerrada' AND fecha_cierre IS NOT NULL
    """)).fetchone()

    cierres = int(fila.cierres or 0)
    exactos = int(fila.exactos or 0)

    return jsonify({
        'precision': round(exactos / cierres * 100, 2) if cierres else 0.0,
        'cierres': cierres,
        'exactos': exactos,
        'con_diferencia': int(fila.con_diferencia or 0),
        'descuadre': round(float(fila.descuadre or 0), 2)
    })
