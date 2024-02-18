# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest

from unittest.mock import AsyncMock
from quart import Quart, g
from tortoise import Tortoise

from bovine_store import BovineAdminStore
from bovine_store.utils.test import store  # noqa F401

from bovine_herd.server import default_configuration
from bovine_herd.server.endpoints import build_endpoints_blueprint

from bovine_herd.server.authorize import add_authorization
from bovine_herd.server.objects import objects_blueprint


async def init(db_url: str = "sqlite://db.sqlite3") -> None:
    await Tortoise.init(
        db_url=db_url,
        modules={
            "models": [
                "bovine_store.models",
            ]
        },
    )
    await Tortoise.generate_schemas()

    return None


async def dummy(item, actor):
    ...


@pytest.fixture
async def test_app(store):  # noqa F801
    app = Quart(__name__)

    app.config["bovine_store"] = store
    app.config["session"] = store.session

    app.config["validate_http_signature"] = AsyncMock(return_value="owner")

    app.before_request(add_authorization)
    app.register_blueprint(objects_blueprint)

    yield app

    await store.session.close()


@pytest.fixture
async def fedi_test_app(test_app):  # noqa F801
    test_app.register_blueprint(default_configuration)
    endpoints = build_endpoints_blueprint(dummy, dummy, dummy)
    test_app.register_blueprint(endpoints, url_prefix="/endpoints")
    yield test_app


@pytest.fixture
async def test_alice(test_app):  # noqa F801
    admin_store = BovineAdminStore(
        endpoint_path="http://localhost/endpoints/templates",
    )
    alice_bovine_name = await admin_store.register("alice")
    alice = await admin_store.actor_for_name(alice_bovine_name)

    @test_app.before_request
    async def set_retriever():
        g.retriever = alice.actor_object.id

    yield alice


def remove_domain_from_url(url):
    assert url.startswith("https://my_domain")

    return url[17:]
