# Business Income API

API REST para gestionar estadísticas de ingresos de negocios.

## Stack técnico

- **Framework:** FastAPI
- **Validación:** Pydantic v2
- **Base de datos:** MySQL / MariaDB
- **Autenticación:** JWT (Bearer token)

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
```

2. Activar entorno virtual:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con las credenciales de la base de datos
```

## Ejecución

Desarrollo:
```bash
fastapi dev
```

Producción:
```bash
fastapi run
```

## Endpoints

- `POST /api/v1/auth/login` - Autenticación JWT
- `GET /api/v1/ingresos/diarios?fecha=YYYY-MM-DD` - Ingresos de un día
- `GET /api/v1/ingresos/rango?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Total por rango
- `GET /api/v1/ingresos/grafica?fecha_inicio=YYYY-MM-DD&fecha_fin=YYYY-MM-DD` - Datos para gráfica

## Estructura

```
app/
├── api/v1/endpoints/  - Routers de endpoints
├── core/              - Configuración, seguridad, dependencias
├── db/                - Conexión a base de datos
├── schemas/           - Modelos Pydantic
└── main.py            - Entry point
```
