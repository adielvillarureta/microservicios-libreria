const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
// remove blue map link line
s=s.replace(/\s*<a id="btnVerEnMapa"[\s\S]*?<\/a>\n/, '\n');
fs.writeFileSync(p,s);
console.log('done');