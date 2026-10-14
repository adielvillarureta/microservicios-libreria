const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/catalogo_cliente.html';
let s=fs.readFileSync(p,'utf8');
const start=s.indexOf('function renderizarPaginaCatalogo() {');
const end=s.indexOf('function renderizarCardsCatalogo',start);
const good=`function renderizarPaginaCatalogo() {
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
`;
s=s.substring(0,start)+good+s.substring(end);
fs.writeFileSync(p,s);
console.log('ok');