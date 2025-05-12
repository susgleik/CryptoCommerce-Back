# app/database/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from decouple import config
from sqlalchemy.pool import QueuePool

# Construir URL de conexión desde variables de entorno
DATABASE_URL = "mysql+pymysql://root:123456@host.docker.internal:3306/ecommerce"

print(DATABASE_URL)

# Configuración del engine con retry
engine = create_engine(
    DATABASE_URL,
    pool_size=5,
    max_overflow=10,
    poolclass=QueuePool,
    pool_pre_ping=True,  # Verifica la conexión antes de usarla
    pool_recycle=3600,   # Recicla conexiones después de una hora
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Inicializa la base de datos creando todas las tablas"""
    Base.metadata.create_all(bind=engine)