# app/database/database.py
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config import settings
import logging 

if settings.db_testing_mode:
    print(f'database url:{settings.database_url}')
    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    print(f'🔗 Conectando a Azure MySQL: {settings.db_host}')
    print(f'📊 Base de datos: {settings.db_name}')
    print(f'👤 Usuario: {settings.db_user}')

# Configuración del engine con retry
engine = create_engine(
    settings.database_url,
    pool_size=5,
    max_overflow=10,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_recycle=3600,   # Recicla conexiones después de una hora
    
    # azure SQL config
    connect_args={
        "charset": "utf8mb4",
        "autocommit": False,
        "ssl_disabled": False,  # SSL requerido en Azure
        "connect_timeout": 30,   # Timeout de conexión
        "read_timeout": 30,      # Timeout de lectura
        "write_timeout": 30,     # Timeout de escritura
    },
    # echo to debug
    #echo=settings.debug, 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
def test_connection():
    """Check the db conection"""
    try:
        if settings.db_testing_mode:
            print("Probando conexión a Azure MySQL...")

        # Crear una conexión temporal
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1 as test, VERSION() as version"))
            test_result = result.fetchone()

            if test_result[0] == 1:
                if settings.db_testing_mode:
                    print("Conexión a Azure MySQL exitosa!")
                    print(f"Versión MySQL: {test_result[1]}")

                # Verificar tablas existentes
                tables_result = connection.execute(text("SHOW TABLES"))
                tables = tables_result.fetchall()

                if settings.db_testing_mode:
                    print(f"Tablas encontradas: {len(tables)}")

                return True
            else:
                if settings.db_testing_mode:
                    print("Error en la conexión a Azure MySQL")
                return False

    except Exception as e:
        if settings.db_testing_mode:
            print(f"Error conectando a Azure MySQL: {str(e)}")
        return False

def verify_tables():
    """Check the important tables"""
    required_tables = [
        'USERS', 'PRODUCTS', 'CATEGORIES', 'SUPPLIERS',
        'PAYMENT_METHODS', 'SHOPPING_CARTS', 'ORDERS'
    ]

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SHOW TABLES"))
            existing_tables = [row[0] for row in result.fetchall()]

            missing_tables = [table for table in required_tables if table not in existing_tables]

            if missing_tables:
                if settings.db_testing_mode:
                    print(f"Tablas faltantes: {missing_tables}")
                return False
            else:
                if settings.db_testing_mode:
                    print("Todas las tablas requeridas existen")
                return True

    except Exception as e:
        if settings.db_testing_mode:
            print(f"Error verificando tablas: {str(e)}")
        return False


def init_db():
    """Inicializa la base de datos"""
    try:
        if settings.db_testing_mode:
            print("Verificando estructura de la base de datos...")

        if test_connection():
            if verify_tables():
                print("Base de datos BookStore lista para usar!")
                return True
            else:
                if settings.db_testing_mode:
                    print("Algunas tablas están faltando. Ejecuta el script SQL desde Workbench.")
                return False
        else:
            if settings.db_testing_mode:
                print("No se puede conectar a la base de datos")
            return False

    except Exception as e:
        if settings.db_testing_mode:
            print(f"Error inicializando base de datos: {str(e)}")
        return False