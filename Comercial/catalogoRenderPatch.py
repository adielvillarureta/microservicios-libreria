p='/app/templates/catalogo_cliente.html'
s=open(p,encoding='utf-8').read()
needle='function mostrarProductos(productos) {\n    var grid = document.getElementById('
assert needle in s, 'not found'
helper='''var porPaginaCatalogo = 12;
var paginaCatalogoActual = 1;
var productosRenderCatalogo = [];
function cambiarPaginaCatalogo(pagina) { paginaCatalogoActual = pagina; renderizarPaginaCatalogo(); var g = document.getElementById('productosGrid'); if (g) g.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
function mostrarProductos(productos) { productosRenderCatalogo = (productos || []); paginaCatalogoActual = 1; renderizarPaginaCatalogo(); }
function renderizarPaginaCatalogo() {
    var grid = document.getElementById('productosGrid');
    var contador = document.getElementById('contadorProductos');
    var productos = productosRenderCatalogo || [];
    if (!productos || productos.length === 0) {
        grid.innerHTML = '<div class="col-12 text-center py-5"><i class="fas fa-box-open fa-5x text-muted mb-4 opacity-50"></i><h5 class="text-muted">No hay productos que coincidan</h5><p class="text-muted small">Prueba con otros filtros</p></div>';
        if (contador) contador.innerHTML = '<i class="fas fa-box me-1"></i> 0 productos';
        var pc = document.getElementById('paginacionCatalogo'); if (pc) pc.innerHTML = '';
        return;
    }
    var total = productos.length;
    var totalPaginas = Math.max(1, Math.ceil(total / porPaginaCatalogo));
    if (paginaCatalogoActual > totalPaginas) paginaCatalogoActual = totalPaginas;
    if (paginaCatalogoActual < 1) paginaCatalogoActual = 1;
    var inicio = (paginaCatalogoActual - 1) * porPaginaCatalogo;
    var paginaItems = productos.slice(inicio, inicio + porPaginaCatalogo);
    renderizarCardsCatalogo(paginaItems, grid);
    if (contador) contador.innerHTML = '<i class="fas fa-box me-1"></i> ' + total + ' producto' + (total !== 1 ? 's' : '');
    var pc = document.getElementById('paginacionCatalogo');
    if (pc) {
        if (totalPaginas <= 1) { pc.innerHTML = ''; }
        else {
            var h = '<nav aria-label="Paginacion" class="d-flex justify-content-center mt-3"><ul class="pagination pagination-sm">';
            for (var i = 1; i <= totalPaginas; i++) {
                var active = i === paginaCatalogoActual ? ' active' : '';
                h += '<li class="page-item' + active + '"><a class="page-link" href="#" onclick="cambiarPaginaCatalogo(' + i + ');return false;">' + i + '</a></li>';
            }
            h += '</ul></nav>';
            pc.innerHTML = h;
        }
    }
}
function renderizarCardsCatalogo(productos, grid) {
'''
helperEnd = '' # then insert original loop after this
# replace original first line needle by wrapper marker + render call; keep original body as function renderizarCardsCatalogo? We need rename original signature.
# We'll turn `function mostrarProductos(productos) {` into `function renderizarCardsCatalogo(productos, grid) {` and remove its grid/contador declarations? Original starts with those.
s = s.replace(needle, helper + '\n', 1)
# Replace the first var grid/contador lines inside original body to use passed grid (avoid redefinition). They are now inside renderizarCardsCatalogo.
marker2 = '''function renderizarCardsCatalogo(productos) {
    var grid = document.getElementById('productosGrid');
    var contador = document.getElementById('contadorProductos');
'''
s = s.replace('''var grid = document.getElementById('productosGrid');
    var contador = document.getElementById('contadorProductos');''', '''if (!grid) grid = document.getElementById('productosGrid');''', 1)
# Callback constructor mismatch: wrapper already called renderizarCardsCatalogo(paginaItems, grid). Fix function signature...
# Replace function signature with grid param.
s = s.replace('function renderizarCardsCatalogo(productos) {', 'function renderizarCardsCatalogo(productos, grid) {', 1)
open(p,'w',encoding='utf-8').write(s)
print('ok')
PY