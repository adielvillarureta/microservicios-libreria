import os

import requests
from urllib.parse import urlsplit
from flask import Blueprint, jsonify, render_template, make_response, request

catalogo_bp = Blueprint('catalogo', __name__)

INVENTARIO_URL = os.getenv('INVENTARIO_API_URL') or os.getenv('INVENTARIO_URL', 'http://localhost:5000')
INVENTARIO_PUBLIC_URL = os.getenv('INVENTARIO_PUBLIC_URL', 'http://localhost:5000')


def _publicar_imagen(producto):
    if not isinstance(producto, dict):
        return producto
    url = producto.get('imagen_url')
    if not url and producto.get('imagen'):
        url = '/static/img/productos/' + str(producto['imagen'])
    if not url:
        return producto

    url_text = str(url)
    parsed = urlsplit(url_text)
    ruta_relativa = parsed.path if parsed.scheme in ('http', 'https') else url_text
    if not ruta_relativa.startswith('/'):
        ruta_relativa = '/' + ruta_relativa
    ruta_relativa = ruta_relativa.lstrip('/')
    # Se sirve desde Comercial para evitar CORS/problemas de host/red.
    producto['imagen_url'] = '/img/inventario/' + ruta_relativa
    return producto


@catalogo_bp.route("/catalogo")
def catalogo_cliente():
    try:
        categorias_response = requests.get(f"{INVENTARIO_URL}/api/categorias", timeout=5)
        categorias = categorias_response.json() if categorias_response.status_code == 200 else []

        productos_response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", timeout=5)
        productos = productos_response.json() if productos_response.status_code == 200 else []
        productos = [_publicar_imagen(p) for p in (productos or [])]

        return render_template("catalogo_cliente.html", categorias=categorias, productos=productos)
    except Exception:
        return render_template("catalogo_cliente.html", categorias=[], productos=[])


@catalogo_bp.route("/api/productos/<int:producto_id>/stock")
def api_producto_stock(producto_id):
    try:
        response = requests.get(f"{INVENTARIO_URL}/productos/{producto_id}/stock", timeout=5)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({"error": "Producto no encontrado"}), 404
    except requests.exceptions.ConnectionError:
        return jsonify({"error": "El microservicio de Inventario no está disponible"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@catalogo_bp.route("/api/productos")
@catalogo_bp.route("/api/productos/catalogo")
def api_productos():
    try:
        q = request.args.get('q', '')
        categoria_id = request.args.get('categoria', type=int)

        params = {}
        if q:
            params['q'] = q
        if categoria_id:
            params['categoria'] = categoria_id

        response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", params=params, timeout=5)

        if response.status_code == 200:
            data = response.json() or []
            data = [_publicar_imagen(p) for p in data]
            return jsonify(data)
        return jsonify({"error": "Error al obtener productos"}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "El microservicio de Inventario no está disponible"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@catalogo_bp.route("/img/inventario/<path:filename>")
def imagen_inventario_proxima(filename):
    try:
        response = requests.get(f"{INVENTARIO_URL}/{filename}", timeout=10)
        if response.status_code != 200:
            return make_response("Not found", response.status_code)
        resp = make_response(response.content)
        resp.headers['Content-Type'] = response.headers.get('Content-Type', 'application/octet-stream')
        resp.headers['Cache-Control'] = 'public, max-age=86400'
        return resp
    except requests.exceptions.ConnectionError:
        return make_response("Inventario no disponible", 503)
    except Exception as e:
        return make_response(str(e), 500)