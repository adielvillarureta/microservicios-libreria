# Comercial/routes/catalogo.py
from flask import Blueprint, render_template, request, jsonify, url_for
from extensions import db
from models.clientes import Cliente
import requests
import os

catalogo_bp = Blueprint('catalogo', __name__, template_folder='../templates')
INVENTARIO_URL = os.getenv('INVENTARIO_URL', 'http://localhost:8002')

@catalogo_bp.route("/")
def catalogo_cliente():
    """Catálogo de productos para clientes"""
    try:
        categorias_response = requests.get(f"{INVENTARIO_URL}/api/categorias", timeout=5)
        categorias = categorias_response.json() if categorias_response.status_code == 200 else []
        productos_response = requests.get(f"{INVENTARIO_URL}/api/productos/catalogo", timeout=5)
        productos = productos_response.json() if productos_response.status_code == 200 else []
        
        return render_template("catalogo_cliente.html", 
                              categorias=categorias,
                              productos=productos)
    except Exception as e:
        print(f"❌ Error en catálogo: {e}")
        return render_template("catalogo_cliente.html", categorias=[], productos=[])

@catalogo_bp.route("/api/productos")
def api_productos():
    """API para obtener productos del catálogo"""
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
        else:
            return jsonify({"error": "Error al obtener productos"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500