import click
import io
import os
import json
import math
from random import Random

from .ops.samples import create_sample

from .schemas.user import UserCreate
from .ops.user import create_user, get_user_by_name

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


@cli.command("import")
@click.argument("path")
@click.argument("username")
def import_files(path, username):
    from .service import get_db

    session = next(get_db())
    user = get_user_by_name(session, username)
    rnd = Random("b24e179ef8a27f061ae2ac307db2m")
    path = os.path.abspath(path)
    print(path)
    description_file = os.path.join(path, "description.json")
    with open(description_file, "r") as f:
        desc = json.load(f)
    rnd.shuffle(desc)
    for item in desc:
        print("Converting", item["filename"])
        file_path = os.path.join(path, item["filename"])
        with open(file_path, "rb") as f:
            stream = ffmpeg.convert_to_mp3(f.read())
            with open("/tmp/test", "wb") as f:
                f.write(stream)
            create_sample(
                session,
                io.BytesIO(stream),
                user,
                "XX",
                comment="{{'origin': {}, 'filename': {}}}".format(
                    item["comment"], item["filename"]
                ),
            )


if __name__ == "__main__":
    cli()
