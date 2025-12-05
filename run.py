import os
import sys
import webbrowser
from threading import Timer
from app import app, init_db

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    try:
        # Si se ejecuta como exe compilado, cambiar el directorio de trabajo al temporal
        if getattr(sys, 'frozen', False):
            template_folder = os.path.join(sys._MEIPASS, 'templates')
            static_folder = os.path.join(sys._MEIPASS, 'static')
            app.template_folder = template_folder
            app.static_folder = static_folder
            print(f"Running in frozen mode.")
            print(f"Templates: {template_folder}")
            print(f"Static: {static_folder}")

        # Inicializar base de datos
        print("Initializing database...")
        init_db()

        # Abrir navegador después de 1.5 segundos
        print("Starting browser...")
        Timer(1.5, open_browser).start()

        # Ejecutar app
        print("Starting server on port 5000...")
        app.run(port=5000, debug=False)
        
    except Exception as e:
        print("\nCRITICAL ERROR:")
        print(str(e))
        import traceback
        traceback.print_exc()
        print("\nPress Enter to close...")
        input()
