from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS

# Instancias globales (sin inicializar con app todavía)
db = SQLAlchemy()
login_manager = LoginManager()
cors = CORS()