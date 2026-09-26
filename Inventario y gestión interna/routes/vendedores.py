from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import generate_password_hash

from extensions import db
from models.usuarioSistema import UsuarioSistema
from services.permisos import solo_admin

vendedores_bp = Blueprint('vendedores', __name__)


def _datos_formulario():
    return {
        'nombres': (request.form.get('nombres') or '').strip(),
        'apellidos': (request.form.get('apellidos') or '').strip(),
        'correo': (request.form.get('correo') or '').strip().lower(),
        'clave': request.form.get('clave') or ''
    }


@vendedores_bp.route('/vendedores')
@solo_admin
def listar_vendedores():
    vendedores = UsuarioSistema.query.filter_by(rol='vendedor').order_by(
        UsuarioSistema.apellidos.asc()
    ).all()
    return render_template('vendedores.html', vendedores=vendedores, error=None)


@vendedores_bp.route('/vendedores/nuevo', methods=['GET', 'POST'])
@solo_admin
def nuevo_vendedor():
    vendedores = UsuarioSistema.query.filter_by(rol='vendedor').order_by(
        UsuarioSistema.apellidos.asc()
    ).all()

    if request.method == 'POST':
        datos = _datos_formulario()
        error = None
        if not datos['nombres'] or not datos['apellidos']:
            error = 'Nombres y apellidos son obligatorios'
        elif not datos['correo']:
            error = 'El correo es obligatorio'
        elif len(datos['clave']) < 6:
            error = 'La clave debe tener al menos 6 caracteres'
        elif UsuarioSistema.query.filter_by(correo=datos['correo']).first():
            error = 'Ya existe un usuario con ese correo'

        if error:
            return render_template('vendedores.html', vendedores=vendedores, error=error)

        vendedor = UsuarioSistema(
            nombres=datos['nombres'],
            apellidos=datos['apellidos'],
            correo=datos['correo'],
            clave=generate_password_hash(datos['clave']),
            rol='vendedor',
            activo=True
        )
        db.session.add(vendedor)
        db.session.commit()
        flash(f'Vendedor {datos["nombres"]} {datos["apellidos"]} registrado correctamente', 'success')
        return redirect(url_for('vendedores.listar_vendedores'))

    return render_template('vendedores.html', vendedores=vendedores, error=None)


@vendedores_bp.route('/vendedores/<int:id>/toggle', methods=['POST'])
@solo_admin
def toggle_vendedor(id):
    vendedor = db.get_or_404(UsuarioSistema, id)
    if vendedor.id == session.get('usuario_id'):
        flash('No puede desactivar su propia cuenta', 'warning')
        return redirect(url_for('vendedores.listar_vendedores'))
    vendedor.activo = not vendedor.activo
    db.session.commit()
    estado = 'activado' if vendedor.activo else 'desactivado'
    flash(f'Vendedor {vendedor.nombres} {vendedor.apellidos} {estado}', 'success')
    return redirect(url_for('vendedores.listar_vendedores'))
