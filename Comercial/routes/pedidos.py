from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from extensions import db  # ✅ CAMBIADO
from models.pedido import Pedido
from models.detallePedido import DetallePedido
from models.cliente import Cliente