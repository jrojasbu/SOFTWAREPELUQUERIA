from xhtml2pdf import pisa
from io import BytesIO
from flask import Flask, render_template
import os

app = Flask(__name__)

def render_pdf(template_src, context_dict):
    # Mocking jinja environment for standalone test if needed, 
    # but since we have the app, we can use app.jinja_env if we set up an app context.
    with app.app_context():
        template = app.jinja_env.get_template(template_src)
        html = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        if not pdf.err:
            return result.getvalue()
    return None

def test_simple_pdf():
    print("Starting PDF generation test...")
    
    # Mock data
    context = {
        'data': [
            {'estilista': 'Test Stylist', 'descripcion': 'Corte', 'tipo': 'Servicio', 'metodo_pago': 'Efectivo', 'valor': 20000},
            {'estilista': 'Test Stylist', 'descripcion': 'Shampoo', 'tipo': 'Producto', 'metodo_pago': 'Tarjeta', 'valor': 15000}
        ],
        'totals': {
            'valor': 35000,
            'comision': 10000,
            'gastos': 5000,
            'utilidad': 20000
        },
        'date': '2023-10-27',
        'logo_path': None, # Skip logo for this test or use a dummy path
        'generation_time': '2023-10-27 10:00:00'
    }
    
    try:
        pdf_content = render_pdf('pdf_report.html', context)
        
        if pdf_content:
            print(f"Success: PDF generated, size {len(pdf_content)} bytes")
            with open('test_simple.pdf', 'wb') as f:
                f.write(pdf_content)
        else:
            print("Error: PDF generation returned None")
    except Exception as e:
        print(f"Exception during PDF generation: {e}")

if __name__ == "__main__":
    test_simple_pdf()
