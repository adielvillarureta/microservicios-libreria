s=open('/app/templates/carrito.html',encoding='utf-8').read()
print('textarea count:', s.count('id="direccion"'))
print('has btnVer:', 'btnVerEnMapa' in s)
print('has helper:', 'function actualizarLinkMapa' in s)
print('clean noduplicate placeholders:', 'placeholder="??' not in s)
PY