# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

from bovine_store.utils.test import store  # noqa F401

from . import BovineAdminStore
from .types import EndpointType


async def test_creation_with_domain(store):  # noqa F801
    store = BovineAdminStore(domain="example.com")

    bovine_name = await store.register("handle_name")
    actor = await store.actor_for_name(bovine_name)

    assert actor.actor_id.startswith("https://example.com/endpoints/")


async def test_creation_with_domain_and_endpoint_path(store):  # noqa F801
    actor_id = "https://example.com/actor"
    store = BovineAdminStore(domain="example.com")

    bovine_name = await store.register(
        "handle_name", endpoints={EndpointType.ACTOR: actor_id}
    )

    actor = await store.actor_for_name(bovine_name)

    assert actor.actor_id == actor_id
