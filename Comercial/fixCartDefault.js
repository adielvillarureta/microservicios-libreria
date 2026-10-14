const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
const old=`        if (tipoGuardado) {
            tipoEntregaSeleccionado = tipoGuardado;
            seleccionarEntrega(tipoEntregaSeleccionado);
        }
`;
const neu=`        tipoEntregaSeleccionado = tipoGuardado || 'recojo';
        seleccionarEntrega(tipoEntregaSeleccionado);
`;
if (s.includes(old)) {
  s=s.replace(old,neu);
  fs.writeFileSync(p,s,'utf8');
  console.log('done');
} else console.log('old not found');
PY