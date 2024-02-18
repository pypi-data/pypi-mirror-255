# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import aiohttp
from urllib.parse import urljoin
from typing import Optional, Tuple, Callable, List
from asyncstdlib.functools import lru_cache
from contextlib import asynccontextmanager
from tortoise import Tortoise
import bovine_store

from .config import tortoise_config
from .types import EndpointType
from .actor.bovine_store_actor import BovineStoreActor
from .actor.register import register, endpoint_path_function_from_endpoint
from .models import BovineActor, BovineActorEndpoint, BovineActorKeyPair

from .utils import user_to_account_and_actor_url

from .store import load_application_actor_data
from .store.retrieve_object import retrieve_remote_object
from .store.utils import domain_from_host


class BovineStore:
    """Basic interface for the bovine store, should be used to obtain actors."""

    def __init__(
        self,
        host: str | None = None,
        session: aiohttp.ClientSession | None = None,
        application_data: dict = {},
    ):
        self.session = session
        self.application_data = application_data
        self.domain = domain_from_host(host)

    async def retrieve(self, retriever: str, object_id: str, include=[]):
        """Retrieves the object identified by object_it for the retriever. This is used
        when a GET request happens, as it is unclear to which actor the
        object_id belongs."""
        return await retrieve_remote_object(retriever, object_id, include=include)

    async def retrieve_for_get(self, retriever, object_id):
        """Retrieves an object"""
        return await retrieve_remote_object(retriever, object_id)

    async def actor_for_name(self, bovine_name: str) -> Optional[BovineStoreActor]:
        """Retrieves the actor for a given bovine_name"""

        actor = await BovineActor.get_or_none(bovine_name=bovine_name).prefetch_related(
            "endpoints", "keypairs"
        )
        if actor is None:
            return None

        return await BovineStoreActor.from_database(actor, self.session)

    @lru_cache
    async def resolve_endpoint(
        self, endpoint: str
    ) -> Tuple[Optional[EndpointType], Optional[BovineStoreActor]]:
        """Given the url of an endpoint, returns the type of the endpoint, e.g. inbox,
        and the corresponding BovineStoreActor"""
        actor_endpoint = await BovineActorEndpoint.get_or_none(
            name=endpoint
        ).prefetch_related("bovine_actor")

        if not actor_endpoint:
            return None, None
        await actor_endpoint.bovine_actor.fetch_related("endpoints", "keypairs")
        return actor_endpoint.endpoint_type, await BovineStoreActor.from_database(
            actor_endpoint.bovine_actor, self.session
        )

    async def resolve_endpoint_no_cache(
        self, endpoint: str
    ) -> Tuple[Optional[EndpointType], Optional[BovineStoreActor]]:
        """Given the url of an endpoint, returns the type of the endpoint, e.g. inbox,
        and the corresponding BovineStoreActor"""
        actor_endpoint = await BovineActorEndpoint.get_or_none(
            name=endpoint
        ).prefetch_related("bovine_actor")

        if not actor_endpoint:
            return None, None
        await actor_endpoint.bovine_actor.fetch_related("endpoints", "keypairs")
        return actor_endpoint.endpoint_type, await BovineStoreActor.from_database(
            actor_endpoint.bovine_actor, self.session
        )

    async def user_count(self) -> int:
        """Returns the total number of bovine actors used in nodeinfo,
        this count probably lies with bovine being a multi hostname server
        and supporting bot accounts."""
        return await BovineActor.filter().count()

    async def get_account_url_for_identity(self, identity: str):
        """Returns the account, i.e. the identity starting with acct:,
        and the actoru_url for a given identity"""
        key = await BovineActorKeyPair.get_or_none(
            public_key=identity
        ).prefetch_related("bovine_actor")
        if not key:
            return None, None
        await key.bovine_actor.fetch_related("endpoints", "keypairs")
        return user_to_account_and_actor_url(key.bovine_actor)

    async def application_actor_for_url(self, url: str):
        """Returns the application actor fot the given url"""
        account_url = urljoin(url, "/activitypub/bovine")
        application_data = await load_application_actor_data(self.application_data)

        app_actor = bovine_store.actor.BovineApplicationActor(
            {**application_data, "account_url": account_url}
        )
        await app_actor.init(session=self.session)

        return app_actor

    # async def collection_response(self, collection_id):
    #     return await collection_response(collection_id)


