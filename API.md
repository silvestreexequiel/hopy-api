# Academy Operations API — Referencia

Base URL (dev): `http://localhost:8000`
Prefijo de todos los recursos: `/api/v1`
Formato: JSON (request y response). Docs interactivas (Swagger): `GET /docs`.

## Autenticacion

- **Sesion staff**: `POST /api/v1/auth/login` devuelve un `token` (JWT). Para
  endpoints que lo requieren, enviar `Authorization: Bearer <token>`.
- **Basic auth admin**: solo `DELETE /api/v1/cleanup/reset` usa
  `Authorization: Basic <base64(user:pass)>` con las credenciales admin.

Los valores de credenciales y de base de datos se configuran por variables de
entorno (ver `.env.example`).

---

## Indice

| Metodo | Ruta | Auth |
| --- | --- | --- |
| GET | `/` | no |
| POST | `/api/v1/auth/login` | no |
| GET | `/api/v1/profiles/{id}` | no |
| GET | `/api/v1/events` | no |
| GET | `/api/v1/cleanup/events` | no |
| DELETE | `/api/v1/cleanup/orphans` | no |
| DELETE | `/api/v1/cleanup/logs` | no |
| DELETE | `/api/v1/cleanup/cache` | no |
| GET/POST/DELETE | `/api/v1/cleanup/reset` | Basic (admin) |
| GET | `/api/v1/admin/overview` | Bearer |
| POST | `/api/v1/chat` | no |
| GET | `/api/v1/status` | no |

---

## GET `/`

Metadatos del servicio y listado de endpoints.

```json
{ "service": "Academy Operations API", "version": "1.0.0", "endpoints": [ ... ] }
```

---

## POST `/api/v1/auth/login`

Login del staff operativo.

**Request**
```json
{ "username": "staff", "password": "hopi123" }
```

**200 OK**
```json
{
  "ok": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": { "username": "staff", "role": "staff" }
}
```

**401 Unauthorized**
```json
{ "ok": false, "error": "Credenciales invalidas para staff" }
```

**500** si faltan las credenciales staff en el entorno.

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"username":"staff","password":"hopi123"}'
```

El `token` es un JWT `HS256` con claims `sub`, `role`, `iat`, `exp` (validez 7 dias).

---

## GET `/api/v1/profiles/{id}`

Ficha de un miembro del staff. `id` es string (ej. `1001`, `1002`, `1003`).

**200 OK**
```json
{ "id": "1002", "name": "Martin Silva", "role": "Data Analyst", "email": "martin@academy.local" }
```

Un `id` desconocido responde 200 con datos `Unknown / N/A`.

```bash
curl http://localhost:8000/api/v1/profiles/1002
```

---

## GET `/api/v1/events`

Buscador de eventos de limpieza.

**Query params**

| Param | Tipo | Default | Descripcion |
| --- | --- | --- | --- |
| `q` | string | `""` | Filtro por categoria, endpoint o IP. |

**200 OK**
```json
{
  "ok": true,
  "query": "users",
  "message": "Resultados para: users",
  "count": 1,
  "results": [
    { "id": 12, "category": "users", "endpoint": "/api/v1/cleanup/orphans",
      "method": "DELETE", "remote_addr": "127.0.0.1", "triggered_at": "2026-08-31 12:34:56" }
  ]
}
```

```bash
curl "http://localhost:8000/api/v1/events?q=users"
```

---

## GET `/api/v1/cleanup/events`

Log paginado de eventos de limpieza.

**Query params**

| Param | Tipo | Default | Valores |
| --- | --- | --- | --- |
| `page` | int | 1 | >= 1 |
| `per_page` | int | 25 | 25, 50, 100, 200 |

**200 OK**
```json
{
  "ok": true, "total": 42, "page": 1, "per_page": 25, "total_pages": 2,
  "events": [
    { "id": 42, "category": "cache", "endpoint": "/api/v1/cleanup/cache",
      "method": "DELETE", "payload": "{\"x\":1}", "remote_addr": "127.0.0.1",
      "user_agent": "curl/8.4", "triggered_at": "2026-08-31 12:34:56" }
  ]
}
```

```bash
curl "http://localhost:8000/api/v1/cleanup/events?page=1&per_page=50"
```

---

## DELETE `/api/v1/cleanup/{orphans|logs|cache}`

Ejecuta un lote de limpieza y registra el evento en MySQL. Metodo **DELETE**,
acepta un cuerpo JSON libre.

**Request** (opcional)
```json
{ "requestedBy": "mobile-app", "batchLimit": 50, "reason": "routine_maintenance" }
```

**200 OK**
```json
{
  "ok": true,
  "endpoint": "/api/v1/cleanup/orphans",
  "received_method": "DELETE",
  "job_id": "JOB-48213",
  "message": "Orphan user accounts erased. Records permanently removed from the database.",
  "received_payload": { "requestedBy": "mobile-app", "batchLimit": 50 },
  "db_tracking": "logged"
}
```

Mensajes por job:
- `orphans` → *Orphan user accounts erased...*
- `logs` → *Legacy logs deleted...*
- `cache` → *Stale cache purged...*

```bash
curl -X DELETE http://localhost:8000/api/v1/cleanup/orphans \
  -H 'Content-Type: application/json' \
  -d '{"requestedBy":"mobile-app","batchLimit":50}'
