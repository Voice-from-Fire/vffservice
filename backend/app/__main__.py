import click
import os
import math
from random import Random

from .schemas.user import UserCreate
from .ops.user import create_user

from .tools import ffmpeg
from .db.database import init_db, connect_db
from .db.models import Sample, Base, Role
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


DATASETS_DIR = "datasets"


@click.group()
def cli():
    pass


@cli.command()
@click.option("--create-test-user", is_flag=True, default=False)
def initdb(create_test_user):
    click.echo("Initialized the database")
    init_db()
    if create_test_user:
        from .service import get_db

        session = next(get_db())
        try:
            create_user(session, UserCreate(name="testuser", password="pass"))
            print("Created user 'testuser' with password 'pass'")
            create_user(
                session,
                UserCreate(name="testadmin", password="pass"),
                role=Role.admin,
            )
            print("Created user 'testadmin' with password 'pass'")
        except IntegrityError:
            click.echo("'testuser' already exists")


@cli.command("import-test")
@click.argument("path")
def import_calibration(path):
    from .service import get_db

    session = next(get_db())

    path = os.path.abspath(path)
    for filename in os.listdir(path):
        fullname = os.path.join(path)
        # TODO


if __name__ == "__main__":
    cli()
