import os


def app_env() -> str:
    return os.environ.get("APP_ENV", "prod")


def is_non_prod() -> bool:
    return app_env() != "prod"
