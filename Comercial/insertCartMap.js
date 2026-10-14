const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
if (s.indexOf('id="mapaCarrito"') === -1) {
  const marker = '<small class="text-muted d-block mt-1">* Tiempo de entrega: 3-5 días hábiles</small>';
  const idx = s.indexOf(marker);
  if (idx !== -1) {
    const insert = `\n                            <div id="mapaCarrito" class="mt-2 rounded overflow-hidden border" style="height: 200px; display:none;"></div>
                            <small class="text-muted d-block mt-1">Ubicación seleccionada en el mapa y sincronizada con checkout.</small>\n`;
    s = s.slice(0, idx + marker.length) + insert + s.slice(idx + marker.length);
    fs.writeFileSync(p,s,'utf8');
    console.log('map inserted');
  } else console.log('marker not found');
} else console.log('already');