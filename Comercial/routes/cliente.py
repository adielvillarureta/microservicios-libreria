import glob
import os

import jwt
import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from datetime import datetime, timedelta
from sqlalchemy import text

from extensions import db, bcrypt
from models.clientes import Cliente
from models.intentos_login import IntentosLogin
from utils import (
    login_required_cliente, obtener_ip_cliente, registrar_intento_fallido,
    verificar_bloqueo_ip, verificar_bloqueo_email, limpiar_bloqueos_expirados,
    limpiar_intentos_exitosos, generar_token_recuperacion
)

cliente_bp = Blueprint('cliente', __name__)

EXTENSIONES_FOTO = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID', '')
FACEBOOK_APP_ID = os.getenv('FACEBOOK_APP_ID', '')
FACEBOOK_APP_SECRET = os.getenv('FACEBOOK_APP_SECRET', '')
_GOOGLE_JWKS_URL = 'https://www.googleapis.com/oauth2/v3/certs'


def _config_social():
    return {
        'google_client_id': GOOGLE_CLIENT_ID,
        'facebook_app_id': FACEBOOK_APP_ID
    }


def _obtener_o_crear_cliente_social(info):
    cliente = Cliente.query.filter_by(email=info['email']).first()
    creado = False
    if not cliente:
        cliente = Cliente(
            nombres=info['nombres'] or 'Cliente',
            apellidos=info['apellidos'] or '',
            email=info['email'],
            clave=os.urandom(24).hex()
        )
        db.session.add(cliente)
        db.session.commit()
        creado = True
    return cliente, creado


def _iniciar_sesion_social(cliente):
    limpiar_intentos_exitosos(cliente.email, obtener_ip_cliente())
    db.session.execute(text("""
        UPDATE bloqueos
        SET estado = 0, fecha_desbloqueo = CURRENT_TIMESTAMP
        WHERE cliente_id = :cliente_id
        AND tipo_usuario = 'cliente'
        AND permanente = 0
        AND estado = 1
    """), {"cliente_id": cliente.id})
    db.session.commit()

    session["cliente_id"] = cliente.id
    session["cliente_nombres"] = cliente.nombres
    session["cliente_apellidos"] = cliente.apellidos
    session["cliente_email"] = cliente.email
    session["cliente_telefono"] = cliente.telefono
    session["cliente_direccion"] = cliente.direccion
    session["cliente_dni"] = cliente.dni


def _verificar_token_google(credential):
    if not GOOGLE_CLIENT_ID:
        return None, 'El inicio de sesión con Google no está configurado'
    try:
        jwks = requests.get(_GOOGLE_JWKS_URL, timeout=10).json()
        payload = jwt.decode(credential, jwks, algorithms=['RS256'], audience=GOOGLE_CLIENT_ID)
        if payload.get('iss') not in ('accounts.google.com', 'https://accounts.google.com'):
            return None, 'Emisor de token no válido'
        email = (payload.get('email') or '').strip().lower()
        if not email:
            return None, 'Google no proporcionó tu correo electrónico'
        nombre = payload.get('given_name') or email.split('@')[0]
        apellido = payload.get('family_name') or ''
        return {'email': email, 'nombres': nombre, 'apellidos': apellido}, None
    except jwt.ExpiredSignatureError:
        return None, 'La sesión de Google ha expirado, intenta nuevamente'
    except Exception:
        return None, 'No se pudo validar tu cuenta de Google'


def _verificar_token_facebook(access_token, user_id):
    if not FACEBOOK_APP_ID:
        return None, 'El inicio de sesión con Facebook no está configurado'
    try:
        if FACEBOOK_APP_SECRET:
            debug = requests.get('https://graph.facebook.com/debug_token', params={
                'input_token': access_token,
                'access_token': f'{FACEBOOK_APP_ID}|{FACEBOOK_APP_SECRET}'
            }, timeout=10).json()
            data = debug.get('data', {})
            if not data.get('is_valid'):
                return None, 'Token de Facebook no válido'
            if user_id and str(data.get('user_id')) != str(user_id):
                return None, 'El token no corresponde al usuario'

        perfil = requests.get('https://graph.facebook.com/me', params={
            'fields': 'id,name,email',
            'access_token': access_token
        }, timeout=10).json()
        email = (perfil.get('email') or '').strip().lower()
        if not email:
            return None, 'Facebook no compartió tu correo electrónico'
        nombre = (perfil.get('name') or '').strip()
        partes = nombre.split(' ')
        nombres = partes[0] if partes else email.split('@')[0]
        apellidos = ' '.join(partes[1:]) if len(partes) > 1 else ''
        return {'email': email, 'nombres': nombres, 'apellidos': apellidos}, None
    except Exception:
        return None, 'No se pudo validar tu cuenta de Facebook'


