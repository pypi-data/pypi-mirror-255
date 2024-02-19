# SPDX-FileCopyrightText: 2023 Helge
#
# SPDX-License-Identifier: MIT

import pytest
from unittest.mock import patch, AsyncMock
from quart import Quart

from bovine_store.utils.test import store  # noqa

from . import objects_blueprint


@pytest.fixture
async def test_app():
    app = Quart(__name__)
    app.register_blueprint(objects_blueprint)

    yield app


@pytest.fixture
async def test_client(test_app):
    yield test_app.test_client()


async def test_object_blueprint_unauthorized(store, test_client):  # noqa
    result = await test_client.get("/some-uuid")

    assert result.status_code == 401


async def test_object_blueprint_not_found(store, test_app, test_client):  # noqa
    test_app.config["bovine_store"] = AsyncMock()
    test_app.config["bovine_store"].retrieve_for_get = AsyncMock(return_value=None)
    with patch("bovine_herd.server.utils.get_requester") as mock:
        mock.return_value = "xxx"
        result = await test_client.get(
            "/some-uuid", headers={"accept": "application/activity+json"}
        )

    assert result.status_code == 404


async def test_object_blueprint_found(store, test_app, test_client):  # noqa
    test_app.config["bovine_store"] = AsyncMock()
    test_app.config["bovine_store"].retrieve_for_get = AsyncMock(
        return_value={"@context": "about:bovine", "type": "Note"}
    )
    with patch("bovine_herd.server.utils.get_requester") as mock:
        mock.return_value = "xxx"
        result = await test_client.get(
            "/some-uuid", headers={"accept": "application/activity+json"}
        )

    assert result.status_code == 200

    data = await result.get_json()

    assert "https://www.w3.org/ns/activitystreams" in data["@context"]
