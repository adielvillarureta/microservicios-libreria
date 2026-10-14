const fs=require('fs');
const p='C:/Users/LABH/Documents/GitHub/microservicios-libreria/Comercial/templates/carrito.html';
let s=fs.readFileSync(p,'utf8');
const old = `        if (tipoEntregaSeleccionado === 'delivery') {
            let direccion = document.getElementById('direccion')?.value.trim();
            if (!direccion) {
                Swal.fire({
                    icon: 'warning',
                    title: 'Dirección requerida',
                    text: 'Ingresa tu dirección de entrega'
                });
                return;
            }
            direccionEntrega = direccion;
        } else {
            direccionEntrega = '';
        }`;
const neu = `        if (tipoEntregaSeleccionado === 'delivery') {
            let direccion = document.getElementById('direccion')?.value.trim() || '';
            direccionEntrega = direccion;
        } else {
            direccionEntrega = '';
        }`;
if (s.includes(old)) { s=s.replace(old,neu,1); fs.writeFileSync(p,s,'utf8'); console.log('done'); } else console.log('old not found');
PY