def _template_data():
    return {
        "bloqueo_permanente": None,
        "bloqueo_temporal": False,
        "minutos_restantes": 0,
        "intentos_restantes": None,
        "intentos_totales": None,
        "intentos_para_permanente": None,
        **_config_social()
    }


def _bloqueo_permanente(cliente):
    return db.session.execute(text("""
        SELECT id, motivo, permanente, fecha_bloqueo
        FROM bloqueos
        WHERE cliente_id = :cliente_id
        AND tipo_usuario = 'cliente'
        AND estado = 1
        AND permanente = 1
    """), {"cliente_id": cliente.id}).mappings().first()


def _flash_bloqueo_permanente(bloqueo):
    flash("Cuenta bloqueada permanentemente", "danger")
    flash(f"Motivo: {bloqueo['motivo'] or '5 intentos fallidos de login'}", "warning")
    if bloqueo.get('fecha_bloqueo'):
        flash(f"Fecha de bloqueo: {bloqueo['fecha_bloqueo'].strftime('%d/%m/%Y %H:%M')}", "info")
    flash("Contacta al administrador para desbloquear tu cuenta.", "warning")
    return {
        "motivo": bloqueo['motivo'] or "Has excedido el número máximo de intentos permitidos."
    }


def _flash_bloqueo_temporal(minutos):
    flash("Cuenta bloqueada temporalmente", "danger")
    flash(f"Espera {minutos} minutos para volver a intentar.", "warning")


