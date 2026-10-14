p='/app/templates/carrito.html'
s=open(p,encoding='utf-8').read()
print('iniciarMapaRecojo' in s)
print('mapaRecojo count', s.count('id="mapaRecojo"'))
print('setTimeout inhibit', 'setTimeout(iniciarMapaRecojo' in s)
PY