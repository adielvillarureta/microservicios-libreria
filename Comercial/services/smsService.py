"""Servicio de SMS para el microservicio Comercial.

Envia la boleta y el mensaje de atencion al cliente por SMS al numero
que el cliente deja en el checkout (no es obligatorio en el registro).

Configuracion (variables de entorno):
  SMS_PROVIDER          -> "twilio" (default) o "mock" (solo registra)
  TWILIO_ACCOUNT_SID    -> SID de la cuenta de Twilio
  TWILIO_AUTH_TOKEN     -> token de autenticacion
  TWILIO_FROM           -> numero remitente (formato E.164, ej. +1...)
  SMS_STORE_PHONE       -> telefono de atencion al cliente de la libreria
  SMS_COUNTRY_CODE      -> codigo de pais (default +51 para Peru)

Si las credenciales no estan configuradas, el servicio no rompe el pedido:
graba en log y devuelve success=False para que la UI lo informe.
"""
import os
import re

import requests

SMS_PROVIDER = os.getenv("SMS_PROVIDER", "twilio").strip().lower()
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
TWILIO_FROM = os.getenv("TWILIO_FROM", "").strip()
SMS_STORE_PHONE = os.getenv("SMS_STORE_PHONE", "(064) 247763").strip()
SMS_COUNTRY_CODE = os.getenv("SMS_COUNTRY_CODE", "+51").strip()


def normalizar_telefono(numero):
    """Deja el numero en formato E.164 para enviar por SMS."""
    if not numero:
        return None
    digits = re.sub(r"\D", "", str(numero))
    if not digits:
        return None
    if str(numero).strip().startswith("+"):
        return "+" + digits
    if len(digits) == 9 and digits.startswith("9"):
        return SMS_COUNTRY_CODE + digits
    if len(digits) >= 10 and not digits.startswith("0"):
        return "+" + digits
    return SMS_COUNTRY_CODE + digits[-9:]


def _enviar_twilio(destinatario, mensaje):
    if not (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM):
        print("[SMS] Twilio no configurado (faltan credenciales). SMS omitido.")
        return {"success": False, "provider": "twilio", "error": "no_credentials"}

    url = (
        f"https://api.twilio.com/2010-04-01/Accounts/"
        f"{TWILIO_ACCOUNT_SID}/Messages.json"
    )
    try:
        resp = requests.post(
            url,
            data={"From": TWILIO_FROM, "To": destinatario, "Body": mensaje},
            auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
            timeout=15,
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            print(f"[SMS] Enviado a {destinatario} (sid={data.get('sid')}).")
            return {"success": True, "provider": "twilio", "sid": data.get("sid")}
        try:
            err = resp.json().get("message", resp.text)
        except Exception:
            err = resp.text
        print(f"[SMS] Error Twilio ({resp.status_code}): {err}")
        return {"success": False, "provider": "twilio", "error": err}
    except Exception as e:
        print(f"[SMS] Excepcion enviando a {destinatario}: {e}")
        return {"success": False, "provider": "twilio", "error": str(e)}


def enviar_sms(numero, mensaje):
    """Punto de entrada unico para enviar un SMS."""
    destinatario = normalizar_telefono(numero)
    if not destinatario:
        print("[SMS] Numero invalido, SMS omitido.")
        return {"success": False, "provider": SMS_PROVIDER, "error": "invalid_phone"}

    if SMS_PROVIDER == "mock" or SMS_PROVIDER == "log":
        print(f"[SMS:mock] {destinatario}: {mensaje}")
        return {"success": True, "provider": "mock", "sid": "mock"}

    return _enviar_twilio(destinatario, mensaje)


def enviar_boleta_sms(telefono, nombre, tipo_comprobante, numero_comprobante,
                      total, pedido_id, venta_id=None, productos=None):
    """Envia por SMS la boleta/comprobante y el mensaje de atencion al cliente."""
    tipo = (tipo_comprobante or "boleta").upper()
    num = numero_comprobante or f"P{pedido_id:06d}"
    cliente = (nombre or "cliente").strip().title()
    lista = ", ".join((productos or []))
    if len(lista) > 70:
        lista = lista[:67] + "..."
    extra = f" Prod: {lista}." if lista else ""
    mensaje = (
        f"Libreria Salesiana: Hola {cliente}, tu {tipo} N {num} "
        f"por S/. {float(total):.2f} fue registrada.{extra} "
        f"Atencion: {SMS_STORE_PHONE}. Gracias."
    )
    return enviar_sms(telefono, mensaje)


def enviar_estado_pedido_sms(telefono, pedido_id, estado):
    """Aviso de actualizacion de estado del pedido por SMS (uso opcional)."""
    mensaje = (
        f"Libreria Salesiana: tu pedido #{pedido_id} cambio de estado a "
        f"\"{estado}\". Atencion: {SMS_STORE_PHONE}."
    )
    return enviar_sms(telefono, mensaje)
