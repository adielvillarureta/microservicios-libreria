from flask import session, redirect, url_for, flash, request
from functools import wraps
from datetime import datetime, timedelta
from extensions import db
from models.intentos_login import IntentosLogin
from sqlalchemy import text
import secrets

# ============================================
# DECORADOR: Proteger rutas de cliente
# ============================================
def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cliente_id" not in session:
            flash("❌ Debes iniciar sesión para acceder", "warning")
            return redirect(url_for("cliente.login_cliente"))
        return f(*args, **kwargs)
    return decorated_function

# ============================================
# OBTENER IP DEL CLIENTE
# ============================================
def obtener_ip_cliente():
    if request.headers.get('X-Forwarded-For'):
        return request.headers.get('X-Forwarded-For').split(',')[0].strip()
    return request.remote_addr or "0.0.0.0"

# ============================================
# VERIFICAR BLOQUEOS
# ============================================
def verificar_bloqueo_ip(ip):
    try:
        resultado = db.session.execute(text("""
            SELECT id FROM bloqueos
            WHERE ip = :ip
            AND tipo_usuario = 'cliente'
            AND estado = 1
            AND permanente = 0
            AND fecha_desbloqueo > CURRENT_TIMESTAMP
        """), {"ip": ip}).first()
        return resultado is not None
    except Exception:
        return False

def verificar_bloqueo_email(email):
    try:
        registro = IntentosLogin.query.filter_by(email=email).first()
        if registro and registro.email_bloqueado:
            if registro.email_bloqueado > datetime.now():
                return True
        # Verificar bloqueo permanente en tabla bloqueos
        resultado = db.session.execute(text("""
            SELECT id FROM bloqueos
            WHERE email = :email
            AND tipo_usuario = 'cliente'
            AND estado = 1
            AND permanente = 1
        """), {"email": email}).first()
        return resultado is not None
    except Exception:
        return False

# ============================================
# LIMPIAR BLOQUEOS EXPIRADOS
# ============================================
def limpiar_bloqueos_expirados():
    try:
        db.session.execute(text("""
            UPDATE bloqueos
            SET estado = 0
            WHERE estado = 1
            AND permanente = 0
            AND fecha_desbloqueo IS NOT NULL
            AND fecha_desbloqueo < CURRENT_TIMESTAMP
        """))
        db.session.commit()

        # Limpiar bloqueos de email expirados
        registros = IntentosLogin.query.filter(
            IntentosLogin.email_bloqueado.isnot(None),
            IntentosLogin.email_bloqueado < datetime.now()
        ).all()
        for r in registros:
            r.email_bloqueado = None
            r.intentos = 0
        db.session.commit()
    except Exception:
        db.session.rollback()

# ============================================
# REGISTRAR INTENTO FALLIDO
# ============================================
def registrar_intento_fallido(email, ip, es_cliente=True):
    resultado = {
        "bloqueado": False,
        "tipo": None,
        "mensaje": "",
        "intentos_restantes": 3,
        "intentos_totales": 0,
        "intentos_para_bloqueo_permanente": 5
    }
    try:
        registro = IntentosLogin.query.filter_by(email=email).first()
        if not registro:
            registro = IntentosLogin(email=email, ip=ip, intentos=0, intentos_totales=0)
            db.session.add(registro)
            db.session.commit()

        registro.intentos += 1
        registro.intentos_totales += 1
        registro.ip = ip
        registro.fecha_ultimo_intento = datetime.now()

        # Bloqueo temporal por email (3 intentos)
        if registro.intentos >= 3:
            registro.email_bloqueado = datetime.now() + timedelta(minutes=10)
            resultado["bloqueado"] = True
            resultado["tipo"] = "email"
            resultado["mensaje"] = "Cuenta bloqueada temporalmente por 10 minutos."

        # Bloqueo permanente (5 intentos totales)
        if registro.intentos_totales >= 5:
            db.session.execute(text("""
                INSERT INTO bloqueos (email, ip, tipo_usuario, motivo, permanente, estado, fecha_bloqueo)
                VALUES (:email, :ip, 'cliente', '5 intentos fallidos de login', 1, 1, CURRENT_TIMESTAMP)
            """), {"email": email, "ip": ip})
            resultado["bloqueado"] = True
            resultado["tipo"] = "permanente"
            resultado["mensaje"] = "Cuenta bloqueada permanentemente."

        db.session.commit()

        resultado["intentos_restantes"] = max(0, 3 - registro.intentos)
        resultado["intentos_totales"] = registro.intentos_totales
        resultado["intentos_para_bloqueo_permanente"] = max(0, 5 - registro.intentos_totales)

    except Exception as e:
        db.session.rollback()
        resultado["mensaje"] = str(e)

    return resultado

# ============================================
# LIMPIAR INTENTOS EXITOSOS
# ============================================
def limpiar_intentos_exitosos(email, ip):
    try:
        registro = IntentosLogin.query.filter_by(email=email).first()
        if registro:
            registro.intentos = 0
            registro.intentos_totales = 0
            registro.email_bloqueado = None
            registro.ip_bloqueado = None
            db.session.commit()
    except Exception:
        db.session.rollback()

# ============================================
# GENERAR TOKEN DE RECUPERACIÓN
# ============================================
def generar_token_recuperacion():
    return secrets.token_urlsafe(32)