@cliente_bp.route('/login-cliente', methods=['GET', 'POST'])
def login_cliente():
    ip_cliente = obtener_ip_cliente()
    limpiar_bloqueos_expirados()
    template_data = _template_data()

    if verificar_bloqueo_ip(ip_cliente):
        flash("Acceso denegado: esta IP ha sido bloqueada. Espera 10 minutos.", "danger")
        return render_template("login_cliente.html", **template_data)

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        clave = request.form.get("clave", "")

        if not email or not clave:
            flash("Ingresa email y contraseña", "danger")
            return render_template("login_cliente.html", **template_data)

        if verificar_bloqueo_email(email):
            cliente_tmp = Cliente.query.filter_by(email=email).first()
            if cliente_tmp:
                bloqueo_permanente = _bloqueo_permanente(cliente_tmp)
                if bloqueo_permanente:
                    template_data["bloqueo_permanente"] = _flash_bloqueo_permanente(bloqueo_permanente)
                else:
                    registro = IntentosLogin.query.filter_by(email=email).first()
                    if registro and registro.email_bloqueado:
                        minutos = (registro.email_bloqueado - datetime.now()).seconds // 60
                        _flash_bloqueo_temporal(minutos)
                        template_data["bloqueo_temporal"] = True
                        template_data["minutos_restantes"] = minutos
            else:
                flash("Cuenta bloqueada", "danger")
                flash("Espera 10 minutos para volver a intentar.", "warning")
            return render_template("login_cliente.html", **template_data)

        if verificar_bloqueo_ip(ip_cliente):
            flash("Acceso denegado: esta IP ha sido bloqueada. Espera 10 minutos.", "danger")
            return render_template("login_cliente.html", **template_data)

        cliente = Cliente.query.filter_by(email=email).first()

        if not cliente:
            resultado = registrar_intento_fallido(email, ip_cliente, es_cliente=True)
            flash("Este correo no está registrado. Crea una cuenta nueva.", "warning")
            flash("Haz clic en 'Registrarme' para crear una cuenta.", "info")
            if resultado.get("bloqueado") and resultado["tipo"] == "ip":
                flash(resultado["mensaje"], "danger")
                return redirect(url_for("cliente.login_cliente"))
            return render_template("login_cliente.html", **template_data)

        bloqueo_permanente = _bloqueo_permanente(cliente)
        if bloqueo_permanente:
            template_data["bloqueo_permanente"] = _flash_bloqueo_permanente(bloqueo_permanente)
            return render_template("login_cliente.html", **template_data)

        registro_intentos = IntentosLogin.query.filter_by(email=email).first()
        if registro_intentos and registro_intentos.email_bloqueado and registro_intentos.email_bloqueado > datetime.now():
            minutos = (registro_intentos.email_bloqueado - datetime.now()).seconds // 60
            _flash_bloqueo_temporal(minutos)
            template_data["bloqueo_temporal"] = True
            template_data["minutos_restantes"] = minutos
            return render_template("login_cliente.html", **template_data)

        if bcrypt.check_password_hash(cliente.clave, clave):
            limpiar_intentos_exitosos(email, ip_cliente)

            db.session.execute(text("""
                UPDATE bloqueos
                SET estado = 0, fecha_desbloqueo = CURRENT_TIMESTAMP
                WHERE cliente_id = :cliente_id
                AND tipo_usuario = 'cliente'
                AND permanente = 0
                AND estado = 1
            """), {"cliente_id": cliente.id})
            db.session.commit()

            session["cliente_id"] = cliente.id
            session["cliente_nombres"] = cliente.nombres
            session["cliente_apellidos"] = cliente.apellidos
            session["cliente_email"] = cliente.email
            session["cliente_telefono"] = cliente.telefono
            session["cliente_direccion"] = cliente.direccion
            session["cliente_dni"] = cliente.dni
            flash(f"¡Bienvenido {cliente.nombres}!", "success")
            return redirect("/catalogo")

        resultado = registrar_intento_fallido(email, ip_cliente, es_cliente=True)
        template_data["intentos_restantes"] = resultado.get("intentos_restantes", 0)
        template_data["intentos_totales"] = resultado.get("intentos_totales", 0)
        template_data["intentos_para_permanente"] = resultado.get("intentos_para_bloqueo_permanente", 5)

        if resultado.get("bloqueado"):
            if resultado["tipo"] == "permanente":
                flash("Cuenta bloqueada permanentemente", "danger")
                flash("Motivo: 5 intentos fallidos de login", "warning")
                flash("Contacta al administrador para desbloquear tu cuenta.", "warning")
                template_data["bloqueo_permanente"] = {
                    "motivo": "Has excedido el número máximo de intentos permitidos (5 fallos)."
                }
            elif resultado["tipo"] == "email":
                flash(resultado["mensaje"], "danger")
                registro = IntentosLogin.query.filter_by(email=email).first()
                if registro and registro.email_bloqueado:
                    minutos = (registro.email_bloqueado - datetime.now()).seconds // 60
                    template_data["bloqueo_temporal"] = True
                    template_data["minutos_restantes"] = minutos
            elif resultado["tipo"] == "ip":
                flash(resultado["mensaje"], "danger")
                flash("Ningún cliente podrá iniciar sesión desde esta IP durante 10 minutos.", "warning")
            else:
                flash(resultado["mensaje"], "danger")
        else:
            intentos_restantes = resultado.get("intentos_restantes", 0)
            intentos_totales = resultado.get("intentos_totales", 0)
            if intentos_restantes > 0 and intentos_restantes != 999:
                if intentos_restantes <= 1:
                    flash(f"Contraseña incorrecta. Te queda {intentos_restantes} intento para bloqueo temporal.", "danger")
                    flash(f"Si fallas 2 veces más (total {intentos_totales + 2} de 5), tu cuenta será bloqueada permanentemente.", "warning")
                else:
                    flash(f"Contraseña incorrecta. Te quedan {intentos_restantes} intentos para bloqueo temporal.", "danger")
                    flash(f"Intentos totales: {intentos_totales} de 5. Si llegas a 5, tu cuenta será bloqueada permanentemente.", "info")
            else:
                if intentos_totales >= 4:
                    flash("Último intento. Contraseña incorrecta. Si fallas una vez más (5 de 5), tu cuenta será bloqueada permanentemente.", "danger")
                else:
                    flash("Contraseña incorrecta. El próximo intento (3 de 3) bloqueará la cuenta temporalmente por 10 minutos.", "warning")
                    flash(f"Intentos totales: {intentos_totales} de 5. Con 5 fallos, bloqueo permanente.", "info")
        return render_template("login_cliente.html", **template_data)

    email_cookie = request.cookies.get('email_actual')
    if email_cookie:
        registro = IntentosLogin.query.filter_by(email=email_cookie).first()
        if registro and not registro.email_bloqueado:
            template_data["intentos_restantes"] = 3 - registro.intentos
            template_data["intentos_totales"] = registro.intentos_totales
            template_data["intentos_para_permanente"] = 5 - registro.intentos_totales

    return render_template("login_cliente.html", **template_data)