```

---

## GET/POST/DELETE `/api/v1/cleanup/reset`

Vacia el log de eventos. Requiere **Basic auth** admin.

**200 OK**
```json
{
  "ok": true, "endpoint": "/api/v1/cleanup/reset", "received_method": "DELETE",
  "message": "Cleanup event log erased.", "deleted_events": 42, "legacy_counters_reset": false
}
```

**401** sin credenciales o invalidas (incluye `WWW-Authenticate: Basic`).

```bash
curl -X DELETE http://localhost:8000/api/v1/cleanup/reset -u admin:reset123
```

---

## GET `/api/v1/admin/overview`

Resumen operativo. Requiere `Authorization: Bearer <token>` con rol `admin`.

**200 OK**
```json
{
  "ok": true, "viewer": "admin", "total_events": 42,
  "staff_directory": [ { "id": "1001", "name": "Lucia Perez", "role": "Operations Lead", "email": "lucia@academy.local" } ],
  "config": { "db_host": "localhost", "db_name": "academy", "openai_model": "gpt-4o-mini", "staff_user": "staff" }
}
```

- **401** sin token. **403** si el rol no es `admin` (incluye `your_role`).

```bash
curl http://localhost:8000/api/v1/admin/overview -H "Authorization: Bearer $TOKEN"
```

---

## POST `/api/v1/chat`

Asistente de declaraciones (proxy a OpenAI).

**Request**
```json
{ "prompt": "quiero encontrar un trabajo que me apasione" }
```

**200 OK**
```json
{ "response": "En este ano encuentro el trabajo que me apasiona." }
```

**Errores**: `{ "error": "No prompt provided." }`, o `{ "error": "..." }` si la
API de OpenAI falla o `OPENAI_API_KEY` no esta configurada (500).

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"quiero un trabajo que me apasione"}'
```

---

## GET `/api/v1/status`

Estado del sistema.

**Query params**: `status` (string, default `System healthy`).

**200 OK**
```json
{ "ok": true, "status": "System healthy", "refresh_seconds": 300 }
```

---

## Codigos de estado

| Codigo | Significado |
| --- | --- |
| 200 | OK |
| 401 | No autenticado / credenciales invalidas |
| 403 | Autenticado pero sin permisos |
| 404 | Ruta inexistente |
| 405 | Metodo no permitido |
| 422 | Body invalido (validacion) |
| 500 | Error del servidor / configuracion incompleta |
