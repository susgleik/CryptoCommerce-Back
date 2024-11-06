# scripts/init_db.py
from sqlalchemy import create_engine
from decouple import config
import time

def wait_for_db():
    """Espera hasta que la base de datos esté disponible"""
    db_url = f"mysql+pymysql://{config('DB_USER')}:{config('DB_PASSWORD')}@{config('DB_HOST')}:{config('DB_PORT')}/{config('DB_NAME')}"
    
    max_retries = 30
    retry_interval = 2
    
    for i in range(max_retries):
        try:
            engine = create_engine(db_url)
            engine.connect()
            print("🟢 Conexión exitosa a la base de datos")
            return True
        except Exception as e:
            print(f"🟡 Intento {i+1} de {max_retries}: No se pudo conectar a la base de datos. Reintentando en {retry_interval} segundos...")
            print(f"Error: {str(e)}")
            time.sleep(retry_interval)
    
    print("🔴 No se pudo establecer conexión con la base de datos después de varios intentos")
    return False

if __name__ == "__main__":
    wait_for_db()