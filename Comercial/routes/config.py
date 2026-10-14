import os

from flask import Blueprint, jsonify, render_template

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
