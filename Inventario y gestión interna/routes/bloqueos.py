from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, session, url_for

from extensions import db
from models.bloqueo import Bloqueo
from services.permisos import ROLES_ADMIN, solo_admin

bloqueos_bp = Blueprint('bloqueos', __name__)


@bloqueos_bp.route('/bloqueos')
@solo_admin
def listar_bloqueos():
    Bloqueo.refrescar_expirados()
    bloqueos = Bloqueo.query.order_by(Bloqueo.creado_en.desc()).all()
    return render_template('bloqueos.html', bloqueos=bloqueos)


@bloqueos_bp.route('/api/bloqueos')
def api_listar_bloqueos():
    if session.get('rol') not in ROLES_ADMIN:
        return jsonify({'error': 'No autorizado'}), 403
    Bloqueo.refrescar_expirados()
    bloqueos = Bloqueo.query.order_by(Bloqueo.creado_en.desc()).all()
    return jsonify([b.to_dict() for b in bloqueos])


@bloqueos_bp.route('/bloqueos/<int:id>/liberar', methods=['POST'])
@solo_admin
def liberar_bloqueo(id):
    bloqueo = db.get_or_404(Bloqueo, id)
    ip = bloqueo.ip
    db.session.delete(bloqueo)
    db.session.commit()
    flash(f'Bloqueo de la IP {ip} liberado', 'success')
    return redirect(url_for('bloqueos.listar_bloqueos'))


@bloqueos_bp.route('/bloqueos/limpiar', methods=['POST'])
@solo_admin
def limpiar_bloqueos():
    bloqueos = Bloqueo.query.filter(
        Bloqueo.activo.is_(False) |
        (Bloqueo.expira_en.isnot(None) & (Bloqueo.expira_en <= datetime.utcnow()))
    ).all()
    for bloqueo in bloqueos:
        db.session.delete(bloqueo)
    db.session.commit()
    flash(f'{len(bloqueos)} registro(s) de bloqueo limpiado(s)', 'success')
    return redirect(url_for('bloqueos.listar_bloqueos'))
