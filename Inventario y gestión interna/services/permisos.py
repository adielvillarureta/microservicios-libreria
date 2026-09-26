from functools import wraps

from flask import flash, redirect, session, url_for

ROLES_ADMIN = ('administrador',)
ROLES_GESTION = ('administrador', 'supervisor')


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('usuario.login'))
        return func(*args, **kwargs)
    return wrapper


def solo_admin(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('usuario.login'))
        if session.get('rol') not in ROLES_ADMIN:
            flash('Esta seccion es exclusiva del administrador', 'danger')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return wrapper


def solo_gestion(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('usuario.login'))
        if session.get('rol') not in ROLES_GESTION:
            flash('Requiere rol de administrador o supervisor', 'warning')
            return redirect(url_for('dashboard'))
        return func(*args, **kwargs)
    return wrapper
