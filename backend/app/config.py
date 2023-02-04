import os

# Values: test, gcloud
RUN_ENVIRONMENT = os.environ["VFF_RUN_ENV"]

if RUN_ENVIRONMENT not in ("local", "gcloud"):
    raise Exception(f"Invalid environment: {RUN_ENVIRONMENT}")

DB_PASSWORD = os.environ["DB_PASSWORD"]
DB_HOST = os.environ["DB_HOST"]
DB_USER = os.environ["DB_USER"]
DB_NAME = os.environ["DB_NAME"]
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}"

TEST_MODE = False
