# E-Commerce API

API REST para un sistema de e-commerce desarrollado con FastAPI y MySQL en Azure.

## Tabla de Contenidos

- [Descripción](#descripción)
- [Tecnologías](#tecnologías)
- [Arquitectura](#arquitectura)
- [Requisitos Previos](#requisitos-previos)
- [Instalación](#instalación)
- [Configuración](#configuración)
- [Ejecución](#ejecución)
- [Endpoints Principales](#endpoints-principales)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Características](#características)

## Descripción

Sistema backend de e-commerce completo que ofrece funcionalidades de gestión de productos, usuarios, categorías, carrito de compras, órdenes y más. Diseñado con arquitectura en capas y mejores prácticas de desarrollo.

## Tecnologías

### Backend
- **FastAPI** v0.104.1 - Framework web moderno para Python
- **Python** 3.11
- **Uvicorn** - Servidor ASGI

### Base de Datos
- **MySQL** - Hospedado en Azure
- **SQLAlchemy** 2.0.23 - ORM
- **PyMySQL** - Conector MySQL

### Autenticación y Seguridad
- **JWT** (JSON Web Tokens)
- **bcrypt** - Hash de contraseñas
- Sistema de roles: `common`, `admin`, `store_staff`

### DevOps
- **Docker** - Containerización
- **Docker Compose** - Orquestación

## Arquitectura

El proyecto sigue una **arquitectura en capas** con separación clara de responsabilidades:

```
┌─────────────────────────────────────┐
│     API Layer (routes/)             │  ← Endpoints REST
├─────────────────────────────────────┤
│  Service Layer (services/)          │  ← Lógica de negocio
├─────────────────────────────────────┤
│   Data Layer (models/)              │  ← Modelos ORM
├─────────────────────────────────────┤
│  Database (MySQL Azure)             │  ← Persistencia
└─────────────────────────────────────┘
```

## Requisitos Previos

- **Docker** >= 20.10
- **Docker Compose** >= 2.0
- **Git**
- Cuenta de Azure con MySQL configurado (o MySQL local)

## Instalación

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd book-store-backend
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
# Database Configuration (Azure MySQL)
DB_USER=tu_usuario
DB_PASSWORD=tu_contraseña
DB_NAME=nombre_base_datos
DB_HOST=tu-servidor.mysql.database.azure.com
DB_PORT=3306
DATABASE_URL=mysql+pymysql://${DB_USER}:${DB_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME}

# Security
SECRET_KEY=tu_clave_secreta_muy_segura_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# SMTP Configuration (opcional)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu-email@gmail.com
SMTP_PASSWORD=tu-app-password

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000
ALLOWED_METHODS=GET,POST,PUT,DELETE,OPTIONS
ALLOWED_HEADERS=*

# Database Testing Mode (opcional)
DB_TESTING_MODE=false
```

### 3. Inicializar la Base de Datos

Si estás usando Azure MySQL, ejecuta el script SQL proporcionado:

```bash
# Conéctate a tu instancia de MySQL y ejecuta:
mysql -h tu-servidor.mysql.database.azure.com -u tu_usuario -p < data.sql
```

## Configuración

### Variables de Entorno Importantes

| Variable | Descripción | Requerido | Default |
|----------|-------------|-----------|---------|
| `DB_USER` | Usuario de MySQL | Sí | - |
| `DB_PASSWORD` | Contraseña de MySQL | Sí | - |
| `DB_NAME` | Nombre de la base de datos | Sí | - |
| `DB_HOST` | Host de MySQL | Sí | - |
| `SECRET_KEY` | Clave secreta para JWT | Sí | - |
| `DB_TESTING_MODE` | Mostrar logs de DB | No | `false` |

### Modo de Testing de Base de Datos

Para activar logs detallados de la base de datos durante desarrollo:

```bash
DB_TESTING_MODE=true
```

Cuando está en `false`, solo se muestran mensajes importantes, manteniendo los logs limpios.

## Ejecución

### Opción 1: Con Docker (Recomendado)

#### Construir la imagen:

```bash
docker-compose build
```

#### Iniciar el servicio:

```bash
docker-compose up
```

#### Iniciar en segundo plano:

```bash
docker-compose up -d
```

#### Ver logs:

```bash
docker-compose logs -f api
```

#### Detener el servicio:

```bash
docker-compose down
```

La API estará disponible en: **http://localhost:8000**

### Opción 2: Sin Docker (Desarrollo Local)

#### Instalar dependencias:

```bash
pip install -r requirements.txt
```

#### Ejecutar el servidor:

```bash
python main.py
```

O con uvicorn directamente:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints Principales

### Documentación Interactiva

Una vez iniciada la aplicación, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints Públicos

```
GET  /                     - Mensaje de bienvenida
GET  /health              - Health check
POST /api/v1/auth/register - Registro de usuarios
POST /api/v1/auth/login    - Inicio de sesión
```

### Endpoints Protegidos (Requieren Token)

#### Usuarios
```
GET    /api/v1/users/me          - Obtener perfil actual
PUT    /api/v1/users/me          - Actualizar perfil
DELETE /api/v1/users/me          - Eliminar cuenta
```

#### Productos
```
GET    /api/v1/products          - Listar productos
GET    /api/v1/products/{id}     - Obtener producto
POST   /api/v1/products          - Crear producto (admin)
PUT    /api/v1/products/{id}     - Actualizar producto (admin)
DELETE /api/v1/products/{id}     - Eliminar producto (admin)
```

#### Categorías
```
GET    /api/v1/categories        - Listar categorías
GET    /api/v1/categories/{id}   - Obtener categoría
POST   /api/v1/categories        - Crear categoría (admin)
PUT    /api/v1/categories/{id}   - Actualizar categoría (admin)
DELETE /api/v1/categories/{id}   - Eliminar categoría (admin)
```

### Autenticación

Todos los endpoints protegidos requieren un token Bearer:

```bash
curl -H "Authorization: Bearer <tu_token>" http://localhost:8000/api/v1/users/me
```

## Estructura del Proyecto

```
book-store-backend/
├── app/
│   ├── auth/                 # Autenticación y autorización
│   │   └── dependencies.py   # Dependencias de auth
│   ├── core/                 # Funcionalidades centrales
│   │   ├── jwt_handler.py    # Manejo de JWT
│   │   ├── security.py       # Funciones de seguridad
│   │   └── dependencies.py   # Dependencias core
│   ├── database/             # Configuración de base de datos
│   │   └── database.py       # Engine y sesiones
│   ├── models/               # Modelos ORM (SQLAlchemy)
│   │   ├── user_model.py
│   │   ├── product_model.py
│   │   ├── cart_model.py
│   │   ├── order_model.py
│   │   └── ...
│   ├── routes/               # Endpoints de la API
│   │   ├── auth/             # Login, registro
│   │   ├── user/             # Gestión de usuarios
│   │   ├── product/          # CRUD de productos
│   │   ├── category/         # Gestión de categorías
│   │   └── __init__.py       # Router principal
│   ├── schemas/              # Schemas Pydantic
│   │   ├── user_schemas.py
│   │   └── product_schemas.py
│   ├── services/             # Lógica de negocio
│   ├── scripts/              # Scripts de utilidad
│   └── config.py             # Configuración global
├── .env                      # Variables de entorno (crear)
├── .gitignore
├── docker-compose.yml        # Configuración Docker Compose
├── dockerfile                # Imagen Docker
├── main.py                   # Punto de entrada
├── requirements.txt          # Dependencias Python
├── data.sql                  # Script inicial de BD
└── README.md                 # Este archivo
```

## Características

### Gestión de Usuarios
- Registro y autenticación con JWT
- Sistema de roles (common, admin, store_staff)
- Perfiles de usuario
- Actualización de contraseñas

### Gestión de Productos
- CRUD completo de productos
- Atributos dinámicos por tipo de producto
- Sistema de SKU único
- Control de stock
- Productos destacados

### Categorías
- Categorías jerárquicas (padre/hijo)
- Relación muchos a muchos con productos
- Estados activo/inactivo

### Proveedores
- Gestión de proveedores
- Relación con productos

### Seguridad
- Tokens JWT con expiración
- Hashing de contraseñas con bcrypt
- CORS configurado
- Validación de datos con Pydantic V2
- SSL habilitado para Azure MySQL

### Base de Datos
- Pool de conexiones optimizado
- Manejo de errores robusto
- Modo de testing para logs
- Auto-reconexión

## Modo de Desarrollo

### Logs de Base de Datos

Por defecto, los logs de la base de datos están desactivados. Para activarlos durante desarrollo:

```bash
# En .env
DB_TESTING_MODE=true
```

Esto mostrará:
- URL de conexión
- Host, usuario y nombre de BD
- Queries SQL ejecutadas
- Estado de tablas

### Hot Reload

El servidor se recarga automáticamente al detectar cambios en el código cuando se ejecuta con:

```bash
uvicorn main:app --reload
```

O con Docker Compose (ya configurado).

## Solución de Problemas

### Error de conexión a la base de datos

Si ves errores como `Can't connect to MySQL server`:

1. Verifica que las credenciales en `.env` sean correctas
2. Asegúrate de tener conexión a internet (si usas Azure)
3. Revisa que el firewall de Azure permita tu IP
4. La aplicación iniciará de todas formas y loggeará el error

### Warnings de Pydantic

Si ves warnings sobre `orm_mode` o `allow_population_by_field_name`, asegúrate de tener la versión correcta:

```bash
pip install pydantic==2.4.2
```

### Puerto 8000 en uso

Si el puerto 8000 está ocupado:

```bash
# Cambiar puerto en docker-compose.yml
ports:
  - "8080:8000"  # Usa puerto 8080 localmente
```

**Desarrollado con FastAPI y Python** 🐍
