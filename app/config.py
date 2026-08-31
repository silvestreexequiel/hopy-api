"""Configuration loading from environment variables.

Uses the same names as escuelahopi/env.php so the PHP portal's .env can be
shared. Values are read from the real environment or from a .env file at the
root of the API repo.
"""
import os
from dotenv import load_dotenv

load_dotenv()


def env(key, default=None):
    value = os.environ.get(key)
    if value is None or value == "":
        return default
    return value


def env_required(key):
    value = env(key)
    if value is None or value == "":
        raise RuntimeError(
            f"Falta la variable de entorno {key}. Copie .env.example a .env."
        )
    return value


class Settings:
    db_host = env("ACADEMY_DB_HOST", "localhost")
    db_name = env("ACADEMY_DB_NAME")
    db_user = env("ACADEMY_DB_USER")
    db_pass = env("ACADEMY_DB_PASS")
    db_charset = env("ACADEMY_DB_CHARSET", "utf8mb4")

    staff_user = env("ACADEMY_STAFF_USER")
    staff_pass = env("ACADEMY_STAFF_PASS")

    admin_user = env("ACADEMY_ADMIN_USER")
    admin_pass = env("ACADEMY_ADMIN_PASS")

    openai_key = env("OPENAI_API_KEY")
    openai_model = env("OPENAI_MODEL", "gpt-4o-mini")

    jwt_secret = env("HOPI_JWT_SECRET", "hopi-mobile-2025")


settings = Settings()
