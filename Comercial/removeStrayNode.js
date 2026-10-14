const fs=require('fs');
const p='C:\\Users\\LABH\\Documents\\GitHub\\microservicios-libreria\\Comercial\\templates\\catalogo_cliente.html';
let s=fs.readFileSync(p,'utf8');
s=s.replace("'\n'productosGrid');\n", '\n');
// fallback
s=s.replace("'productosGrid');\n",'');
fs.writeFileSync(p,s);
console.log('done');