class BovineAdminStore:
    """Store for managing actors. This store should be used to create
    actor management interfaces. Usage:

    ```python
    store = BovineAdmineStore(domain="cows.example")
    bovine_name = await store.register("moocow")
    await store.add_identity_string_to_actor(
        bovine_name, "sample", "did:example:123")
    ```

    This will create the account `@moocow@cows.example` which can be accessed
    through Moo-Auth-1 with the secret corresponding to the did.

    These can be kept separate from the actual fediverse server implementation.

    For usage see `bovine_tool` and `bovine_management`.

    The parameters endpoint_path, endpoint_path_function can probably be removed
    at one point. The parameter domain can actually be of the form
    "http://domain_name" or "https://domain_name". This is useful for end
    to end tests.
    """

    def __init__(
        self,
        endpoint_path: str | None = None,
        endpoint_path_function: Callable | None = None,
        domain: str | None = None,
    ):
        self.domain = domain
        self.endpoint_path_function = endpoint_path_function
        if endpoint_path_function is None and endpoint_path:
            self.endpoint_path_function = endpoint_path_function_from_endpoint(
                endpoint_path
            )

    async def register(self, handle_name: str, endpoints: dict = {}) -> str:
        """registers a new user with handle_name. The domain is extracted from
        the endpoint path configured when creating the store. This method
        generates the necessary private keys for the actor. Implementations
        of bovine should never require one adding a secret.

        :param handle_name: The username
        :param endpoints: dictionary of predefined endpoints.

        :return: The bovine name given by handle_name + uuid4"""

        if self.endpoint_path_function is None:
            if self.domain is None:
                raise Exception("Need to specify an endpoint")
            if "://" not in self.domain:
                domain = "https://" + self.domain
            else:
                domain = self.domain

            self.endpoint_path_function = endpoint_path_function_from_endpoint(
                urljoin(domain, "endpoints/template")
            )

        result = await register(
            handle_name,
            endpoint_path_function=self.endpoint_path_function,
            endpoints=endpoints,
        )
        return result.bovine_name

    async def add_identity_string_to_actor(
        self, bovine_name: str, name: str, identity: str
    ) -> None:
        """Modifies an Actor by adding a new identity to it. name is used
        to identity the identity and serves little functional purpose."""
        actor = await BovineActor.get_or_none(bovine_name=bovine_name)
        await BovineActorKeyPair.create(
            bovine_actor=actor, name=name, public_key=identity, private_key=""
        )

    async def set_properties_for_actor(
        self, bovine_name: str, properties: dict
    ) -> None:
        """Sets a new properties object for the actor"""
        actor = await BovineActor.get_or_none(bovine_name=bovine_name)
        if actor is None:
            return None
        actor.properties = properties
        await actor.save()

    async def actor_for_name(self, bovine_name: str) -> Optional[BovineStoreActor]:
        """Retrieves the actor for a given bovine_name"""

        actor = await BovineActor.get_or_none(bovine_name=bovine_name).prefetch_related(
            "endpoints", "keypairs"
        )
        if actor is None:
            return None

        return await BovineStoreActor.from_database(actor, None)

    async def list_bovine_names(self) -> List[str]:
        result = await BovineActor.filter().all()
        return [x.bovine_name for x in result]


@asynccontextmanager
async def bovine_admin_store(db_url: str, domain: str = None):
    """Allows one to manage a [`BovineAdminStore`][bovine_store.BovineAdminStore]
    using an async context manager."""

    await Tortoise.init(config=tortoise_config(db_url))

    yield BovineAdminStore(domain=domain)

    await Tortoise.close_connections()
