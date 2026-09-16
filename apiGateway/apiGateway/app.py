# apiGateway/app.py
import os
import time
import logging
import requests
from datetime import datetime
from flask import Flask, request, Response, jsonify, session, redirect, url_for, render_template
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "clave_secreta_gateway")
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================
# URLs DE LOS MICROSERVICIOS
# ============================================
COMERCIAL_URL = os.getenv("COMERCIAL_URL", "http://localhost:5000")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://localhost:5001")


# ============================================
# FUNCIÓN PARA REENVIAR PETICIONES
# ============================================
def proxy_request(method, service_url, path, prefix=""):
    """Reenvía una petición al microservicio correspondiente"""
    # Construir URL final
    if prefix:
        full_url = f"{service_url}/{prefix}/{path}" if path else f"{service_url}/{prefix}"
    else:
        full_url = f"{service_url}/{path}" if path else service_url

    # Limpiar headers (quitar los que causan problemas)
    clean_headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ['host', 'content-length', 'connection']:
            clean_headers[key] = value

    logger.info(f"🔀 {method} /{path} → {full_url}")

    try:
        response = requests.request(
            method=method,
            url=full_url,
            headers=clean_headers,
            data=request.get_data(),
            cookies=request.cookies,
            params=request.args,
            allow_redirects=False,
            timeout=30
        )

        # Construir respuesta
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.headers.items()
                   if name.lower() not in excluded_headers]

        return Response(response.content, status=response.status_code, headers=headers)

    except requests.exceptions.Timeout:
        logger.error(f"⏱️ Timeout en {full_url}")
        return jsonify({"error": "Timeout del servidor", "url": full_url}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"🔌 Error de conexión en {full_url}")
        return jsonify({
            "error": "Microservicio no disponible",
            "url": full_url,
            "sugerencia": "Asegúrate de que el microservicio esté corriendo"
        }), 503
    except Exception as e:
        logger.error(f"❌ Error en proxy: {str(e)}")
        return jsonify({"error": str(e)}), 500


# ============================================
# HEALTH CHECK
# ============================================
def check_service_health(url):
    """Verifica si un microservicio está activo y mide la latencia (ms)"""
    try:
        start = time.time()
        response = requests.get(f"{url}/health", timeout=3)
        latency_ms = round((time.time() - start) * 1000)
        status = "active" if response.status_code == 200 else "inactive"
        return {"status": status, "latency_ms": latency_ms}
    except Exception:
        return {"status": "inactive", "latency_ms": None}


@app.route("/health")
def health():
    """Health check del gateway (JSON)"""
    comercial = check_service_health(COMERCIAL_URL)
    inventario = check_service_health(INVENTARIO_URL)
    return jsonify({
        "gateway": "active",
        "services": {
            "comercial": comercial,
            "inventario": inventario
        },
        "urls": {
            "comercial": COMERCIAL_URL,
            "inventario": INVENTARIO_URL
        },
        "timestamp": time.time()
    })


# ============================================
# PÁGINA PRINCIPAL (DASHBOARD HTML)
# ============================================
@app.route("/")
def home():
    """Dashboard visual del API Gateway"""
    comercial = check_service_health(COMERCIAL_URL)
    inventario = check_service_health(INVENTARIO_URL)
    return render_template(
        "dashboard.html",
        gateway="active",
        fecha_hora=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        comercial=comercial,
        inventario=inventario,
        comercial_url=COMERCIAL_URL,
        inventario_url=INVENTARIO_URL
    )


# ============================================
# RUTAS ESPECÍFICAS DEL GATEWAY
# ============================================
@app.route("/login", methods=["GET", "POST"])
def login_redirect():
    """Redirige al login según el tipo de usuario"""
    if request.method == "POST":
        tipo = request.form.get("tipo", "cliente")
        if tipo == "cliente":
            return redirect("/login-cliente")
        else:
            return redirect("/inventario/login")
    return redirect("/login-cliente")


# ============================================
# PROXY PARA COMERCIAL
# ============================================
@app.route("/api/comercial/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_comercial_api(path):
    return proxy_request(request.method, COMERCIAL_URL, path)


# ============================================
# PROXY PARA INVENTARIO
# ============================================
@app.route("/api/inventario/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_inventario_api(path):
    return proxy_request(request.method, INVENTARIO_URL, path)


# ============================================
# PROXY INTELIGENTE (catch-all)
# ============================================
@app.route("/inventario", defaults={"path": ""})
@app.route("/inventario/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_inventario(path):
    """Todo lo que empiece con /inventario va al microservicio Inventario"""
    return proxy_request(request.method, INVENTARIO_URL, path)


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_general(path):
    """Todo lo demás va a Comercial (por defecto)"""
    # Si la ruta ya fue capturada por otros decoradores, no llega aquí
    return proxy_request(request.method, COMERCIAL_URL, path)


# ============================================
# INICIO
# ============================================
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 API GATEWAY - Librería Salesiana")
    print("=" * 60)
    print(f"📡 Comercial:  {COMERCIAL_URL}")
    print(f"📡 Inventario: {INVENTARIO_URL}")
    print(f"🌐 Gateway corriendo en: http://localhost:8000")
    print("=" * 60)
    app.run(host="0.0.0.0", port=8000, debug=True)