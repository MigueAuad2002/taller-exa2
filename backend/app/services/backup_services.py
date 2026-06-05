import os
import subprocess
import glob
import shutil
from datetime import datetime
from app.config import Config

def buscar_pg_dump():
    """
    Función 'Radar' Mejorada: Escanea múltiples discos y carpetas.
    """
    # 1. Si está en las variables de entorno globales, lo usa
    if shutil.which("pg_dump"):
        return "pg_dump"
    
    # 2. Rutas de búsqueda ampliadas (Agregamos el disco D:\)
    rutas_busqueda = [
        r"C:\Program Files\PostgreSQL\*\bin\pg_dump.exe",
        r"C:\Program Files (x86)\PostgreSQL\*\bin\pg_dump.exe",
        r"D:\Program Files\PostgreSQL\*\bin\pg_dump.exe",
        r"D:\PostgreSQL\*\bin\pg_dump.exe",
        r"C:\PostgreSQL\*\bin\pg_dump.exe"
    ]
    
    for ruta in rutas_busqueda:
        coincidencias = glob.glob(ruta)
        if coincidencias:
            # Ordenamos por versión (para agarrar la más nueva si hay varias)
            return sorted(coincidencias)[-1]
            
    # 3. Si no lo encuentra en ningún lado
    raise FileNotFoundError("No se encontró 'pg_dump.exe' automáticamente ni en C:\\ ni en D:\\. Por favor asegúrate de tener PostgreSQL instalado en tu computadora.")

def generar_backup_bd_memoria():
    try:
        fecha_actual = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        nombre_archivo = f"taller_backup_{fecha_actual}.sql"
        
        env = os.environ.copy()
        env['PGPASSWORD'] = Config.DB_PASSWORD

        # --- APLICAMOS LA SOLUCIÓN DINÁMICA ---
        comando_pg_dump = buscar_pg_dump()

        comando = [
            comando_pg_dump, # Usamos la ruta o el comando que el radar encontró
            "-h", Config.DB_HOST,
            "-p", str(Config.DB_PORT),
            "-U", Config.DB_USER,
            "-F", "p", 
            "-O",
            "-x",
            "-n", Config.SCHEMA,
            Config.DB_NAME
        ]

        proceso = subprocess.run(comando, env=env, capture_output=True, text=False, check=True)

        return {
            'file_bytes': proceso.stdout,
            'file_name': nombre_archivo
        }

    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.decode('utf-8', errors='ignore') if e.stderr else str(e)
        print(f"[ERROR de pg_dump] {error_msg}")
        raise RuntimeError(f'Fallo al extraer los datos: {error_msg}')
        
    except Exception as e:
        print(f"[ERROR Backup] {str(e)}")
        raise RuntimeError(f'Error generando el backup: {str(e)}')