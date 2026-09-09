import os
from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

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
    
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    cors.init_app(app)
    
    # Configurar login
    login_manager.login_view = 'usuario.login'
    
    # Importar modelos para que SQLAlchemy los conozca
    from models.categoria import Categoria
    from models.producto import Producto
    from models.proveedor import Proveedor
    from models.usuarioSistema import UsuarioSistema
    
    # Registrar blueprints
    from routes.producto import producto_bp
    from routes.proveedores import proveedores_bp
    from routes.bloqueos import bloqueos_bp
    from routes.usuario import usuario_bp
    
    app.register_blueprint(producto_bp)
    app.register_blueprint(proveedores_bp)
    app.register_blueprint(bloqueos_bp)
    app.register_blueprint(usuario_bp)
    
    # ======================================
    # RUTAS AUXILIARES (Login y Panel)
    # ======================================
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            correo = request.form.get('correo')
            clave = request.form.get('clave')
            usuario = UsuarioSistema.query.filter_by(correo=correo).first()
            
            if usuario and check_password_hash(usuario.clave, clave):
                session['usuario_id'] = usuario.id
                session['nombre'] = usuario.nombres
                session['rol'] = usuario.rol
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error="Credenciales incorrectas")
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.route('/')
    def dashboard():
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        
        total_productos = Producto.query.count()
        stock_bajo = Producto.query.filter(Producto.cantidad <= 5, Producto.cantidad > 0).all()
        stock_critico = Producto.query.filter(Producto.cantidad == 0).all()
        total_proveedores = Proveedor.query.count()
        
        return render_template(
            'dashboard.html',
            total_ventas_hoy=0,
            cantidad_ventas_hoy=0,
            total_ventas_mes=0,
            cantidad_ventas_mes=0,
            pedidos_pendientes=0,
            pedidos_en_proceso=0,
            total_clientes=0,
            clientes_nuevos=0,
            stock_bajo=stock_bajo,
            stock_critico=stock_critico,
            total_productos=total_productos,
            total_proveedores=total_proveedores,
            top_productos=[],
            graph_ventas={"data": [], "layout": {}},
            graph_top={"data": [], "layout": {}},
            graph_cat={"data": [], "layout": {}},
            graph_estados={"data": [], "layout": {}},
            ahora_peru=__import__('datetime').datetime.now()
        )

    @app.route('/health')
    def health():
        return {"status": "ok", "service": "inventario"}, 200

    # Crear tablas automáticamente
    with app.app_context():
        db.create_all()
        # Crear usuario admin por defecto si no existe
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
    app.run(host='0.0.0.0', port=5001, debug=True)