p='/app/templates/catalogo_cliente.html'
s=open(p,encoding='utf-8').read()
marker = '<div class="row g-3 g-md-4" id="productosGrid">'
idx = s.rfind(marker)
assert idx!=-1
close = '</div>\n            </div>'
# Insert pagination holder after grid's closing div: find first occurrence of '</div>\n        </div>' after marker
end = s.find('</div>\n        </div>', idx)
assert end!=-1
insert = '</div>\n            <div id="paginacionCatalogo" class="col-12 mt-2 d-flex justify-content-center"></div>\n'
s = s[:end] + insert + s[end:]
# Remove "Aplicar Filtros" duplicate button row; hide button keep only limpiar visually? Make one.
s = s.replace('                        <button class="btn btn-gold w-100 mb-2 rounded-pill" id="btnAplicarFiltros">\n                            <i class="fas fa-search me-2"></i>Aplicar Filtros\n                        </button>\n', '')
open(p,'w',encoding='utf-8').write(s)
print('ok')
PY