""" redirección de la raíz del proyecto.

    Comercial  -> http://localhost:5001
    Inventario -> http://localhost:5000
"""
from flask import Flask, redirect

app = Flask(__name__)


@app.route('/')
def home():
    return (
        "Proyecto Librería Salesiana Don Bosco\n"
        "--------------------------------------\n"
        "Comercial (ventas) : http://localhost:5001\n"
        "Inventario         : http://localhost:5000\n"
        "phpMyAdmin         : http://localhost:8080\n"
    )


@app.route('/comercial')
def ir_a_comercial():
    return redirect('http://localhost:5001')


@app.route('/inventario')
def ir_a_inventario():
    return redirect('http://localhost:5000')


if __name__ == '__main__':
    app.run(debug=True, port=5002)
