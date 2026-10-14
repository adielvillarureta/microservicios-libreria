const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/catalogo_cliente.html';
let lines=fs.readFileSync(p,'utf8').split(/\n/);
for (let i=0;i<lines.length;i++){
  if (lines[i].includes("if (!grid) grid = document.getElementById(")) {
    lines[i]="    var grid = document.getElementById('productosGrid');";
    console.log('fixed line',i+1);
  }
  if (lines[i].includes("var contador = document.getElementById('contadorProductos');") && i>0 && lines[i-1].includes("renderizarPaginaCatalogo")) {
    // nothing
  }
}
fs.writeFileSync(p, lines.join('\n'));
console.log('done');