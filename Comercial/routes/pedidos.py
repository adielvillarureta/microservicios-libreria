from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from extensions import db
from models.detallePedido import DetallePedido
from models.clientes import Cliente
from models.pedidos import Pedido # <-- Asegúrate de tener este import si usas Pedido aquí
pedidos_bp = Blueprint('pedidos_bp', __name__)