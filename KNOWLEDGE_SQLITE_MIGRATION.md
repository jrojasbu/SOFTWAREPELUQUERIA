# SQLite Migration Patterns

The application has been migrated from Excel (`database.xlsx`) to SQLite (`database.db`).

## Database Connection
A helper function `get_db_connection()` is used to establish connections:
```python
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn
```

## Schema
The database contains the following tables:
- `servicios`: id, sede, fecha, estilista, servicio, valor, comision, metodo_pago
- `productos`: id, sede, fecha, estilista, producto, marca, descripcion, valor, comision, metodo_pago
- `gastos`: id, sede, fecha, descripcion, valor
- `inventario`: id, sede, producto, marca, descripcion, cantidad, unidad, valor, estado, fecha_actualizacion
- `citas`: id (UUID), sede, fecha, hora, cliente, telefono, servicio, notas, estado
- `gastos_mensuales`: id, sede, mes, tipo, valor, fecha_registro

## Key Implementation Patterns

### Data Retrieval
Use `pd.read_sql` for easy conversion to dictionaries or when complex analysis is needed:
```python
conn = get_db_connection()
df = pd.read_sql("SELECT * FROM servicios WHERE sede = ?", conn, params=(sede_filter,))
conn.close()
```

### Record Insertion
A generic `insert_record(table, data)` function is provided:
```python
def insert_record(table, data):
    data = {k.lower(): v for k, v in data.items()}
    columns = ', '.join(data.keys())
    placeholders = ', '.join(['?' for _ in data])
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    # ... execute ...
```

### Inventory Updates
Inventory is updated atomically using SQL when a product is sold:
```python
c.execute('UPDATE inventario SET cantidad = ?, estado = ? WHERE id = ?', (new_qty, status, row['id']))
```

### Date Filtering
SQLite `date()` function is used for filtering by date strings:
```sql
SELECT * FROM servicios WHERE date(fecha) = ?
```
