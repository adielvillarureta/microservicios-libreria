import os
import time
import logging

import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, redirect, render_template, request
from flask_cors import CORS

load_dotenv()

app = Flask(__name__, static_folder=None)
app.secret_key = os.getenv("SECRET_KEY")
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMERCIAL_URL = os.getenv("COMERCIAL_URL", "http://localhost:5000")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://localhost:5001")


def proxy_request(method, service_url, path, public_prefix=""):
    if path:
        full_url = f"{service_url}/{path}"
    else:
        full_url = service_url

    clean_headers = {}
    for key, value in request.headers.items():
        if key.lower() not in ['host', 'content-length', 'connection']:
            clean_headers[key] = value

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

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for name, value in response.headers.items()
                   if name.lower() not in excluded_headers]

        if public_prefix and response.status_code in (301, 302, 303, 307, 308) and "Location" in response.headers:
            location = response.headers["Location"]
            if location.startswith(service_url):
                location = location[len(service_url):]
            if location == "/":
                location = public_prefix
            elif location.startswith("/") and not location.startswith("//") and not location.startswith(f"{public_prefix}/") and location != public_prefix:
                location = f"{public_prefix}{location}"
            if location != response.headers["Location"]:
                headers = [(n, v) for n, v in headers if n.lower() != "location"]
                headers.append(("Location", location))

        return Response(response.content, status=response.status_code, headers=headers)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout en {full_url}")
        return jsonify({"error": "Timeout del servidor", "url": full_url}), 504
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión en {full_url}")
        return jsonify({
            "error": "Microservicio no disponible",
            "url": full_url,
            "sugerencia": "Asegúrate de que el microservicio esté corriendo"
        }), 503
    except Exception as e:
        logger.error(f"Error en proxy: {str(e)}")
        return jsonify({"error": str(e)}), 500


def check_service_health(url):
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


@app.route("/")
def home():
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


@app.route("/login", methods=["GET", "POST"])
def login_redirect():
    if request.method == "POST":
        tipo = request.form.get("tipo", "cliente")
        if tipo == "cliente":
            return redirect("/login-cliente")
        return redirect("/inventario/login")
    return redirect("/login-cliente")


@app.route("/api/comercial/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_comercial_api(path):
    return proxy_request(request.method, COMERCIAL_URL, path, public_prefix="/api/comercial")


@app.route("/api/inventario/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_inventario_api(path):
    return proxy_request(request.method, INVENTARIO_URL, path, public_prefix="/api/inventario")


@app.route("/inventario", defaults={"path": ""})
@app.route("/inventario/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_inventario(path):
    return proxy_request(request.method, INVENTARIO_URL, path, public_prefix="/inventario")


@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_general(path):
    return proxy_request(request.method, COMERCIAL_URL, path)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=os.getenv("DEBUG", "false").lower() == "true")