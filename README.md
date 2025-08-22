# Gestión de Riesgo de Crédito

Sistema de gestión de riesgo crediticio para evaluación y seguimiento de clientes.

## Características principales

- Evaluación de riesgo crediticio
- Seguimiento de clientes
- Análisis de datos de crédito
- Generación de informes

## Requisitos

- Python 3.8+
- PostgreSQL (recomendado) o SQLite

## Instalación

1. Clonar el repositorio
2. Crear y activar un entorno virtual:
   ```
   python -m venv venv
   .\venv\Scripts\activate  # Windows
   ```
3. Instalar dependencias:
   ```
   pip install -r requirements.txt
   ```
4. Configurar las variables de entorno en `.env`
5. Aplicar migraciones:
   ```
   python manage.py migrate
   ```
6. Crear un superusuario:
   ```
   python manage.py createsuperuser
   ```
7. Iniciar el servidor de desarrollo:
   ```
   python manage.py runserver
   ```

## Estructura del Proyecto

- `gestion_riesgo/` - Configuración principal del proyecto
- `clientes/` - Módulo de gestión de clientes
- `creditos/` - Módulo de análisis de riesgo crediticio
- `informes/` - Generación de informes y análisis

## Licencia

Este proyecto está bajo la licencia MIT.
