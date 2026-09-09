# Comercial/routes/__init__.py
from .catalogo import catalogo_bp
from .clientes import clientes_bp
from .pedidos import pedidos_bp
from .ventas import ventas_bp

__all__ = ['catalogo_bp', 'clientes_bp', 'pedidos_bp', 'ventas_bp']