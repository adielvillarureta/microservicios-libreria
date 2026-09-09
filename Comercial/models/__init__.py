# Comercial/models/__init__.py
from .clientes import Cliente
from .ventas import Venta
from .pedidos import Pedido
from .detallePedido import DetallePedido

__all__ = ['Cliente', 'Venta', 'Pedido', 'DetallePedido']