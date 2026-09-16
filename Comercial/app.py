import os
from flask import Flask, render_template, session, request, redirect, url_for
from extensions import db, login_manager, cors, bcrypt
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Importar las instancias desde extensions.py
from flask_login import UserMixin

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

load_dotenv()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/comercial_db'
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    bcrypt.init_app(app)  # Inicializar Bcrypt  
    # Configurar login
    login_manager.login_view = 'admin.login'
    
    # =============================================
    # IMPORTAR BLUEPRINTS (AHORA SÍ FUNCIONA)
    # =============================================
    from routes.cliente import cliente_bp
    from routes.pedidos import pedidos_bp
    from routes.ventas import ventas_bp
    #from routes.cupones import cupones_bp
    from routes.pagos import pagos_bp
    #from routes.admin import admin_bp
    
    app.register_blueprint(cliente_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(ventas_bp)
    #app.register_blueprint(cupones_bp)
    app.register_blueprint(pagos_bp)
    #app.register_blueprint(admin_bp)
    
    # Rutas principales
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/catalogo')
    def catalogo():
        return render_template('catalogo_cliente.html')
    
    @app.route('/health')
    def health():
        return {"status": "ok", "service": "comercial"}, 200
    
    # =============================================
    # CREAR TABLAS Y USUARIO ADMIN
    # =============================================
    with app.app_context():
        from models.clientes import Cliente
        from models.pedidos import Pedido
        from models.ventas import Venta
        from models.detallePedido import DetallePedido
        from models.usuarioSistema import UsuarioSistema
        from models.cupones import Cupon
        from models.intentos_login import IntentosLogin

        db.create_all()
        
      
        if not UsuarioSistema.query.filter_by(correo='admin@admin.com').first():
            admin = UsuarioSistema(
                nombres='Admin',
                apellidos='Principal',
                correo='admin@admin.com',
                clave=generate_password_hash('admin123'),
                rol='administrador'
            )
            db.session.add(admin)
            db.session.commit()
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)