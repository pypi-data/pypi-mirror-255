# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import json
import asyncio

from tortoise import Tortoise
from bovine_store import bovine_admin_store
from bovine.types import Visibility
from bovine_store.models import BovineActor
from bovine.crypto import generate_ed25519_private_key, private_key_to_did_key


async def create_tables(db_url):
    async with bovine_admin_store(db_url=db_url):
        await Tortoise.generate_schemas()


async def list_bovine_names_from_db(db_url):
    async with bovine_admin_store(db_url=db_url) as store:
        names = await store.list_bovine_names()
        for name in names:
            print(name)


async def handle_actor_profile(db_url, bovine_name, filename: str | None = None):
    async with bovine_admin_store(db_url=db_url) as store:
        if filename:
            with open(filename) as fp:
                properties = json.load(fp)
            await store.set_properties_for_actor(bovine_name, properties)

        actor = await store.actor_for_name(bovine_name)

        print(
            json.dumps(actor.actor_object.build(visibility=Visibility.OWNER), indent=2)
        )

        await actor.session.close()


async def handle_keys(db_url, bovine_name, list, new, did_key):
    async with bovine_admin_store(db_url=db_url) as store:
        if list:
            actor = await BovineActor.get_or_none(
                bovine_name=bovine_name
            ).prefetch_related("keypairs")
            for x in actor.keypairs:
                if x.private_key and len(x.private_key) > 0:
                    secret_info = "Has secret"
                else:
                    secret_info = ""

                print(f"Key name {x.name} {secret_info}")

                print(x.public_key)
                print()
        elif new:
            secret = generate_ed25519_private_key()
            print(f"Your new secret: {secret}")
            did_key = private_key_to_did_key(secret)
            name = did_key.removeprefix("did:key:")
            await store.add_identity_string_to_actor(bovine_name, name, did_key)
        elif did_key:
            name = did_key.removeprefix("did:key:")
            await store.add_identity_string_to_actor(bovine_name, name, did_key)


async def cleanup(db_url, batch_size=1000, days=3):
    async with bovine_admin_store(db_url=db_url):
        client = Tortoise.get_connection("default")

        sql_query_visible_to = f"""
        delete from visibleto where main_object_id in 
            (select id from storedjsonobject
                where object_type='REMOTE'
                    and updated < (current_date - interval '{days} day')
                limit {batch_size}) RETURNING *;
        """

        delete_count = batch_size

        while delete_count >= batch_size:
            delete_count, _ = await client.execute_query(sql_query_visible_to)
            print(delete_count)

            await asyncio.sleep(0.1)

        print("Done with visible to")

        try:
            await client.execute_query(
                """alter table visibleto drop constraint 
                visibleto_main_object_id_fkey;"""
            )
        except Exception:
            ...

        sql_query = f"""
        delete from storedjsonobject where id in 
            (select id from storedjsonobject
                where object_type='REMOTE'
                    and updated < (current_date - interval '{days} day')
                limit {batch_size}) RETURNING *;
        """

        delete_count = batch_size

        try:
            while delete_count == batch_size:
                delete_count, _ = await client.execute_query(sql_query)
                print(delete_count)

                await asyncio.sleep(0.1)
        finally:
            delete_visible_to = """
            delete from visibleto where main_object_id in 
                (select main_object_id from 
                    visibleto v left join storedjsonobject s on v.main_object_id = s.id 
                where s.id is null);"""
            await client.execute_query(delete_visible_to)

            await client.execute_query(
                """alter table visibleto add constraint visibleto_main_object_id_fkey 
                foreign key (main_object_id) references storedjsonobject (id);"""
            )
