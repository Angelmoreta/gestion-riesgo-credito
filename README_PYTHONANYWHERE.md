# Despliegue en PythonAnywhere (sin Docker)

Este proyecto está preparado para desplegarse en PythonAnywhere usando virtualenv y WSGI.

## 1) Subir el código
- Sube el repo a GitHub.
- En PythonAnywhere, abre una consola Bash:
```
git clone https://github.com/TUUSUARIO/TUREPO.git
cd TUREPO
```

## 2) Crear entorno virtual e instalar dependencias
```
python3.10 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 3) Variables de entorno
- Crea un archivo `.env` basado en `.env.example` o añade variables en la pestaña Web:
```
DJANGO_SETTINGS_MODULE=gestion_riesgo.settings
DJANGO_SECRET_KEY=pon_aqui_una_clave_segura
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=TUUSUARIO.pythonanywhere.com
```

## 4) Configurar la Web App
- Pestaña Web -> Add a new web app -> Manual configuration (Python 3.10)
- Virtualenv: selecciona `/home/TUUSUARIO/TUREPO/.venv`
- Archivo WSGI: edítalo y asegúrate de apuntar a este proyecto:
```
import os, sys
path = '/home/TUUSUARIO/TUREPO'
if path not in sys.path:
    sys.path.append(path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gestion_riesgo.settings')
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

## 5) Migraciones y superusuario
```
python manage.py migrate
python manage.py createsuperuser
```

## 6) Archivos estáticos
- Ya existe `STATIC_ROOT = BASE_DIR / 'staticfiles'`.
- Ejecuta:
```
python manage.py collectstatic
```
- En la pestaña Web añade static files mapping:
  - URL: `/static/` -> Directorio: `/home/TUUSUARIO/TUREPO/staticfiles`

## 7) Recargar la app
- Pestaña Web -> botón "Reload".
- Accede: `https://TUUSUARIO.pythonanywhere.com/`

## Notas
- Base de datos: SQLite funciona para demos; para producción, evalúa MySQL en PA.
- Seguridad: no subas `.env` al repositorio (ya está en `.gitignore`).
- Cualquier ajuste de dominios, agrégalo en `DJANGO_ALLOWED_HOSTS`.
