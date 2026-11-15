"""Общий HTTP-клиент для публичного API каталога товаров DummyJSON."""

import os

import pytest
import requests


@pytest.fixture(scope="session")
def api_client():
    base_url = os.environ.get("DUMMYJSON_BASE_URL", "https://dummyjson.com").rstrip("/")
    session = requests.Session()
    session.headers.update({"Accept": "application/json"})

    def get(path, **params):
        return session.get(f"{base_url}{path}", params=params or None, timeout=20)

    yield get
    session.close()
