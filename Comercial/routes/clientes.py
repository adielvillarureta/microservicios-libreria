# Comercial/routes/clientes.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db, bcrypt
from models.clientes import Cliente
from functools import wraps
from datetime import datetime, timedelta
import secrets

clientes_bp = Blueprint('clientes', __name__, template_folder='../templates')

def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cliente_id" not in session:
            flash("Debes iniciar sesión para continuar", "warning")
            return redirect(url_for("clientes.login_cliente"))
        return f(*args, **kwargs)
    return decorated_function

@clientes_bp.route("/registro", methods=["GET", "POST"])
def registro_cliente():
    """Registro de nuevos clientes"""
    if request.method == "POST":
        try:
            existe = Cliente.query.filter_by(correo=request.form["email"]).first()
            if existe:
                flash("❌ El correo ya está registrado", "danger")
                return redirect(url_for("clientes.registro_cliente"))
            
            cliente = Cliente(
                dni=request.form.get("dni"),
                nombres=request.form["nombres"],
                apellidos=request.form["apellidos"],
                correo=request.form["email"],
                telefono=request.form.get("telefono"),
                direccion=request.form.get("direccion"),
                clave=bcrypt.generate_password_hash(request.form["clave"]).decode("utf-8"),
            )
            db.session.add(cliente)
            db.session.commit()
            flash("✅ Registro exitoso", "success")
            return redirect(url_for("clientes.login_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error: {str(e)}", "danger")
    
    return render_template("registro_cliente.html")

@clientes_bp.route("/perfil")
@login_required_cliente
def perfil():
    cliente = Cliente.query.get(session["cliente_id"])
    return render_template("cliente_perfil.html", cliente=cliente)

@clientes_bp.route("/actualizar-perfil", methods=["POST"])
@login_required_cliente
def actualizar_perfil():
    try:
        cliente = Cliente.query.get(session["cliente_id"])
        cliente.nombres = request.form.get("nombres")
        cliente.apellidos = request.form.get("apellidos")
        cliente.telefono = request.form.get("telefono")
        cliente.direccion = request.form.get("direccion")
        
        nuevo_email = request.form.get("email")
        if nuevo_email and nuevo_email != cliente.correo:
            existe = Cliente.query.filter_by(correo=nuevo_email).first()
            if existe:
                flash("❌ El correo ya está registrado", "danger")
                return redirect(url_for("clientes.perfil"))
            cliente.correo = nuevo_email
            session["cliente_correo"] = nuevo_email
        
        db.session.commit()
        session["cliente_nombres"] = cliente.nombres
        session["cliente_apellidos"] = cliente.apellidos
        
        flash("✅ Perfil actualizado", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Error: {str(e)}", "danger")
    
    return redirect(url_for("clientes.perfil"))

@clientes_bp.route("/cambiar-contrasena", methods=["GET", "POST"])
@login_required_cliente
def cambiar_contrasena():
    if request.method == "POST":
        contrasena_actual = request.form.get("contrasena_actual")
        nueva_contrasena = request.form.get("nueva_contrasena")
        confirmar_contrasena = request.form.get("confirmar_contrasena")

        if not all([contrasena_actual, nueva_contrasena, confirmar_contrasena]):
            flash("❌ Todos los campos son obligatorios", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        if nueva_contrasena != confirmar_contrasena:
            flash("❌ Las contraseñas no coinciden", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        if len(nueva_contrasena) < 6:
            flash("❌ La contraseña debe tener al menos 6 caracteres", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        cliente = Cliente.query.get(session["cliente_id"])
        
        if not bcrypt.check_password_hash(cliente.clave, contrasena_actual):
            flash("❌ Contraseña actual incorrecta", "danger")
            return redirect(url_for("clientes.cambiar_contrasena"))

        try:
            cliente.clave = bcrypt.generate_password_hash(nueva_contrasena).decode("utf-8")
            db.session.commit()
            flash("✅ Contraseña actualizada", "success")
            return redirect(url_for("catalogo.catalogo_cliente"))
        except Exception as e:
            db.session.rollback()
            flash(f"❌ Error: {str(e)}", "danger")
    
    return render_template("cliente_cambiar_contrasena.html")