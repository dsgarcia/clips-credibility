import os


def require_env(name):
    value = os.getenv(name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable: {name}. "
            "Create a local .env file or export the variable before running this script."
        )
    return value


def optional_env(name, default=None):
    return os.getenv(name, default)
