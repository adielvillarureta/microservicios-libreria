import os

from flask import Blueprint, jsonify, render_template, request

from utils import login_required

config_bp = Blueprint("config_bp", __name__)


def _estado():
    return {
        "email": {
            "host": os.getenv("EMAIL_HOST", ""),
            "user": os.getenv("EMAIL_USER", ""),
            "configurado": bool(os.getenv("EMAIL_PASSWORD")),
        },
        "sms": {
            "provider": os.getenv("SMS_PROVIDER", "mock"),
            "twilio_sid": bool(os.getenv("TWILIO_ACCOUNT_SID")),
            "twilio_token": bool(os.getenv("TWILIO_AUTH_TOKEN")),
            "from": os.getenv("TWILIO_FROM", ""),
        },
        "tienda": {
            "telefono": os.getenv("SMS_STORE_PHONE", "(064) 247763"),
            "pais": os.getenv("SMS_COUNTRY_CODE", "+51"),
        },
    }


@config_bp.route("/configuracion", methods=["GET"])
@login_required
def configuracion():
    return render_template("configuracion.html", estado=_estado())


@config_bp.route("/api/config/estado", methods=["GET"])
def api_config_estado():
    return jsonify(_estado())


@config_bp.route("/api/config/test-sms", methods=["POST"])
def api_config_test_sms():
    data = request.get_json(silent=True) or {}
    telefono = (data.get("telefono") or "").strip()
    if not telefono:
        return jsonify({"success": False, "error": "Falta el teléfono"}), 400

    try:
        from datetime import datetime
        from services.smsService import enviar_boleta_sms
        resultado = enviar_boleta_sms(
            telefono=telefono,
            nombre=data.get("nombre") or "Cliente de prueba",
            tipo_comprobante="BOLETA",
            numero_comprobante=data.get("numero_comprobante") or f"TEST-{int(datetime.now().timestamp())}",
            total=float(data.get("total") or 10.0),
            pedido_id=0,
            venta_id=0,
            productos=["Cuaderno A4 100 hojas", "Lapicero Azul"],
        )
        return jsonify({"canal": "sms", "destino": telefono, "resultado": resultado}), 200
    except Exception as e:
        return jsonify({"canal": "sms", "destino": telefono, "resultado": {"success": False, "error": str(e)}}), 500


@config_bp.route("/api/config/test-email", methods=["POST"])
def api_config_test_email():
    data = request.get_json(silent=True) or {}
    correo = (data.get("correo") or "").strip()
    if not correo or "@" not in correo:
        return jsonify({"success": False, "error": "Correo inválido"}), 400

    try:
        from datetime import datetime
        from services.emailService import enviar_comprobante_email
        exito = enviar_comprobante_email(
            destinatario=correo,
            cliente_nombre=data.get("cliente") or "Cliente de prueba",
            tipo_comprobante="BOLETA",
            numero_comprobante=data.get("numero_comprobante") or f"TEST-{int(datetime.now().timestamp())}",
            fecha=datetime.now(),
            productos=[
                {"nombre": "Cuaderno A4 100 hojas", "cantidad": 1, "precio_unitario": 8.5, "total": 8.5},
                {"nombre": "Lapicero Azul", "cantidad": 2, "precio_unitario": 1.8, "total": 3.6},
            ],
            total_venta=float(data.get("total") or 12.1),
        )
        return jsonify({"canal": "email", "destino": correo, "enviado": bool(exito)}), 200
    except Exception as e:
        return jsonify({"canal": "email", "destino": correo, "enviado": False, "error": str(e)}), 500
