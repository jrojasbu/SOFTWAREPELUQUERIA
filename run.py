import os
import sys
import webbrowser
from threading import Timer
from app import app, init_db

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    try:
        # ── Establecer el directorio de trabajo en la carpeta del exe/script ──
        # Esto garantiza que database.db y los .json siempre se lean/escriban
        # en la misma carpeta que el ejecutable, sin importar desde dónde se lance.
        if getattr(sys, 'frozen', False):
            # Modo compilado (.exe)
            app_dir = os.path.dirname(sys.executable)
            template_folder = os.path.join(sys._MEIPASS, 'templates')
            static_folder = os.path.join(sys._MEIPASS, 'static')
            app.template_folder = template_folder
            app.static_folder = static_folder
            print(f"Running in frozen mode.")
            print(f"Executable folder: {app_dir}")
            print(f"Templates: {template_folder}")
            print(f"Static: {static_folder}")
        else:
            # Modo script Python normal
            app_dir = os.path.dirname(os.path.abspath(__file__))
            print(f"Running in script mode.")
            print(f"Script folder: {app_dir}")

        # Cambiar el directorio de trabajo a la carpeta del exe/script
        os.chdir(app_dir)
        print(f"Working directory set to: {app_dir}")

        # Inicializar base de datos
        print("Initializing database...")
        init_db()

        # Abrir navegador después de 1.5 segundos
        print("Starting browser...")
        Timer(1.5, open_browser).start()

        # Ejecutar app
        print("Starting server on port 5000...")
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    except Exception as e:
        print("\nCRITICAL ERROR:")
        print(str(e))
        import traceback
        traceback.print_exc()
        print("\nPress Enter to close...")
        input()
