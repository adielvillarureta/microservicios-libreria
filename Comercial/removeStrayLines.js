const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/catalogo_cliente.html';
let lines=fs.readFileSync(p,'utf8').split(/\r?\n/);
const before=lines.length;
const cleaned=lines.filter(l=>!l.includes("'productosGrid');"));
fs.writeFileSync(p,cleaned.join('\n'));
console.log('removed', before-cleaned.length);