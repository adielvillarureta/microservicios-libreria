const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/catalogo_cliente.html';
let s=fs.readFileSync(p,'utf8');
// Add section before container-fluid
if (!s.includes('id="destacadosTemporada"')) {
  const marker = '<div class="d-md-none px-3 pt-2 pb-1">';
  const block = `<section id="destacadosTemporada" class="container mt-3 mb-2" style="display:none;">
    <div class="card border-0 rounded-4 shadow-sm mb-3">
        <div class="card-body py-3">
            <h5 class="mb-0 fw-bold"><i class="fas fa-seedling me-2 text-gold"></i>Temporada destacada</h5>
            <div class="row g-2 mt-2" id="destacadosGrid"></div>
        </div>
    </div>
</section>
`;
  s=s.replace(marker, block+marker,1);
}
// Update cargarProductos area: after productosOriginal = data;
if (!s.includes('renderizarDestacados(')) {
  s=s.replace('            productosOriginal = data;\n            productosFiltrados = data;\n            mostrarProductos(productosFiltrados);',
              '            productosOriginal = data;\n            productosFiltrados = data;\n            renderizarDestacados((data || []).filter(function(p){return p.destacado;}).slice(0,4));\n            mostrarProductos(productosFiltrados);', 1);
}
// Add renderizarDestacados function before mostrarProductos wrapper (porPaginaCatalogo)
const fn = `function renderizarDestacados(items) {
    var sec = document.getElementById('destacadosTemporada');
    var grid = document.getElementById('destacadosGrid');
    if (!sec || !grid) return;
    if (!items || items.length === 0) { sec.style.display = 'none'; return; }
    sec.style.display = '';
    var h = '';
    items.forEach(function(p) {
        var precio = p.precio_oferta ? p.precio_oferta : p.precio;
        h += '<div class="col-6 col-md-3"><div class="card h-100 border-0 shadow-sm rounded-3"><div class="card-body p-2 p-md-3 text-center"><img src="' + (p.imagen_url || '/static/img/default-product.png') + '" class="img-fluid rounded mb-2" style="max-height:84px;object-fit:contain" alt="' + escapeHtml(p.nombre) + '"><div class="fw-bold small">' + escapeHtml(p.nombre.substring(0,38)) + '</div><div class="text-danger fw-bold mt-1">S/. ' + (precio||0).toFixed(2) + '</div><button class="btn btn-gold btn-sm rounded-pill w-100 mt-2" onclick="agregarAlCarrito(' + p.id + ',\\'' + escapeHtml(p.nombre) + '\\', ' + precio + ', ' + (p.cantidad||1) + ')">Agregar</button></div></div></div>';
    });
    grid.innerHTML = h;
}
`;
if (!s.includes('function renderizarDestacados')) {
  s=s.replace('var porPaginaCatalogo = 12;', fn + '\nvar porPaginaCatalogo = 12;', 1);
}
fs.writeFileSync(p,s,'utf8');
console.log('ok');