from flask import Flask, render_template, request, jsonify, session, redirect, url_for, make_response
from werkzeug.security import generate_password_hash, check_password_hash
import functools
import pandas as pd
import os
from datetime import datetime
import sqlite3
import json
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = 'magical_hair_secret_key_change_this_in_production'  # Required for session

# Use relative path for database.db
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')
STYLISTS_FILE = 'stylists.json'
SERVICES_FILE = 'services.json'
SEDES_FILE = 'sedes.json'
USERS_FILE = 'users.json'

@app.errorhandler(500)
def internal_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Error interno del servidor. Verifique los logs.'}), 500
    return "Error interno del servidor", 500

@app.errorhandler(404)
def not_found_error(error):
    if request.path.startswith('/api/'):
        return jsonify({'status': 'error', 'message': 'Recurso no encontrado'}), 404
    return "Página no encontrada", 404

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'status': 'error', 'message': 'Sesión expirada. Por favor recargue la página.'}), 401
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

def get_users():
    try:
        if not os.path.exists(USERS_FILE):
            # Create default admin user
            default_users = {
                'admin': generate_password_hash('admin')
            }
            save_users(default_users)
            return default_users
        with open(USERS_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        users = get_users()
        
        if username in users and check_password_hash(users[username], password):
            session.clear()
            session['user_id'] = username
            return jsonify({'status': 'success', 'message': 'Login exitoso'})
        
        return jsonify({'status': 'error', 'message': 'Usuario o contraseña incorrectos'})
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/users', methods=['GET'])
@login_required
def get_users_api():
    users = get_users()
    # Return list of usernames only
    return jsonify({'status': 'success', 'data': list(users.keys())})

@app.route('/api/users', methods=['POST'])
@login_required
def add_user():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Usuario y contraseña requeridos'})
        
    users = get_users()
    if username in users:
        return jsonify({'status': 'error', 'message': 'El usuario ya existe'})
        
    users[username] = generate_password_hash(password)
    save_users(users)
    return jsonify({'status': 'success', 'message': 'Usuario creado'})

@app.route('/api/users', methods=['DELETE'])
@login_required
def delete_user():
    data = request.json
    username = data.get('username')
    
    if username == 'admin':
        return jsonify({'status': 'error', 'message': 'No se puede eliminar el usuario admin'})
        
    if username == session.get('user_id'):
        return jsonify({'status': 'error', 'message': 'No puedes eliminar tu propio usuario'})
        
    users = get_users()
    if username in users:
        del users[username]
        save_users(users)
        return jsonify({'status': 'success', 'message': 'Usuario eliminado'})
        
    return jsonify({'status': 'error', 'message': 'Usuario no encontrado'})



def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the SQLite database if it doesn't exist."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Servicios
    c.execute('''CREATE TABLE IF NOT EXISTS servicios (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sede TEXT,
                    fecha TIMESTAMP,
                    estilista TEXT,
                    servicio TEXT,
                    valor REAL,
                    comision REAL,
                    metodo_pago TEXT
                );''')
                
    # Productos
    c.execute('''CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sede TEXT,
                    fecha TIMESTAMP,
                    estilista TEXT,
                    producto TEXT,
                    marca TEXT,
                    descripcion TEXT,
                    valor REAL,
                    comision REAL,
                    metodo_pago TEXT
                );''')

    # Gastos
    c.execute('''CREATE TABLE IF NOT EXISTS gastos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sede TEXT,
                    fecha TIMESTAMP,
                    descripcion TEXT,
                    valor REAL
                );''')

    # Inventario
    c.execute('''CREATE TABLE IF NOT EXISTS inventario (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sede TEXT,
                    producto TEXT,
                    marca TEXT,
                    descripcion TEXT,
                    cantidad REAL,
                    unidad TEXT,
                    valor REAL,
                    estado TEXT,
                    fecha_actualizacion TIMESTAMP
                );''')

    # Citas
    c.execute('''CREATE TABLE IF NOT EXISTS citas (
                    id TEXT PRIMARY KEY,
                    sede TEXT,
                    fecha TEXT,
                    hora TEXT,
                    cliente TEXT,
                    telefono TEXT,
                    servicio TEXT,
                    notas TEXT,
                    estado TEXT
                );''')

    # Gastos Mensuales
    c.execute('''CREATE TABLE IF NOT EXISTS gastos_mensuales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sede TEXT,
                    mes TEXT,
                    tipo TEXT,
                    valor REAL,
                    fecha_registro TIMESTAMP
                );''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_FILE} initialized.")


def get_stylists():
    try:
        with open(STYLISTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_stylists(stylists):
    with open(STYLISTS_FILE, 'w') as f:
        json.dump(stylists, f)

def get_services():
    try:
        with open(SERVICES_FILE, 'r') as f:
            data = json.load(f)
            # Migration check: if list of strings, convert to objects
            if data and isinstance(data[0], str):
                new_data = [{'name': s, 'value': 0} for s in data]
                save_services(new_data)
                return new_data
            return data
    except:
        return []

def save_services(services):
    with open(SERVICES_FILE, 'w') as f:
        json.dump(services, f)

def get_sedes():
    try:
        with open(SEDES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        # Return default sede if file doesn't exist
        default = ['Principal']
        save_sedes(default)
        return default

def save_sedes(sedes):
    with open(SEDES_FILE, 'w', encoding='utf-8') as f:
        json.dump(sedes, f, ensure_ascii=False, indent=2)

def insert_record(table, data):
    """Insert a record into the specified SQLite table."""
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Ensure data keys are lowercase to match SQL columns
        data = {k.lower(): v for k, v in data.items()}
        
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        
        c.execute(sql, list(data.values()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error inserting into SQLite: {e}")
        return False

@app.route('/')
@login_required
def index():
    stylists = get_stylists()
    services = get_services()
    sedes = get_sedes()
    return render_template('index.html', stylists=stylists, services=services, sedes=sedes)

@app.route('/certificado')
@login_required
def view_certificate():
    return render_template('certificado.html')

@app.route('/admin')
@login_required
def admin_panel():
    stylists = get_stylists()
    sedes = get_sedes()
    services = get_services()
    return render_template('admin.html', stylists=stylists, sedes=sedes, services=services)

@app.route('/certificado/descargar')
@login_required
def download_certificate_pdf():
    try:
        context = {
            'date': datetime.now().strftime('%d de %B de %Y'),
            'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Translate month names if possible or use simple format
        months = {
            'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo', 'April': 'Abril',
            'May': 'Mayo', 'June': 'Junio', 'July': 'Julio', 'August': 'Agosto',
            'September': 'Septiembre', 'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
        }
        now = datetime.now()
        date_str = f"{now.day} de {months.get(now.strftime('%B'), now.strftime('%B'))} de {now.year}"
        context['date'] = date_str

        pdf = render_pdf('certificado_pdf.html', context)
        if pdf:
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = 'attachment; filename=Certificado_Propiedad_MagicalHair.pdf'
            return response
        
        return "Error al generar el PDF del certificado", 500
    except Exception as e:
        return str(e), 500

@app.route('/api/stylist', methods=['POST'])
@login_required
def add_stylist():
    data = request.json
    new_stylist = data.get('name')
    if new_stylist:
        stylists = get_stylists()
        if new_stylist not in stylists:
            stylists.append(new_stylist)
            save_stylists(stylists)
            return jsonify({'status': 'success', 'message': 'Estilista agregado'})
        return jsonify({'status': 'error', 'message': 'El estilista ya existe'})
    return jsonify({'status': 'error', 'message': 'Nombre inválido'})

@app.route('/api/stylist', methods=['DELETE'])
@login_required
def delete_stylist():
    data = request.json
    name_to_delete = data.get('name')
    stylists = get_stylists()
    if name_to_delete in stylists:
        stylists.remove(name_to_delete)
        save_stylists(stylists)
        return jsonify({'status': 'success', 'message': 'Estilista eliminado'})
    return jsonify({'status': 'error', 'message': 'Estilista no encontrado'})

@app.route('/api/service-item', methods=['POST'])
@login_required
def add_service_item():
    data = request.json
    new_service_name = data.get('name')
    new_service_value = float(data.get('value', 0))
    
    if new_service_name:
        services = get_services()
        # Check if exists by name
        if not any(s['name'] == new_service_name for s in services):
            services.append({'name': new_service_name, 'value': new_service_value})
            save_services(services)
            return jsonify({'status': 'success', 'message': 'Servicio agregado'})
        return jsonify({'status': 'error', 'message': 'El servicio ya existe'})
    return jsonify({'status': 'error', 'message': 'Nombre inválido'})

@app.route('/api/service-item', methods=['DELETE'])
@login_required
def delete_service_item():
    data = request.json
    name_to_delete = data.get('name')
    services = get_services()
    
    # Filter out the service with the given name
    new_services = [s for s in services if s['name'] != name_to_delete]
    
    if len(new_services) < len(services):
        save_services(new_services)
        return jsonify({'status': 'success', 'message': 'Servicio eliminado'})
    return jsonify({'status': 'error', 'message': 'Servicio no encontrado'})

@app.route('/api/sedes', methods=['GET'])
@login_required
def get_sedes_api():
    sedes = get_sedes()
    return jsonify({'status': 'success', 'data': sedes})

@app.route('/api/sede', methods=['POST'])
@login_required
def add_sede():
    data = request.json
    new_sede = data.get('name')
    if new_sede:
        sedes = get_sedes()
        if new_sede not in sedes:
            sedes.append(new_sede)
            save_sedes(sedes)
            return jsonify({'status': 'success', 'message': 'Sede agregada'})
        return jsonify({'status': 'error', 'message': 'La sede ya existe'})
    return jsonify({'status': 'error', 'message': 'Nombre inválido'})

@app.route('/api/sede', methods=['DELETE'])
@login_required
def delete_sede():
    data = request.json
    name_to_delete = data.get('name')
    sedes = get_sedes()
    if len(sedes) <= 1:
        return jsonify({'status': 'error', 'message': 'No se puede eliminar la última sede'})
    if name_to_delete in sedes:
        sedes.remove(name_to_delete)
        save_sedes(sedes)
        return jsonify({'status': 'success', 'message': 'Sede eliminada'})
    return jsonify({'status': 'error', 'message': 'Sede no encontrada'})

def calculate_commission(stylist, service, value):
    service_lower = service.lower()
    is_special_service = 'tinte' in service_lower or 'mechas' in service_lower or 'keratina' in service_lower
    
    if 'monica' in stylist.lower():
        if is_special_service:
            return value * 0.50
        return value * 0.40
    
    if 'elizabeth' in stylist.lower():
        if is_special_service:
            return value * 0.60
        return value * 0.50
        
    # Default for others
    return value * 0.50

@app.route('/api/service', methods=['POST'])
@login_required
def add_service():
    data = request.json
    valor = float(data['valor'])
    stylist = data['estilista']
    service = data['servicio']
    metodo_pago = data.get('metodo_pago', 'Efectivo')
    sede = data.get('sede', 'Principal')
    
    comision = calculate_commission(stylist, service, valor)
    
    record = {
        'Sede': sede,
        'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Estilista': stylist,
        'Servicio': service,
        'Valor': valor,
        'Comision': comision,
        'Metodo_Pago': metodo_pago
    }
    
    if insert_record('servicios', record):
        return jsonify({'status': 'success', 'message': 'Servicio registrado', 'comision': comision})
    return jsonify({'status': 'error', 'message': 'Error al guardar'}), 500

@app.route('/api/product', methods=['POST'])
@login_required
def add_product():
    data = request.json
    valor = float(data['valor'])
    metodo_pago = data.get('metodo_pago', 'Efectivo')
    marca = data.get('marca', '')
    descripcion = data.get('descripcion', '')
    sede = data.get('sede', 'Principal')
    
    record = {
        'Sede': sede,
        'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Estilista': data['estilista'],
        'Producto': data['producto'],
        'Marca': marca,
        'Descripcion': descripcion,
        'Valor': valor,
        'Comision': valor * 0.10,
        'Metodo_Pago': metodo_pago
    }
    
    if insert_record('productos', record):
        # Update Inventory
        try:
            conn = get_db_connection()
            c = conn.cursor()
            
            # Use lowercase for column names
            # Find matching product in inventory at the same sede
            c.execute('SELECT id, cantidad FROM inventario WHERE producto = ? AND sede = ?', (data['producto'], sede))
            row = c.fetchone()
            
            if row:
                current_qty = float(row['cantidad'])
                if current_qty > 0:
                    new_qty = current_qty - 1
                    status = 'Nuevo' if new_qty > 0 else 'Agotado'
                    c.execute('UPDATE inventario SET cantidad = ?, estado = ? WHERE id = ?', (new_qty, status, row['id']))
                    conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating inventory: {e}")
            
        return jsonify({'status': 'success', 'message': 'Producto registrado y descontado del inventario'})
    return jsonify({'status': 'error', 'message': 'Error al guardar'}), 500

@app.route('/api/expense', methods=['POST'])
@login_required
def add_expense():
    data = request.json
    sede = data.get('sede', 'Principal')
    record = {
        'Sede': sede,
        'Fecha': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'Descripcion': data['descripcion'],
        'Valor': float(data['valor'])
    }
    
    if insert_record('gastos', record):
        return jsonify({'status': 'success', 'message': 'Gasto registrado'})
    return jsonify({'status': 'error', 'message': 'Error al guardar'}), 500

@app.route('/api/inventory', methods=['GET'])
@login_required
def get_inventory():
    try:
        sede_filter = request.args.get('sede', 'Principal')
        conn = get_db_connection()
        # Use pandas to read from SQL for easy dictionary conversion
        df = pd.read_sql('SELECT * FROM inventario WHERE sede = ?', conn, params=(sede_filter,))
        conn.close()
        
        # Replace NaN with empty string or 0 for JSON serialization
        df = df.fillna('')
        inventory = df.to_dict(orient='records')
        return jsonify({'status': 'success', 'data': inventory})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/inventory', methods=['POST'])
@login_required
def add_inventory_item():
    try:
        data = request.json
        producto = data.get('producto')
        marca = data.get('marca', '')
        descripcion = data.get('descripcion', '')
        cantidad = float(data.get('cantidad', 0))
        unidad = data.get('unidad')
        valor = float(data.get('valor', 0))
        estado = data.get('estado', 'Nuevo')
        sede = data.get('sede', 'Principal')
        
        if not producto:
            return jsonify({'status': 'error', 'message': 'Nombre del producto requerido'}), 400

        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if product exists to update
        c.execute('SELECT id FROM inventario WHERE sede = ? AND producto = ? AND marca = ? AND descripcion = ?', 
                  (sede, producto, marca, descripcion))
        row = c.fetchone()
        
        if row:
            # Update existing
            c.execute('''UPDATE inventario 
                         SET cantidad = ?, unidad = ?, valor = ?, estado = ?, fecha_actualizacion = ?
                         WHERE id = ?''', 
                      (cantidad, unidad, valor, estado, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), row['id']))
            message = 'Producto actualizado'
        else:
            # Add new
            new_row = {
                'sede': sede,
                'producto': producto,
                'marca': marca,
                'descripcion': descripcion,
                'cantidad': cantidad,
                'unidad': unidad,
                'valor': valor,
                'estado': estado,
                'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            columns = ', '.join(new_row.keys())
            placeholders = ', '.join(['?' for _ in new_row])
            c.execute(f'INSERT INTO inventario ({columns}) VALUES ({placeholders})', list(new_row.values()))
            message = 'Producto agregado al inventario'
            
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': message})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/inventory', methods=['DELETE'])
@login_required
def delete_inventory_item():
    try:
        data = request.json
        producto = data.get('producto')
        marca = data.get('marca', '')
        descripcion = data.get('descripcion', '')
        sede = data.get('sede', 'Principal')
        
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute('DELETE FROM inventario WHERE sede = ? AND producto = ? AND marca = ? AND descripcion = ?', 
                  (sede, producto, marca, descripcion))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Producto eliminado del inventario'})
        conn.close()
        return jsonify({'status': 'error', 'message': 'Producto no encontrado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/summary', methods=['GET'])
@login_required
def get_summary():
    try:
        # Get date and sede from query parameters
        date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        sede_filter = request.args.get('sede', 'Principal')
        summary_data = []
        total_valor = 0
        total_comision = 0
        total_gastos = 0

        conn = get_db_connection()
        
        # Read Services
        try:
            # Filter by date and sede using SQL
            df_services = pd.read_sql("SELECT * FROM servicios WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_services.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                com = float(row['comision']) if pd.notna(row['comision']) else 0.0
                metodo = row['metodo_pago'] if pd.notna(row['metodo_pago']) else 'N/A'
                    
                summary_data.append({
                    'id': int(row['id']),
                    'sheet': 'servicios',
                    'estilista': row['estilista'],
                    'descripcion': row['servicio'],
                    'valor': val,
                    'comision': com,
                    'tipo': 'Servicio',
                    'metodo_pago': metodo
                })
                total_valor += val
                total_comision += com
        except Exception as e:
            print(f"Error reading services: {e}")

        # Read Products
        try:
            df_products = pd.read_sql("SELECT * FROM productos WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_products.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                com = float(row['comision']) if pd.notna(row['comision']) else 0.0
                metodo = row['metodo_pago'] if pd.notna(row['metodo_pago']) else 'N/A'

                summary_data.append({
                    'id': int(row['id']),
                    'sheet': 'productos',
                    'estilista': row['estilista'],
                    'descripcion': row['producto'],
                    'valor': val,
                    'comision': com,
                    'tipo': 'Producto',
                    'metodo_pago': metodo
                })
                total_valor += val
                total_comision += com
        except Exception as e:
            print(f"Error reading products: {e}")

        # Read Expenses
        try:
            df_expenses = pd.read_sql("SELECT * FROM gastos WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_expenses.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                total_gastos += val
        except Exception as e:
            print(f"Error reading expenses: {e}")

        conn.close()
        
        # Calculate profit: Net Sales - Expenses - Commissions
        utilidad = total_valor - total_gastos - total_comision

        return jsonify({
            'status': 'success',
            'data': summary_data,
            'totals': {
                'valor': total_valor,
                'comision': total_comision,
                'gastos': total_gastos,
                'utilidad': utilidad
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/summary/update', methods=['POST'])
@login_required
def update_summary_item():
    try:
        data = request.json
        table_name = data.get('sheet').lower()
        try:
            row_id = int(data.get('id'))
            new_valor = float(data.get('valor'))
            new_comision = float(data.get('comision'))
        except (ValueError, TypeError):
             return jsonify({'status': 'error', 'message': 'Dato numérico inválido'}), 400
        
        if table_name not in ['servicios', 'productos']:
            return jsonify({'status': 'error', 'message': 'Tabla inválida'}), 400
            
        conn = get_db_connection()
        c = conn.cursor()
        
        c.execute(f'UPDATE {table_name} SET valor = ?, comision = ? WHERE id = ?', 
                  (new_valor, new_comision, row_id))
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Item actualizado'})
        
        conn.close()
        return jsonify({'status': 'error', 'message': 'Item no encontrado'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def render_pdf(template_src, context_dict):
    template = app.jinja_env.get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return result.getvalue()
    return None

@app.route('/export_pdf')
@login_required
def export_pdf():
    try:
        date_filter = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        sede_filter = request.args.get('sede', 'Principal')
        
        summary_data = []
        total_valor = 0
        total_comision = 0
        total_gastos = 0

        conn = get_db_connection()
        
        # Read Services
        try:
            df_services = pd.read_sql("SELECT * FROM servicios WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_services.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                com = float(row['comision']) if pd.notna(row['comision']) else 0.0
                metodo = row['metodo_pago'] if pd.notna(row['metodo_pago']) else 'N/A'
                    
                summary_data.append({
                    'estilista': row['estilista'],
                    'descripcion': row['servicio'],
                    'valor': val,
                    'comision': com,
                    'tipo': 'Servicio',
                    'metodo_pago': metodo
                })
                total_valor += val
                total_comision += com
        except: pass

        # Read Products
        try:
            df_products = pd.read_sql("SELECT * FROM productos WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_products.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                com = float(row['comision']) if pd.notna(row['comision']) else 0.0
                metodo = row['metodo_pago'] if pd.notna(row['metodo_pago']) else 'N/A'

                summary_data.append({
                    'estilista': row['estilista'],
                    'descripcion': row['producto'],
                    'valor': val,
                    'comision': com,
                    'tipo': 'Producto',
                    'metodo_pago': metodo
                })
                total_valor += val
                total_comision += com
        except: pass

        # Read Expenses
        try:
            df_expenses = pd.read_sql("SELECT * FROM gastos WHERE date(fecha) = ? AND sede = ?", 
                                     conn, params=(date_filter, sede_filter))
            for _, row in df_expenses.iterrows():
                val = float(row['valor']) if pd.notna(row['valor']) else 0.0
                total_gastos += val
        except: pass

        conn.close()
        
        utilidad = total_valor - total_gastos - total_comision
        
        context = {
            'date': date_filter,
            'sede': sede_filter,
            'summary': summary_data,
            'totals': {
                'valor': total_valor,
                'comision': total_comision,
                'gastos': total_gastos,
                'utilidad': utilidad
            }
        }
        
        pdf = render_pdf('pdf_report.html', context)
        if pdf:
            response = make_response(pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers['Content-Disposition'] = f'attachment; filename=Cierre_{sede_filter}_{date_filter}.pdf'
            return response
        
        return "Error generating PDF", 500
    except Exception as e:
        import traceback
        traceback.print_exc()
        return str(e), 500

@app.route('/api/statistics', methods=['GET'])
@login_required
def get_statistics():
    try:
        # Get month from query parameter (format: YYYY-MM)
        month_filter = request.args.get('month', datetime.now().strftime('%Y-%m'))
        year, month = month_filter.split('-')
        sede_filter = request.args.get('sede', '') # Optional sede filter
        
        conn = get_db_connection()
        
        # Read data from SQLite
        servicios_df = pd.read_sql("SELECT * FROM servicios", conn)
        productos_df = pd.read_sql("SELECT * FROM productos", conn)
        gastos_df = pd.read_sql("SELECT * FROM gastos", conn)
        inventario_df = pd.read_sql("SELECT * FROM inventario", conn)
        gastos_mensuales_df = pd.read_sql("SELECT * FROM gastos_mensuales", conn)
        
        conn.close()
        
        # Apply Sede Filter if provided
        if sede_filter:
             servicios_df = servicios_df[servicios_df['sede'] == sede_filter]
             productos_df = productos_df[productos_df['sede'] == sede_filter]
             gastos_df = gastos_df[gastos_df['sede'] == sede_filter]
             inventario_df = inventario_df[inventario_df['sede'] == sede_filter]
             gastos_mensuales_df = gastos_mensuales_df[gastos_mensuales_df['sede'] == sede_filter]

        # Filter by month with robust date parsing
        servicios_df['fecha'] = pd.to_datetime(servicios_df['fecha'], errors='coerce')
        productos_df['fecha'] = pd.to_datetime(productos_df['fecha'], errors='coerce')
        gastos_df['fecha'] = pd.to_datetime(gastos_df['fecha'], errors='coerce')
        
        # Drop rows with invalid dates if any
        servicios_df = servicios_df.dropna(subset=['fecha'])
        productos_df = productos_df.dropna(subset=['fecha'])
        gastos_df = gastos_df.dropna(subset=['fecha'])
        
        servicios_month = servicios_df[(servicios_df['fecha'].dt.year == int(year)) & 
                                       (servicios_df['fecha'].dt.month == int(month))]
        productos_month = productos_df[(productos_df['fecha'].dt.year == int(year)) & 
                                       (productos_df['fecha'].dt.month == int(month))]
        gastos_month = gastos_df[(gastos_df['fecha'].dt.year == int(year)) & 
                                 (gastos_df['fecha'].dt.month == int(month))]
        
        # Gastos Mensuales
        gastos_mensuales_month = gastos_mensuales_df[gastos_mensuales_df['mes'] == month_filter]

        # Calculate totals
        total_ventas = servicios_month['valor'].sum() + productos_month['valor'].sum()
        total_gastos = gastos_month['valor'].sum()
        total_nomina = servicios_month['comision'].sum() + productos_month['comision'].sum()
        utilidad_operativa = total_ventas - total_gastos - total_nomina
        
        total_gastos_fijos = gastos_mensuales_month['valor'].sum()
        utilidad_real = utilidad_operativa - total_gastos_fijos
        
        # Nómina por estilista
        nomina_servicios = servicios_month.groupby('estilista')['comision'].sum()
        nomina_productos = productos_month.groupby('estilista')['comision'].sum()
        nomina_por_estilista = (nomina_servicios.add(nomina_productos, fill_value=0)).to_dict()
        
        # Ventas por estilista
        ventas_servicios = servicios_month.groupby('estilista')['valor'].sum()
        ventas_productos = productos_month.groupby('estilista')['valor'].sum()
        ventas_por_estilista = (ventas_servicios.add(ventas_productos, fill_value=0)).to_dict()
        
        # Inventario resumido - Agrupado por producto
        inventario_agrupado = {}
        for _, row in inventario_df.iterrows():
            try:
                producto = row['producto'] if pd.notna(row['producto']) else ''
                if not producto:
                    continue
                    
                cantidad = float(row['cantidad']) if pd.notna(row['cantidad']) else 0.0
                valor = float(row['valor']) if pd.notna(row['valor']) else 0.0
                unidad = row['unidad'] if pd.notna(row['unidad']) else ''
                
                # Si el producto ya existe, sumar las cantidades y valores
                if producto in inventario_agrupado:
                    inventario_agrupado[producto]['cantidad'] += cantidad
                    inventario_agrupado[producto]['valor_total'] += cantidad * valor
                else:
                    inventario_agrupado[producto] = {
                        'producto': producto,
                        'cantidad': cantidad,
                        'unidad': unidad,
                        'valor_total': cantidad * valor
                    }
            except:
                continue
        
        # Convertir el diccionario a lista
        inventario_resumido = list(inventario_agrupado.values())
            
        # Yearly Sales Timeline - Last 3 Years
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        timeline_data = {}
        
        for y in range(int(year) - 2, int(year) + 1):
            ventas_anuales = []
            for m in range(1, 13):
                try:
                    s_month = servicios_df[(servicios_df['fecha'].dt.year == y) & 
                                           (servicios_df['fecha'].dt.month == m)]
                    p_month = productos_df[(productos_df['fecha'].dt.year == y) & 
                                           (productos_df['fecha'].dt.month == m)]
                    total = s_month['valor'].sum() + p_month['valor'].sum()
                    ventas_anuales.append(float(total))
                except:
                    ventas_anuales.append(0.0)
            timeline_data[str(y)] = ventas_anuales
        
        # Top Servicios (Frecuencia)
        top_servicios = servicios_month['servicio'].value_counts().head(10).to_dict()
        
        # Estado Inventario
        disponibles = 0
        agotados = 0
        for _, row in inventario_df.iterrows():
            try:
                qty = float(row['cantidad']) if pd.notna(row['cantidad']) else 0
                if qty > 0:
                    disponibles += 1
                else:
                    agotados += 1
            except:
                pass
        
        estado_inventario = {
            'Disponibles': disponibles,
            'Agotados': agotados
        }
        
        return jsonify({
            'status': 'success',
            'data': {
                'totales': {
                    'ventas': float(total_ventas),
                    'gastos': float(total_gastos),
                    'nomina': float(total_nomina),
                    'utilidad_operativa': float(utilidad_operativa),
                    'gastos_fijos': float(total_gastos_fijos),
                    'utilidad_real': float(utilidad_real)
                },
                'gastos_mensuales_detalle': gastos_mensuales_month[['tipo', 'valor']].to_dict(orient='records'),
                'nomina_por_estilista': {k: float(v) for k, v in nomina_por_estilista.items()},
                'ventas_por_estilista': {k: float(v) for k, v in ventas_por_estilista.items()},
                'top_servicios': top_servicios,
                'estado_inventario': estado_inventario,
                'inventario': inventario_resumido,
                'timeline': timeline_data
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/appointment', methods=['POST'])
def add_appointment():
    try:
        import uuid
        data = request.json
        sede = data.get('sede', 'Principal')
        record = {
            'id': str(uuid.uuid4()),
            'sede': sede,
            'fecha': data['fecha'],
            'hora': data['hora'],
            'cliente': data['cliente'],
            'telefono': data['telefono'],
            'servicio': data['servicio'],
            'notas': data.get('notas', ''),
            'estado': 'Pendiente'
        }
        
        if insert_record('citas', record):
            return jsonify({'status': 'success', 'message': 'Cita agendada correctamente'})
        return jsonify({'status': 'error', 'message': 'Error al guardar la cita'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/appointment/<appointment_id>', methods=['DELETE'])
def delete_appointment(appointment_id):
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute('DELETE FROM citas WHERE id = ?', (appointment_id,))
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Cita eliminada correctamente'})
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cita no encontrada'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/appointment/<appointment_id>', methods=['PUT'])
def update_appointment(appointment_id):
    try:
        data = request.json
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if updating only status or multiple fields
        if 'estado' in data and len(data) == 1:
            c.execute('UPDATE citas SET estado = ? WHERE id = ?', (data['estado'], appointment_id))
        else:
            # Multi-field update (from original code logic)
            fields = []
            values = []
            if 'fecha' in data:
                fields.append('fecha = ?')
                values.append(data['fecha'])
            if 'hora' in data:
                fields.append('hora = ?')
                values.append(data['hora'])
            if 'cliente' in data:
                fields.append('cliente = ?')
                values.append(data['cliente'])
            if 'telefono' in data:
                fields.append('telefono = ?')
                values.append(data['telefono'])
            if 'servicio' in data:
                fields.append('servicio = ?')
                values.append(data['servicio'])
            if 'notas' in data:
                fields.append('notas = ?')
                values.append(data['notas'])
            if 'estado' in data:
                fields.append('estado = ?')
                values.append(data['estado'])
            
            if fields:
                values.append(appointment_id)
                query = f"UPDATE citas SET {', '.join(fields)} WHERE id = ?"
                c.execute(query, values)
        
        if c.rowcount > 0:
            conn.commit()
            conn.close()
            return jsonify({'status': 'success', 'message': 'Cita actualizada correctamente'})
        
        conn.close()
        return jsonify({'status': 'error', 'message': 'Cita no encontrada'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/appointments', methods=['GET'])
def get_appointments():
    try:
        date_filter = request.args.get('date')
        sede_filter = request.args.get('sede', 'Principal')
        
        conn = get_db_connection()
        query = "SELECT * FROM citas WHERE sede = ?"
        params = [sede_filter]
        
        if date_filter:
            query += " AND date(fecha) = ?"
            params.append(date_filter)
            
        df = pd.read_sql(query, conn, params=params)
        conn.close()
            
        df = df.fillna('')
        
        # Sort by Time
        try:
            df = df.sort_values('hora')
        except:
            pass

        appointments = df.to_dict(orient='records')
        return jsonify({'status': 'success', 'data': appointments})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    try:
        today = datetime.now().strftime('%Y-%m-%d')
        
        conn = get_db_connection()
        query = "SELECT count(*) as count FROM citas WHERE date(fecha) = ?"
        c = conn.cursor()
        c.execute(query, (today,))
        count = c.fetchone()['count']
        conn.close()
        
        alerts = []
        if count > 0:
            alerts.append({
                'type': 'info',
                'message': f'Tienes {count} cita(s) programada(s) para hoy.'
            })
            
        return jsonify({'status': 'success', 'alerts': alerts})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/monthly-expenses', methods=['POST'])
@login_required
def add_update_monthly_expenses():
    try:
        data = request.json
        sede = data.get('sede', 'Principal')
        mes = data.get('mes')  # YYYY-MM
        expenses = data.get('expenses', [])  # List of {tipo: '...', valor: ...}
        
        if not mes or not expenses:
             return jsonify({'status': 'error', 'message': 'Datos incompletos'}), 400

        conn = get_db_connection()
        c = conn.cursor()
        
        # Create a timestamp
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # We want to replace existing entries for this Sede + Mes + Tipo, or append if new
        for exp in expenses:
            tipo = exp['tipo']
            valor = float(exp['valor'])
            
            # Check if exists
            c.execute('SELECT id FROM gastos_mensuales WHERE sede = ? AND mes = ? AND tipo = ?', 
                      (sede, mes, tipo))
            row = c.fetchone()
            
            if row:
                # Update
                c.execute('UPDATE gastos_mensuales SET valor = ?, fecha_registro = ? WHERE id = ?', 
                          (valor, now, row['id']))
            else:
                # Add new
                c.execute('INSERT INTO gastos_mensuales (sede, mes, tipo, valor, fecha_registro) VALUES (?, ?, ?, ?, ?)', 
                          (sede, mes, tipo, valor, now))

        conn.commit()
        conn.close()
            
        return jsonify({'status': 'success', 'message': 'Gastos mensuales guardados correctamente'})

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/monthly-expenses', methods=['GET'])
@login_required
def get_monthly_expenses():
    try:
        sede = request.args.get('sede', 'Principal')
        mes = request.args.get('mes') # YYYY-MM
        
        conn = get_db_connection()
        query = "SELECT * FROM gastos_mensuales WHERE sede = ?"
        params = [sede]
        
        if mes:
            query += " AND mes = ?"
            params.append(mes)
            
        df = pd.read_sql(query, conn, params=params)
        conn.close()
            
        df = df.fillna('')
        data = df.to_dict(orient='records')
        return jsonify({'status': 'success', 'data': data})
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/prediction', methods=['GET'])
@login_required
def get_prediction():
    try:
        sede_filter = request.args.get('sede', 'Principal')
        
        conn = get_db_connection()
        # Load data
        df_servicios = pd.read_sql("SELECT fecha, valor FROM servicios WHERE sede = ?", conn, params=(sede_filter,))
        df_productos = pd.read_sql("SELECT fecha, valor FROM productos WHERE sede = ?", conn, params=(sede_filter,))
        conn.close()
        
        # Convert fecha to datetime and floor to date
        df_servicios['fecha'] = pd.to_datetime(df_servicios['fecha'], errors='coerce')
        df_productos['fecha'] = pd.to_datetime(df_productos['fecha'], errors='coerce')
        
        # Drop invalid dates and convert to date object
        df_servicios = df_servicios.dropna(subset=['fecha'])
        df_productos = df_productos.dropna(subset=['fecha'])
        
        df_servicios['fecha'] = df_servicios['fecha'].dt.date
        df_productos['fecha'] = df_productos['fecha'].dt.date
        
        # Aggregate by date
        daily_servicios = df_servicios.groupby('fecha')['valor'].sum()
        daily_productos = df_productos.groupby('fecha')['valor'].sum()
        
        # Combine
        daily_income = daily_servicios.add(daily_productos, fill_value=0).sort_index()
        
        # Convert to DataFrame
        income_df = daily_income.reset_index()
        income_df.columns = ['fecha', 'valor']
        
        # Get last 11 months of data (approximately 330 days)
        today = datetime.now().date()
        eleven_months_ago = today - pd.Timedelta(days=330)
        income_df = income_df[income_df['fecha'] >= eleven_months_ago]
        
        if income_df.empty:
            return jsonify({'status': 'success', 'historical': [], 'prediction': []})
            
        # Prepare for prediction (Linear Regression)
        import numpy as np
        
        income_df['ordinal'] = income_df['fecha'].apply(lambda x: x.toordinal())
        X = income_df['ordinal'].values.reshape(-1, 1)
        y = income_df['valor'].values
        
        # Simple Linear Regression: y = mx + b
        if len(income_df) > 1:
            n = len(X)
            sum_x = np.sum(X)
            sum_y = np.sum(y)
            sum_xx = np.sum(X**2)
            sum_xy = np.sum(X * y.reshape(-1, 1))
            
            denominator = (n * sum_xx - sum_x**2)
            if denominator == 0:
                slope = 0
                intercept = np.mean(y)
            else:
                slope = (n * sum_xy - sum_x * sum_y) / denominator
                intercept = (sum_y - slope * sum_x) / n
        else:
            slope = 0
            intercept = y[0] if len(y) > 0 else 0
            
        # Generate next 7 days
        predictions = []
        last_date = income_df['fecha'].max()
        for i in range(1, 8):
            pred_date = last_date + pd.Timedelta(days=i)
            pred_ordinal = pred_date.toordinal()
            pred_value = max(0, slope * pred_ordinal + intercept)
            predictions.append({
                'fecha': pred_date.strftime('%Y-%m-%d'),
                'valor': float(pred_value)
            })
            
        historical = []
        for _, row in income_df.iterrows():
            historical.append({
                'fecha': row['fecha'].strftime('%Y-%m-%d'),
                'valor': float(row['valor'])
            })
            
        return jsonify({
            'status': 'success',
            'historical': historical,
            'prediction': predictions,
            'trend': 'up' if slope > 0 else 'down' if slope < 0 else 'stable'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/revenue-patterns', methods=['GET'])
@login_required
def get_revenue_patterns():
    try:
        sede_filter = request.args.get('sede', 'Principal')
        
        conn = get_db_connection()
        # Load data
        df_servicios = pd.read_sql("SELECT fecha, valor FROM servicios WHERE sede = ?", conn, params=(sede_filter,))
        df_productos = pd.read_sql("SELECT fecha, valor FROM productos WHERE sede = ?", conn, params=(sede_filter,))
        conn.close()
        
        # Convert fecha
        df_servicios['fecha'] = pd.to_datetime(df_servicios['fecha'], errors='coerce')
        df_productos['fecha'] = pd.to_datetime(df_productos['fecha'], errors='coerce')
        
        # Drop invalid and convert to date
        df_servicios = df_servicios.dropna(subset=['fecha'])
        df_productos = df_productos.dropna(subset=['fecha'])
        
        df_servicios['fecha'] = df_servicios['fecha'].dt.date
        df_productos['fecha'] = df_productos['fecha'].dt.date
        
        # Group by date
        daily_servicios = df_servicios.groupby('fecha')['valor'].sum()
        daily_productos = df_productos.groupby('fecha')['valor'].sum()
        
        daily_revenue = daily_servicios.add(daily_productos, fill_value=0).sort_index()
        
        # Reset index
        df = daily_revenue.reset_index()
        df.columns = ['fecha', 'valor']
        
        # Use all historical data (no date filter)
        if df.empty:
            return jsonify({'status': 'success', 'heatmap': [], 'patterns': {}, 'inference': 'Datos insuficientes'})
            
        # 1. Heatmap Data (Week vs Day)
        heatmap_data = []
        for _, row in df.iterrows():
            dt = pd.to_datetime(row['fecha'])
            heatmap_data.append({
                'date': row['fecha'].strftime('%Y-%m-%d'),
                'day': dt.day_name(), 
                'day_index': dt.dayofweek, # 0=Mon
                'week': int(dt.isocalendar()[1]),
                'value': float(row['valor'])
            })
            
        # 2. Average Stats by Day of Week
        df['dayofweek'] = pd.to_datetime(df['fecha']).dt.dayofweek
        patterns = df.groupby('dayofweek')['valor'].mean().to_dict()
        
        day_map = {0: 'Lunes', 1: 'Martes', 2: 'Miércoles', 3: 'Jueves', 4: 'Viernes', 5: 'Sábado', 6: 'Domingo'}
        named_patterns = {day_map[k]: float(v) for k, v in patterns.items()}
        
        # 3. Inference
        sorted_days = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_days) >= 2:
            best_day_1 = day_map[sorted_days[0][0]]
            best_day_2 = day_map[sorted_days[1][0]]
            inference = f"Basado en todos los datos históricos, los días con mayor probabilidad de altos ingresos son los {best_day_1} y {best_day_2}."
        elif len(sorted_days) == 1:
            best_day = day_map[sorted_days[0][0]]
            inference = f"Basado en todos los datos históricos, el día con mayor probabilidad de altos ingresos es el {best_day}."
        else:
            inference = "No hay suficientes datos para generar una inferencia."
            
        return jsonify({
            'status': 'success', 
            'heatmap': heatmap_data, 
            'patterns': named_patterns, 
            'inference': inference
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/service-demand', methods=['GET'])
@login_required
def get_service_demand():
    try:
        import numpy as np
        sede_filter = request.args.get('sede', 'Principal')
        
        conn = get_db_connection()
        # Load services data
        df_servicios = pd.read_sql("SELECT fecha, servicio, sede FROM servicios WHERE sede = ?", conn, params=(sede_filter,))
        conn.close()
        
        if df_servicios.empty:
             return jsonify({'status': 'success', 'historical': [], 'prediction': [], 'growthService': None})

        # Convert fecha
        df_servicios['fecha'] = pd.to_datetime(df_servicios['fecha'], errors='coerce')
        df_servicios = df_servicios.dropna(subset=['fecha'])
        df_servicios['fecha'] = df_servicios['fecha'].dt.date
        
        # Filter last 60 days
        today = datetime.now().date()
        sixty_days_ago = today - pd.Timedelta(days=60)
        df_recent = df_servicios[df_servicios['fecha'] >= sixty_days_ago].copy()
        
        if df_recent.empty:
            return jsonify({'status': 'success', 'historical': [], 'prediction': [], 'growthService': None})

        # Categorize Services
        def categorize_service(name):
            name = str(name).lower()
            if 'corte' in name: return 'Corte'
            if 'tinte' in name or 'mechas' in name or 'color' in name or 'iluminaciones' in name or 'keratina' in name: return 'Tintura'
            if 'manicure' in name or 'pedicure' in name or 'uñas' in name or 'semi' in name: return 'Uñas'
            if 'depilacion' in name or 'cejas' in name or 'cera' in name or 'bigote' in name: return 'Depilación'
            return 'Otros'

        df_recent['tipo'] = df_recent['servicio'].apply(categorize_service)
        
        # Filter only expected types
        expected = ['Corte', 'Tintura', 'Uñas', 'Depilación']
        df_recent = df_recent[df_recent['tipo'].isin(expected)]
        
        # Group by Date and Tipo
        daily_counts = df_recent.groupby(['fecha', 'tipo']).size().reset_index(name='count')
        
        # Pivot
        pivot_df = daily_counts.pivot(index='fecha', columns='tipo', values='count').fillna(0).astype(int)
        
        # Ensure all columns exist
        for col in expected:
            if col not in pivot_df.columns:
                pivot_df[col] = 0
                
        # Prepare Historical Data
        historical = []
        # Sort by date
        pivot_df = pivot_df.sort_index()
        
        for date_val, row in pivot_df.iterrows():
            entry = {'fecha': date_val.strftime('%Y-%m-%d')}
            for col in expected:
                entry[col] = int(row[col])
            historical.append(entry)
            
        # Prediction
        predictions = []
        growth_scores = {}
        
        # Create a date range for regression X to be accurate
        dates = pivot_df.index
        X_dates = np.array([d.toordinal() for d in dates])
        
        last_date = dates.max()
        next_7_days = [last_date + pd.Timedelta(days=i) for i in range(1, 8)]
        next_7_ordinals = np.array([d.toordinal() for d in next_7_days])
        
        for col in expected:
            y = pivot_df[col].values
            X = X_dates.reshape(-1, 1)
            
            if len(y) > 1:
                # Linear Regression
                n = len(X)
                sum_x = np.sum(X)
                sum_y = np.sum(y)
                sum_xx = np.sum(X**2)
                sum_xy = np.sum(X.flatten() * y)
                
                denom = n * sum_xx - sum_x**2
                if denom == 0:
                    slope = 0
                    intercept = np.mean(y)
                else:
                    slope = (n * sum_xy - sum_x * sum_y) / denom
                    intercept = (sum_y - slope * sum_x) / n
            else:
                slope = 0
                intercept = y[0] if len(y) > 0 else 0
                
            growth_scores[col] = slope
            
            col_preds = []
            for ordinal in next_7_ordinals:
                val = slope * ordinal + intercept
                col_preds.append(max(0, val)) 
            
            # We need to structure 'predictions' as list of dicts: [{fecha:..., Corte:..., ...}, ...]
            if not predictions:
                for d in next_7_days:
                    predictions.append({'fecha': d.strftime('%Y-%m-%d')})
            
            for i, val in enumerate(col_preds):
                predictions[i][col] = float(val)

        # Determine highest growth
        if growth_scores:
            growth_service = max(growth_scores, key=growth_scores.get)
        else:
            growth_service = None

        return jsonify({
            'status': 'success',
            'historical': historical,
            'prediction': predictions,
            'growthService': growth_service
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/<table_name>', methods=['GET'])
@login_required
def admin_get_records(table_name):
    allowed_tables = ['servicios', 'productos', 'gastos', 'inventario', 'citas', 'gastos_mensuales']
    if table_name not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Tabla no permitida'}), 400
        
    try:
        sede = request.args.get('sede')
        fecha = request.args.get('fecha')
        limit = request.args.get('limit', '100')
        offset = request.args.get('offset', '0')
        
        conn = get_db_connection()
        query = f"SELECT * FROM {table_name}"
        params = []
        where_clauses = []
        
        if sede:
            where_clauses.append("sede = ?")
            params.append(sede)
        if fecha:
            where_clauses.append("date(fecha) = ?")
            params.append(fecha)
            
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            
        query += " ORDER BY id DESC"
        
        if limit:
            query += f" LIMIT {int(limit)}"
        if offset:
            query += f" OFFSET {int(offset)}"
            
        df = pd.read_sql(query, conn, params=params)
        conn.close()
        
        return jsonify({
            'status': 'success', 
            'data': df.to_dict(orient='records'),
            'columns': list(df.columns)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/<table_name>/<id>', methods=['GET'])
@login_required
def admin_get_record(table_name, id):
    allowed_tables = ['servicios', 'productos', 'gastos', 'inventario', 'citas', 'gastos_mensuales']
    if table_name not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Tabla no permitida'}), 400
        
    try:
        conn = get_db_connection()
        query = f"SELECT * FROM {table_name} WHERE id = ?"
        df = pd.read_sql(query, conn, params=(id,))
        conn.close()
        
        if df.empty:
            return jsonify({'status': 'error', 'message': 'Registro no encontrado'}), 404
            
        return jsonify({'status': 'success', 'data': df.to_dict(orient='records')[0]})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/<table_name>', methods=['POST'])
@login_required
def admin_create_record(table_name):
    allowed_tables = ['servicios', 'productos', 'gastos', 'inventario', 'citas', 'gastos_mensuales']
    if table_name not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Tabla no permitida'}), 400
        
    try:
        data = request.json
        if insert_record(table_name, data):
            return jsonify({'status': 'success', 'message': 'Registro creado'})
        return jsonify({'status': 'error', 'message': 'Error al insertar'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/<table_name>/<id>', methods=['PUT'])
@login_required
def admin_update_record(table_name, id):
    allowed_tables = ['servicios', 'productos', 'gastos', 'inventario', 'citas', 'gastos_mensuales']
    if table_name not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Tabla no permitida'}), 400
        
    try:
        data = request.json
        conn = get_db_connection()
        c = conn.cursor()
        
        set_clause = ", ".join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE id = ?"
        params = list(data.values()) + [id]
        
        c.execute(query, params)
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Registro actualizado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/admin/<table_name>/<id>', methods=['DELETE'])
@login_required
def admin_delete_record(table_name, id):
    allowed_tables = ['servicios', 'productos', 'gastos', 'inventario', 'citas', 'gastos_mensuales']
    if table_name not in allowed_tables:
        return jsonify({'status': 'error', 'message': 'Tabla no permitida'}), 400
        
    try:
        conn = get_db_connection()
        c = conn.cursor()
        c.execute(f"DELETE FROM {table_name} WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success', 'message': 'Registro eliminado'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', debug=True)
