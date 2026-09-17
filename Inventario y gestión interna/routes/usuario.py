from flask import Blueprint, render_template, request, redirect, url_for, session

from services.authService import AuthService

usuario_bp = Blueprint('usuario', __name__)


@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        clave = request.form.get('clave')

        usuario = AuthService.authenticate(correo, clave)
        if usuario:
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombres
            session['rol'] = usuario.rol
            return redirect(url_for('dashboard'))

        return render_template('login.html', error="Credenciales incorrectas")

    return render_template('login.html')


@usuario_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))