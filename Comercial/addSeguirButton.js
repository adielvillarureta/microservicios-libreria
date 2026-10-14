const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
if (!s.includes('href="/catalogo"') || !s.includes('Seguir comprando en tienda')) {
  const marker='                    <button class="btn btn-oro w-100 mt-2 py-2" onclick="irACheckout()">';
  const btn='\n                    <a href="/catalogo" class="btn btn-outline-secondary w-100 mt-2 py-2 rounded-pill">\n                        <i class="fas fa-store me-2"></i>Seguir comprando en tienda\n                    </a>\n';
  s=s.replace(marker, btn + marker, 1);
  fs.writeFileSync(p,s,'utf8');
  console.log('done');
} else console.log('already has button');