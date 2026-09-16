from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from extensions import db
from models.usuarioSistema import UsuarioSistema
from services.authService import AuthService

usuario_bp = Blueprint('usuario', __name__)

@usuario_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        clave = request.form['clave']
        
        usuario = AuthService.authenticate(correo, clave)
        if usuario:
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombres
            session['rol'] = usuario.rol
            return redirect(url_for('index'))
        
        return render_template('baseInventario.html', error="Credenciales incorrectas")
    
    return render_template('baseInventario.html')

@usuario_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuario.login'))