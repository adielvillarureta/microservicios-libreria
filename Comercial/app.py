import os
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

load_dotenv()

# Inicializar extensiones fuera de create_app
db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()

def create_app():
    app = Flask(__name__, template_folder='templates')
    
    # Configuración
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}"
        f"@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Configuración de correo
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'admin.login'
    
    # Registrar blueprints DESPUÉS de que db esté inicializado
    from routes.cliente import cliente_bp
    from routes.pedidos import pedidos_bp
    from routes.ventas import ventas_bp
    from routes.cupones import cupones_bp
    from routes.pagos import pagos_bp
    from routes.admin import admin_bp
    
    app.register_blueprint(cliente_bp)
    app.register_blueprint(pedidos_bp)
    app.register_blueprint(ventas_bp)
    app.register_blueprint(cupones_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(admin_bp)
    
    # Rutas principales
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/catalogo')
    def catalogo():
        # Aquí se consumiría la API de inventario
        return render_template('catalogo_cliente.html')
    
    @app.route('/health')
    def health():
        return {"status": "ok", "service": "comercial"}, 200
    
    # Crear tablas automáticamente
    with app.app_context():
        db.create_all()
        # Crear admin por defecto si no existe
        from models.usuarioSistema import UsuarioSistema
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