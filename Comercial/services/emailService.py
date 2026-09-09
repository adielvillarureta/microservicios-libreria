# Comercial/services/emailService.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime

EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp-librospe.alwaysdata.net')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USER = os.getenv('EMAIL_USER', 'librospe@alwaysdata.net')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'Ventas2026!')
EMAIL_FROM = os.getenv('EMAIL_FROM', 'librospe@alwaysdata.net')

def enviar_comprobante_email(destinatario, cliente_nombre, tipo_comprobante, 
                             numero_comprobante, fecha, productos, total_venta):
    """Envía el comprobante por correo electrónico"""
    try:
        if not destinatario or '@' not in destinatario:
            print(f"❌ Email inválido: {destinatario}")
            return False
        
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = destinatario
        msg['Subject'] = f"{tipo_comprobante.upper()} ELECTRÓNICA N° {numero_comprobante}"
        
        html = generar_html_comprobante(cliente_nombre, tipo_comprobante, 
                                       numero_comprobante, fecha, productos, total_venta)
        
        msg.attach(MIMEText(html, 'html'))
        
        print(f"📧 Enviando a {destinatario}...")
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Correo enviado a {destinatario}")
        return True
        
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
        return False

def generar_html_comprobante(cliente_nombre, tipo_comprobante, numero_comprobante, 
                             fecha, productos, total_venta):
    """Genera el HTML del comprobante"""
    
    productos_html = ""
    for p in productos:
        productos_html += f"""
        <tr>
            <td style="padding: 8px;">{p['nombre']}</td>
            <td style="padding: 8px; text-align: center;">{p['cantidad']}</td>
            <td style="padding: 8px; text-align: right;">S/. {p['precio_unitario']:.2f}</td>
            <td style="padding: 8px; text-align: right;">S/. {p['total']:.2f}</td>
        </tr>
        """
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; }}
            .header {{ background: linear-gradient(135deg, #1e3a8a, #3b82f6); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ padding: 30px; background: #f8f9fa; }}
            .total {{ font-size: 20px; font-weight: bold; color: #28a745; text-align: right; padding-top: 15px; margin-top: 15px; border-top: 2px solid #28a745; }}
            .footer {{ background: #e9ecef; padding: 15px; text-align: center; font-size: 12px; color: #6c757d; border-radius: 0 0 10px 10px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #1e3a8a; color: white; padding: 10px; }}
            td {{ padding: 8px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h2>📚 LIBRERÍA SALESIANA DON BOSCO</h2>
            <h3>{tipo_comprobante.upper()} DE VENTA ELECTRÓNICA</h3>
            <p><strong>N° {numero_comprobante}</strong></p>
        </div>
        <div class="content">
            <p><strong>📅 Fecha:</strong> {fecha.strftime('%d/%m/%Y %H:%M:%S')}</p>
            <p><strong>👤 Cliente:</strong> {cliente_nombre or 'Consumidor Final'}</p>
            
            <table>
                <thead>
                    <tr>
                        <th>Producto</th>
                        <th>Cantidad</th>
                        <th>Precio Unit.</th>
                        <th>Total</th>
                    </tr>
                </thead>
                <tbody>
                    {productos_html}
                </tbody>
            </table>
            
            <div class="total">
                <p><strong>TOTAL: S/. {total_venta:.2f}</strong></p>
            </div>
            
            <p style="text-align: center; margin-top: 25px;">
                <strong>✨ ¡Gracias por su compra! ✨</strong><br>
                <small>Este es un comprobante de venta electrónico válido</small>
            </p>
        </div>
        <div class="footer">
            <p>Librería Salesiana Don Bosco | Todos los derechos reservados</p>
            <p>📧 ventas@librospe.alwaysdata.net</p>
        </div>
    </body>
    </html>
    """