# Academy Operations API

API REST (FastAPI) que expone la operatoria del portal `academy-operations` de
Escuela Hopi para ser consumida por la app mobile. Se conecta al **mismo MySQL**
que el portal PHP y reusa la tabla `cleanup_events`.

## Requisitos

- Python 3.9+
- Un MySQL alcanzable con el esquema de `academy-operations`
  (`escuelahopi/academy-operations/sql/init_cleanup_events.sql`). La tabla
  `cleanup_events` se crea sola en el primer acceso si no existe.

## Configuracion

```bash
cp .env.example .env
# complete ACADEMY_DB_*, ACADEMY_STAFF_*, ACADEMY_ADMIN_*, OPENAI_*, HOPI_JWT_SECRET
```

Las variables usan los **mismos nombres** que `escuelahopi/env.php`, de modo que
se puede compartir la misma configuracion que el portal PHP.

## Levantar

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Docs interactivas: `http://localhost:8000/docs`.

## Endpoints

| Metodo | Ruta | Descripcion |
| --- | --- | --- |
| POST | `/api/v1/auth/login` | Login staff, devuelve token de sesion. |
| GET | `/api/v1/profiles/{id}` | Ficha de un miembro del staff. |
| GET | `/api/v1/events?q=` | Buscador de eventos de limpieza. |
| GET | `/api/v1/cleanup/events?page=&per_page=` | Log paginado de eventos. |
| DELETE | `/api/v1/cleanup/orphans` | Ejecuta limpieza de usuarios huerfanos. |
| DELETE | `/api/v1/cleanup/logs` | Ejecuta limpieza de logs legacy. |
| DELETE | `/api/v1/cleanup/cache` | Ejecuta limpieza de cache. |
| DELETE | `/api/v1/cleanup/reset` | Resetea el log de eventos (basic auth admin). |
| GET | `/api/v1/admin/overview` | Resumen operativo (requiere sesion admin). |
| POST | `/api/v1/chat` | Asistente de declaraciones (OpenAI). |
| GET | `/api/v1/status` | Estado del sistema. |

## MySQL rapido para desarrollo

```bash
docker run -d --name hopi-mysql -e MYSQL_ROOT_PASSWORD=root \
  -e MYSQL_DATABASE=academy -p 3306:3306 mysql:8
# .env -> ACADEMY_DB_HOST=127.0.0.1 DB_NAME=academy DB_USER=root DB_PASS=root
```
