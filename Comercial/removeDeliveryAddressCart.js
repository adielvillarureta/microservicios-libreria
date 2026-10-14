const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
const start=s.indexOf('                        <div id="direccionEntrega"');
const end=s.indexOf('                </div>\n\n                    <a href="/catalogo"', start);
console.log('start',start,'end',end);
if (start!==-1 && end!==-1) {
  s = s.slice(0,start) + '\n' + s.slice(end);
  fs.writeFileSync(p,s);
  console.log('done');
} else {
  console.log('not found');
}