@cliente_bp.route('/registro-cliente', methods=['GET', 'POST'])
def registro_cliente():
    if request.method == "POST":
        clave = request.form.get("clave")
        confirmar = request.form.get("confirmar_clave")
        if clave != confirmar:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("cliente.registro_cliente"))

        try:
            existe = Cliente.query.filter_by(email=request.form["email"]).first()
            if existe:
                flash("El correo ya está registrado", "danger")
                return redirect(url_for("cliente.registro_cliente"))

            cliente = Cliente(
                dni=request.form.get("dni"),
                nombres=request.form["nombres"],
                apellidos=request.form["apellidos"],
                email=request.form["email"],
                telefono=request.form.get("telefono"),
                direccion=request.form.get("direccion"),
                clave=bcrypt.generate_password_hash(request.form["clave"]).decode("utf-8"),
            )
            db.session.add(cliente)
            db.session.commit()
            flash("Registro exitoso", "success")
            return redirect(url_for("cliente.login_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")
            return render_template("registro_cliente.html", **_config_social())

    return render_template("registro_cliente.html", **_config_social())


@cliente_bp.route('/logout-cliente')
def logout_cliente():
    session.clear()
    flash("Sesión cerrada", "success")
    return redirect("/catalogo")


@cliente_bp.route('/cliente/perfil')
@login_required_cliente
def cliente_perfil():
    cliente = Cliente.query.get(session["cliente_id"])
    if not cliente:
        flash("Cliente no encontrado", "danger")
        return redirect(url_for("cliente.logout_cliente"))
    return render_template("cliente_perfil.html", cliente=cliente)


@cliente_bp.route('/cliente/foto-perfil', methods=['POST'])
@login_required_cliente
def cliente_foto_perfil():
    archivo = request.files.get('foto')
    if not archivo or archivo.filename == '':
        flash("Selecciona una imagen", "warning")
        return redirect(url_for("cliente.cliente_perfil"))

    if '.' not in archivo.filename or archivo.filename.rsplit('.', 1)[-1].lower() not in EXTENSIONES_FOTO:
        flash("Formato no permitido (usa PNG, JPG, JPEG, GIF o WEBP)", "danger")
        return redirect(url_for("cliente.cliente_perfil"))

    extension = archivo.filename.rsplit('.', 1)[-1].lower()
    carpeta = os.path.join(current_app.root_path, 'static', 'img', 'perfiles')
    os.makedirs(carpeta, exist_ok=True)

    for anterior in glob.glob(os.path.join(carpeta, f'cliente_{session["cliente_id"]}.*')):
        try:
            os.remove(anterior)
        except OSError:
            pass

    archivo.save(os.path.join(carpeta, f'cliente_{session["cliente_id"]}.{extension}'))
    flash("Foto de perfil actualizada", "success")
    return redirect(url_for("cliente.cliente_perfil"))


@cliente_bp.route('/cliente/actualizar-perfil', methods=['POST'])
@login_required_cliente
def cliente_actualizar_perfil():
    cliente = Cliente.query.get(session["cliente_id"])
    if not cliente:
        flash("Sesión inválida. Inicia sesión de nuevo.", "danger")
        return redirect(url_for("cliente.login_cliente"))

    try:
        cliente.nombres = request.form.get("nombres")
        cliente.apellidos = request.form.get("apellidos")
        cliente.telefono = request.form.get("telefono")
        cliente.direccion = request.form.get("direccion")
        cliente.dni = request.form.get("dni")

        nuevo_email = request.form.get("email")
        if nuevo_email and nuevo_email != cliente.email:
            existe = Cliente.query.filter_by(email=nuevo_email).first()
            if existe:
                flash("El correo ya está registrado por otro usuario", "danger")
                return redirect(url_for("cliente.cliente_perfil"))
            cliente.email = nuevo_email
            session["cliente_email"] = nuevo_email

        db.session.commit()

        session["cliente_nombres"] = cliente.nombres
        session["cliente_apellidos"] = cliente.apellidos
        session["cliente_telefono"] = cliente.telefono
        session["cliente_direccion"] = cliente.direccion
        session["cliente_dni"] = cliente.dni

        flash("Perfil actualizado correctamente", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al actualizar: {str(e)}", "danger")

    return redirect(url_for("cliente.cliente_perfil"))


@cliente_bp.route('/cliente/cambiar-contrasena', methods=['GET', 'POST'])
@login_required_cliente
def cliente_cambiar_contrasena():
    if request.method == "POST":
        contrasena_actual = request.form.get("contrasena_actual")
        nueva_contrasena = request.form.get("nueva_contrasena")
        confirmar_contrasena = request.form.get("confirmar_contrasena")

        if not contrasena_actual or not nueva_contrasena or not confirmar_contrasena:
            flash("Todos los campos son obligatorios", "danger")
            return redirect(url_for("cliente.cliente_cambiar_contrasena"))

        if nueva_contrasena != confirmar_contrasena:
            flash("Las contraseñas no coinciden", "danger")
            return redirect(url_for("cliente.cliente_cambiar_contrasena"))

        if len(nueva_contrasena) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "danger")
            return redirect(url_for("cliente.cliente_cambiar_contrasena"))

        cliente = Cliente.query.get(session["cliente_id"])

        if not bcrypt.check_password_hash(cliente.clave, contrasena_actual):
            flash("Contraseña actual incorrecta", "danger")
            return redirect(url_for("cliente.cliente_cambiar_contrasena"))

        try:
            nueva_clave_hash = bcrypt.generate_password_hash(nueva_contrasena).decode("utf-8")
            cliente.clave = nueva_clave_hash
            db.session.commit()
            flash("Contraseña actualizada", "success")
            return redirect("/catalogo")
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    return render_template("cliente_cambiar_contrasena.html")


@cliente_bp.route('/recuperar-contrasena', methods=['GET', 'POST'])
def recuperar_contrasena():
    if request.method == "POST":
        email = request.form.get("email")

        if not email:
            flash("Ingresa tu correo electrónico", "danger")
            return redirect(url_for("cliente.recuperar_contrasena"))

        cliente = Cliente.query.filter_by(email=email).first()

        if cliente:
            token = generar_token_recuperacion()
            cliente.token_recuperacion = token
            cliente.token_expiracion = datetime.now() + timedelta(hours=1)
            db.session.commit()

            enlace = url_for("cliente.resetear_contrasena", token=token, _external=True)
            flash(f"Enlace de recuperación: {enlace}", "info")
        else:
            flash("Si el correo está registrado, recibirás un enlace", "success")

        return redirect(url_for("cliente.login_cliente"))

    return render_template("recuperar_contrasena.html")


@cliente_bp.route('/resetear-contrasena/<token>', methods=['GET', 'POST'])
def resetear_contrasena(token):
    cliente = Cliente.query.filter_by(token_recuperacion=token).first()

    if not cliente:
        flash("Enlace inválido o ya utilizado", "danger")
        return redirect(url_for("cliente.login_cliente"))

    if cliente.token_expiracion < datetime.now():
        flash("El enlace ha expirado", "danger")
        return redirect(url_for("cliente.recuperar_contrasena"))

    if request.method == "POST":
        nueva = request.form.get("nueva")
        confirmar = request.form.get("confirmar")

        if not nueva or not confirmar:
            flash("Todos los campos son obligatorios", "danger")
            return render_template("resetear_contrasena.html", token=token)

        if nueva != confirmar:
            flash("Las contraseñas no coinciden", "danger")
            return render_template("resetear_contrasena.html", token=token)

        if len(nueva) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "danger")
            return render_template("resetear_contrasena.html", token=token)

        try:
            nueva_clave_hash = bcrypt.generate_password_hash(nueva).decode("utf-8")
            cliente.clave = nueva_clave_hash
            cliente.token_recuperacion = None
            cliente.token_expiracion = None
            db.session.commit()

            flash("Contraseña actualizada", "success")
            return redirect(url_for("cliente.login_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: {str(e)}", "danger")

    return render_template("resetear_contrasena.html", token=token)


@cliente_bp.route('/api/auth/google', methods=['POST'])
def auth_google():
    data = request.get_json(silent=True) or {}
    credential = data.get('credential')
    if not credential:
        return jsonify({'success': False, 'error': 'Falta el token de Google'}), 400

    info, error = _verificar_token_google(credential)
    if error:
        return jsonify({'success': False, 'error': error}), 401

    cliente, creado = _obtener_o_crear_cliente_social(info)
    _iniciar_sesion_social(cliente)
    return jsonify({'success': True, 'creado': creado, 'redirect': '/catalogo'})


@cliente_bp.route('/api/auth/facebook', methods=['POST'])
def auth_facebook():
    data = request.get_json(silent=True) or {}
    access_token = data.get('access_token')
    user_id = data.get('user_id')
    if not access_token:
        return jsonify({'success': False, 'error': 'Falta el token de Facebook'}), 400

    info, error = _verificar_token_facebook(access_token, user_id)
    if error:
        return jsonify({'success': False, 'error': error}), 401

    cliente, creado = _obtener_o_crear_cliente_social(info)
    _iniciar_sesion_social(cliente)
    return jsonify({'success': True, 'creado': creado, 'redirect': '/catalogo'})