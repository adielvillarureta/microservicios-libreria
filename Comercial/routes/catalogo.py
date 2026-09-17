import os

import requests
from flask import Blueprint, jsonify, render_template, request

catalogo_bp = Blueprint('catalogo', __name__)

INVENTARIO_URL = os.getenv('INVENTARIO_API_URL') or os.getenv('INVENTARIO_URL', 'http://localhost:5001')


@catalogo_bp.route("/catalogo")
def catalogo_cliente():
    try:
        categorias_response = requests.get(f"{INVENTARIO_URL}/api/categorias", timeout=5)
        categorias = categorias_response.json() if categorias_response.status_code == 200 else []

        productos_response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", timeout=5)
        productos = productos_response.json() if productos_response.status_code == 200 else []

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
            return jsonify(response.json())
        return jsonify({"error": "Error al obtener productos"}), 500

    except requests.exceptions.ConnectionError:
        return jsonify({"error": "El microservicio de Inventario no está disponible"}), 503
    except Exception as e:
        return jsonify({"error": str(e)}), 500