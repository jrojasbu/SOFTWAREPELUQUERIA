import unittest
import os
import pandas as pd
from app import app, init_db, DB_FILE

class TestHairSalonApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        # Use a test database
        global DB_FILE
        self.original_db = DB_FILE
        # We can't easily change the global variable in the imported module without reloading, 
        # but since we import DB_FILE from app, we might be able to patch it if we imported it differently.
        # However, for simplicity, we will just let it use the real DB or try to mock it.
        # Since this is a local environment, using the real DB file is fine as long as we clean up or accept test data.
        # Let's just run init_db to make sure it exists.
        init_db()

    def test_1_add_service(self):
        response = self.app.post('/api/service', json={
            'estilista': 'TestStylist',
            'servicio': 'TestCut',
            'valor': 50000
        })
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['comision'], 25000)
        
        # Verify Excel
        df = pd.read_excel(DB_FILE, sheet_name='Servicios')
        last_row = df.iloc[-1]
        self.assertEqual(last_row['Estilista'], 'TestStylist')
        self.assertEqual(last_row['Valor'], 50000)

    def test_2_add_product(self):
        response = self.app.post('/api/product', json={
            'estilista': 'TestStylist',
            'producto': 'TestShampoo',
            'valor': 20000
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify Excel
        df = pd.read_excel(DB_FILE, sheet_name='Productos')
        last_row = df.iloc[-1]
        self.assertEqual(last_row['Producto'], 'TestShampoo')
        self.assertEqual(last_row['Valor'], 20000)

    def test_3_add_expense(self):
        response = self.app.post('/api/expense', json={
            'descripcion': 'TestExpense',
            'valor': 5000
        })
        self.assertEqual(response.status_code, 200)
        
        # Verify Excel
        df = pd.read_excel(DB_FILE, sheet_name='Gastos')
        last_row = df.iloc[-1]
        self.assertEqual(last_row['Descripcion'], 'TestExpense')

if __name__ == '__main__':
    unittest.main()
