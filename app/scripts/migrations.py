# scripts/migrations.py
from alembic import command
from alembic.config import Config
from pathlib import Path
import os

def run_migrations():
    """Ejecuta las migraciones de la base de datos"""
    # Crear directorio de migraciones si no existe
    migrations_dir = Path("migrations")
    if not migrations_dir.exists():
        migrations_dir.mkdir()
    
    # Configurar alembic
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("script_location", "migrations")
    alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
    
    try:
        # Generar migración
        command.revision(alembic_cfg, autogenerate=True, message="Initial migration")
        # Ejecutar migración
        command.upgrade(alembic_cfg, "head")
        print("✅ Migraciones ejecutadas correctamente")
    except Exception as e:
        print(f"❌ Error ejecutando migraciones: {str(e)}")
        raise

if __name__ == "__main__":
    run_migrations()