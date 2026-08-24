# CineVault

Una plataforma cinematográfica full-stack para descubrir películas, armar una lista personal y compartir puntuaciones y reseñas.

## Funcionalidades

- Catálogo público con búsqueda por título, descripción o director.
- Filtros por género y orden cronológico o alfabético.
- Catálogo paginado para mantener una navegación rápida al crecer la colección.
- Inicio dinámico con selección destacada, estrenos recientes y películas mejor puntuadas.
- Fichas con póster, sinopsis, géneros, dirección, promedio de puntuación y películas relacionadas.
- Registro, inicio de sesión, perfil y cambio de contraseña.
- Lista personal de películas para ver.
- Puntuaciones y reseñas editables, una por usuario y película.
- Administración del catálogo restringida a usuarios `staff`.
- Panel administrativo con importación y exportación de datos.
- Diseño responsive y navegación accesible.

## Tecnologías

Python 3.12, Django 5.2, SQLite en desarrollo, PostgreSQL en producción, WhiteNoise, Pillow y django-import-export.

## Desarrollo local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

En Windows, activá el entorno con `.venv\Scripts\activate`.

La aplicación queda disponible en `http://127.0.0.1:8000/`.

Para crear una cuenta administradora:

```bash
python manage.py createsuperuser
```

## Variables de entorno

| Variable | Uso |
| --- | --- |
| `DJANGO_SECRET_KEY` | Clave privada obligatoria en producción |
| `DJANGO_DEBUG` | `True` sólo durante desarrollo |
| `DJANGO_ALLOWED_HOSTS` | Hosts separados por comas |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Orígenes HTTPS separados por comas |
| `DATABASE_URL` | Conexión PostgreSQL utilizada en producción |

## Despliegue

El repositorio incluye `render.yaml`, `build.sh` y configuración para WhiteNoise/PostgreSQL. En Render el build instala dependencias, recolecta archivos estáticos y ejecuta migraciones antes de iniciar Gunicorn.

## Calidad

```bash
python manage.py test
python manage.py check
python manage.py check --deploy
```

La suite cubre acceso público, búsqueda, paginación, permisos, lista personal, reseñas y restricciones de método HTTP.
