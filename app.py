from flask import Flask, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return "¡Hola! Soy la raíz del proyecto. Ve a /comercial o /inventario"

# Redirigir a los microservicios (ejemplo si estuvieran en otros puertos)
@app.route('/comercial')
def ir_a_comercial():
    return redirect('http://localhost:5001') # Asumiendo que Comercial corre en el 5001

if __name__ == '__main__':
    app.run(debug=True, port=5000) # La raíz corre en el 5000