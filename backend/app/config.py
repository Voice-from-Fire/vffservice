import os


# Values: local, gcloud
DB_TYPE = os.environ["DB_TYPE"]

if DB_TYPE not in ("direct", "gcloud"):
    raise Exception(f"Invalid environment: {DB_ENVIRONMENT}")

STORAGE_TYPE = os.environ["STORAGE_TYPE"]

if STORAGE_TYPE not in ("local", "gcloud"):
    raise Exception(f"Invalid environment: {DB_ENVIRONMENT}")

if STORAGE_TYPE == "gcloud":
    STORAGE_BUCKET = os.environ.get("STORAGE_BUCKET") or "vff-storage"
else:
    STORAGE_BUCKET = None

DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_NAME = os.environ["DB_NAME"]
DB_OPTS = os.environ.get("DB_OPTS") or ""


def update_db_url():
    global DATABASE_URL
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}{DB_OPTS}"
    return DATABASE_URL


update_db_url()


TEST_MODE = False
