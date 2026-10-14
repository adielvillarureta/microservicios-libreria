p='/app/templates/catalogo_cliente.html'
lines=open(p,encoding='utf-8').read().splitlines()
# find the line with stray 'productsGrid');
target = None
for i,line in enumerate(lines):
    if "'productosGrid');" in line:
        target=i
        break
print('target', target, repr(lines[target]) if target is not None else 'NONE')
if target is not None:
    del lines[target]
    open(p,'w',encoding='utf-8').write('\n'.join(lines))
    print('removed')
PY