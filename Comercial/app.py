# Comercial/app.py
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from functools import wraps
from datetime import datetime, timedelta
from sqlalchemy import func, text
import secrets
from dotenv import load_dotenv


load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "clave_secreta_comercial")

db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"connect_args": {"ssl": {"ssl_mode": "REQUIRED"}}}

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


from models.clientes import Cliente
from models.ventas import Venta
from models.pedidos import Pedido
from models.detallePedido import DetallePedido



def login_required_cliente(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "cliente_id" not in session:
            flash("Debes iniciar sesión para continuar", "warning")
            return redirect(url_for("login_cliente"))
        return f(*args, **kwargs)
    return decorated_function



from routes.catalogo import catalogo_bp
from routes.clientes import clientes_bp
from routes.pedidos import pedidos_bp
from routes.ventas import ventas_bp

app.register_blueprint(catalogo_bp, url_prefix='/catalogo')
app.register_blueprint(clientes_bp, url_prefix='/cliente')
app.register_blueprint(pedidos_bp, url_prefix='/pedidos')
app.register_blueprint(ventas_bp, url_prefix='/ventas')


@app.route("/")
def inicio():
    return render_template("index.html")

@app.route("/health")
def health():
    """Health check para el microservicio"""
    return jsonify({
        "status": "ok",
        "service": "comercial",
        "timestamp": datetime.now().isoformat()
    })

@app.route("/login-cliente", methods=["GET", "POST"])
def login_cliente():
    """Login para clientes"""
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        clave = request.form.get("clave", "")
        
        if not email or not clave:
            flash("❌ Ingresa email y contraseña", "danger")
            return render_template("login_cliente.html")
        
        cliente = Cliente.query.filter_by(correo=email).first()
        
        if not cliente:
            flash("❌ Correo no registrado", "danger")
            return render_template("login_cliente.html")
        
        if bcrypt.check_password_hash(cliente.clave, clave):
            session["cliente_id"] = cliente.id
            session["cliente_nombres"] = cliente.nombres
            session["cliente_apellidos"] = cliente.apellidos
            session["cliente_correo"] = cliente.correo
            flash(f"✅ ¡Bienvenido {cliente.nombres}!", "success")
            return redirect(url_for("catalogo.catalogo_cliente"))
        else:
            flash("❌ Contraseña incorrecta", "danger")
        
    return render_template("login_cliente.html")

@app.route("/logout-cliente")
def logout_cliente():
    session.clear()
    flash("✅ Sesión cerrada", "success")
    return redirect(url_for("catalogo.catalogo_cliente"))

# ============================
# CONTEXT PROCESSORS
# ============================

@app.context_processor
def inject_categorias():

    try:

        from models.categoria import Categoria
        categorias = Categoria.query.filter_by(activo=True).all()
        return dict(categorias=categorias)
    except:
        return dict(categorias=[])


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001, debug=False)