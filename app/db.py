"""Acceso al MySQL compartido con academy-operations.

Reusa la tabla `cleanup_events` y replica las operaciones de
escuelahopi/academy-operations/db.php.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from .config import settings

_engine: Engine = None


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = (
            f"mysql+pymysql://{settings.db_user}:{settings.db_pass}"
            f"@{settings.db_host}/{settings.db_name}?charset={settings.db_charset}"
        )
        _engine = create_engine(url, pool_pre_ping=True, future=True)
    return _engine


def ensure_cleanup_table():
    ddl = text(
        """
        CREATE TABLE IF NOT EXISTS cleanup_events (
            id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
            category VARCHAR(80) NOT NULL,
            endpoint VARCHAR(120) NOT NULL,
            method VARCHAR(10) NOT NULL,
            payload TEXT NULL,
            remote_addr VARCHAR(45) NULL,
            user_agent VARCHAR(255) NULL,
            triggered_at DATETIME NOT NULL,
            KEY idx_triggered_at (triggered_at),
            KEY idx_category (category)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """
    )
    with get_engine().begin() as conn:
        conn.execute(ddl)


def register_cleanup_trigger(category, endpoint, method, raw_payload, remote_addr, user_agent):
    ensure_cleanup_table()
    sql = text(
        """
        INSERT INTO cleanup_events
            (category, endpoint, method, payload, remote_addr, user_agent, triggered_at)
        VALUES
            (:category, :endpoint, :method, :payload, :remote_addr, :user_agent, NOW())
        """
    )
    with get_engine().begin() as conn:
        result = conn.execute(
            sql,
            {
                "category": category,
                "endpoint": endpoint,
                "method": method,
                "payload": raw_payload,
                "remote_addr": remote_addr,
                "user_agent": (user_agent or "")[:255] or None,
            },
        )
        return int(result.lastrowid)


def count_cleanup_events():
    try:
        ensure_cleanup_table()
        with get_engine().connect() as conn:
            return int(conn.execute(text("SELECT COUNT(*) FROM cleanup_events")).scalar())
    except Exception:
        return 0


def get_cleanup_events(limit=25, offset=0):
    try:
        ensure_cleanup_table()
        sql = text(
            """
            SELECT id, category, endpoint, method, payload, remote_addr, user_agent, triggered_at
            FROM cleanup_events
            ORDER BY id DESC
            LIMIT :limit OFFSET :offset
            """
        )
        with get_engine().connect() as conn:
            rows = conn.execute(sql, {"limit": int(limit), "offset": int(offset)}).mappings().all()
            return [dict(r) for r in rows]
    except Exception:
        return []


def purge_cleanup_events():
    ensure_cleanup_table()
    with get_engine().begin() as conn:
        deleted = int(conn.execute(text("SELECT COUNT(*) FROM cleanup_events")).scalar())
        conn.execute(text("TRUNCATE TABLE cleanup_events"))
        legacy = False
        has_legacy = conn.execute(text("SHOW TABLES LIKE 'cleanup_counts'")).rowcount
        if has_legacy and has_legacy > 0:
            conn.execute(text("TRUNCATE TABLE cleanup_counts"))
            legacy = True
    return {"deleted_events": deleted, "legacy_counters_reset": legacy}


def raw_search_events(where_clause):
    """Filtra cleanup_events con una condicion armada por el llamador."""
    sql = (
        "SELECT id, category, endpoint, method, remote_addr, triggered_at "
        "FROM cleanup_events WHERE " + where_clause + " ORDER BY id DESC LIMIT 50"
    )
    ensure_cleanup_table()
    raw = get_engine().raw_connection()
    try:
        cursor = raw.cursor()
        cursor.execute(sql)
        columns = [col[0] for col in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        raw.close()
