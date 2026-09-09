# api-gateway/app.py
import os
import requests
from flask import Flask, request, Response, jsonify, session, redirect, url_for, flash
from flask_cors import CORS
from dotenv import load_dotenv
from functools import wraps
import time
import logging

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_gateway")
CORS(app)  


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

COMMERCIAL_URL = os.getenv("COMMERCIAL_URL", "http://localhost:8001")
INVENTARIO_URL = os.getenv("INVENTARIO_URL", "http://localhost:8002")

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session and "cliente_id" not in session:
            return redirect(url_for("proxy_login", path="login"))
        return f(*args, **kwargs)
    return decorated_function



def proxy_request(method, url, path, headers=None, data=None, json=None, cookies=None):
    """Función para reenviar requests a los microservicios"""
    try:
        full_url = f"{url}/{path}"
        

        clean_headers = {}
        if headers:
            for key, value in headers.items():
                if key.lower() not in ['host', 'content-length']:
                    clean_headers[key] = value
        

        response = requests.request(
            method=method,
            url=full_url,
            headers=clean_headers,
            data=data,
            json=json,
            cookies=cookies or request.cookies,
            timeout=30,
            allow_redirects=False
        )
        
        return response
        
    except requests.exceptions.Timeout:
        logger.error(f"Timeout en {full_url}")
        return None, {"error": "Timeout del servidor", "status": 504}
    except requests.exceptions.ConnectionError:
        logger.error(f"Error de conexión en {full_url}")
        return None, {"error": "Microservicio no disponible", "status": 503}
    except Exception as e:
        logger.error(f"Error en proxy: {str(e)}")
        return None, {"error": str(e), "status": 500}

def create_proxy_route(service_url, prefix=""):
    """Crea una ruta proxy dinámica"""
    def proxy_route(path="", **kwargs):

        full_path = path
        
 
        if full_path.endswith('/'):
            full_path = full_path[:-1]
        

        target_url = service_url
        if prefix:
            target_url = f"{service_url}/{prefix}"
        
        logger.info(f"Proxy: {request.method} {full_path} -> {target_url}/{full_path}")
        
        response = proxy_request(
            method=request.method,
            url=target_url,
            path=full_path,
            headers=dict(request.headers),
            data=request.get_data(),
            json=request.get_json(),
            cookies=request.cookies
        )
        
        if isinstance(response, tuple) and len(response) == 2:
            # Error
            error_data, status_code = response
            return jsonify(error_data), status_code
        

        resp = Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
        
       if 'Set-Cookie' in response.headers:
            resp.headers['Set-Cookie'] = response.headers['Set-Cookie']
        
        return resp
    
    return proxy_route


@app.route("/")
def home():
    """Página principal del gateway"""
    return jsonify({
        "name": "API Gateway - Librería Salesiana",
        "version": "1.0.0",
        "services": {
            "commercial": {
                "url": COMMERCIAL_URL,
                "status": check_service_health(COMMERCIAL_URL)
            },
            "inventario": {
                "url": INVENTARIO_URL,
                "status": check_service_health(INVENTARIO_URL)
            }
        },
        "endpoints": {
            "commercial": "/api/comercial/*",
            "inventario": "/api/inventario/*",
            "health": "/health"
        }
    })

def check_service_health(url):
    """Verifica si un microservicio está activo"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return "active" if response.status_code == 200 else "inactive"
    except:
        return "inactive"

@app.route("/health", methods=["GET"])
def health():
    """Health check del gateway"""
    commercial_status = check_service_health(COMMERCIAL_URL)
    inventario_status = check_service_health(INVENTARIO_URL)
    
    return jsonify({
        "gateway": "active",
        "services": {
            "commercial": commercial_status,
            "inventario": inventario_status
        },
        "timestamp": time.time()
    })

@app.route("/api/comercial/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_comercial(path):
    """Proxy para el microservicio comercial"""
    response = proxy_request(
        method=request.method,
        url=COMMERCIAL_URL,
        path=path,
        headers=dict(request.headers),
        data=request.get_data(),
        json=request.get_json(),
        cookies=request.cookies
    )
    
    if isinstance(response, tuple) and len(response) == 2:
        error_data, status_code = response
        return jsonify(error_data), status_code
    
    return Response(response.content, response.status_code, dict(response.headers))


@app.route("/api/inventario/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy_inventario(path):
    """Proxy para el microservicio de inventario"""
    response = proxy_request(
        method=request.method,
        url=INVENTARIO_URL,
        path=path,
        headers=dict(request.headers),
        data=request.get_data(),
        json=request.get_json(),
        cookies=request.cookies
    )
    
    if isinstance(response, tuple) and len(response) == 2:
        error_data, status_code = response
        return jsonify(error_data), status_code
    
    return Response(response.content, response.status_code, dict(response.headers))



@app.route("/login", methods=["GET", "POST"])
def proxy_login():
    """Redirige al login según el tipo de usuario"""
    if request.method == "GET":
        return render_template("login_gateway.html")
    else:
        tipo = request.form.get("tipo", "cliente")
        
        if tipo == "cliente":
            return redirect(url_for("proxy_comercial", path="login-cliente"))
        else:
            return redirect(url_for("proxy_inventario", path="login"))



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)