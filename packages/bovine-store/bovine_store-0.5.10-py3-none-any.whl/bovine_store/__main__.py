# SPDX-FileCopyrightText: 2023-2024 Helge
#
# SPDX-License-Identifier: MIT

import asyncio
import click
import json

from dataclasses import dataclass
from .utils.cli import (
    create_tables,
    list_bovine_names_from_db,
    handle_actor_profile,
    handle_keys,
    cleanup,
    register_new_user,
)


@dataclass
class Options:
    db_url: str


@click.group()
@click.option(
    "--db_url",
    default="sqlite://bovine.sqlite3",
    show_envvar=True,
    show_default=True,
    envvar="BOVINE_DB_URL",
    help="Database url",
)
@click.pass_context
def db_group(ctx, db_url):
    ctx.obj = Options(db_url=db_url)


@db_group.command("create", help="Creates the database tables")
@click.pass_obj
def create_db(obj):
    asyncio.run(create_tables(obj.db_url))


@db_group.command(
    "actor", help="lists bovine names in database or shows an actor profile"
)
@click.option(
    "--name",
    metavar="BOVINE_NAME",
    help="Instead of showing a list, shows a specific actor profile",
    default=None,
)
@click.option(
    "--profile",
    metavar="filename.json",
    help="Reads the given file and adds it to the actor's profile; requires providing a bovine_name",
)
@click.pass_obj
def list_bovine_names(obj, name, profile):
    if name:
        actor = asyncio.run(handle_actor_profile(obj.db_url, name, filename=profile))
        print(json.dumps(actor, indent=2))
    elif profile:
        click.echo("Please provide a name")
    else:
        names = asyncio.run(list_bovine_names_from_db(obj.db_url))
        for name in names:
            print(name)


@db_group.command("register", help="registers a new user")
@click.option("--domain", help="The domain name the account is under", required=True)
@click.option("--handle", help="The handle name")
@click.pass_obj
def register_user(obj, domain, handle):
    bovine_name = asyncio.run(register_new_user(obj.db_url, domain, handle))
    print(f"Registered new user with bovine name {bovine_name}")


@db_group.command("key", help="Allows management of cryptographic identifiers")
@click.option("--list", is_flag=True, default=False, help="list identifiers")
@click.option("--new", is_flag=True, default=False, help="Generate a new key")
@click.option("--add", metavar="DID_KEY", help="Add given key")
@click.argument("name", metavar="BOVINE_NAME")
@click.pass_obj
def manage_keys(obj, name, list, new, add):
    asyncio.run(handle_keys(obj.db_url, name, list, new, add))


@db_group.command("cleanup", help="Removes old stored remote objects")
@click.option("--batch_size", default=1000, show_default=True)
@click.option(
    "--days", default=3, show_default=True, help="Age of post in days to clean"
)
@click.pass_obj
def clean_db(obj, batch_size, days):
    asyncio.run(cleanup(obj.db_url, batch_size=batch_size, days=days))


if __name__ == "__main__":
    db_group()
