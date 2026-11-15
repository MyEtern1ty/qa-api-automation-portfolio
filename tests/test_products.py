"""API-001–API-008: DummyJSON products contract/integration checks.

The negative ID contract (API-003) is deliberately skipped until confirmed.
See docs/test-cases/products.md for full manual test designs.
"""

import pytest


def assert_product(product):
    assert isinstance(product, dict)
    assert type(product.get("id")) is int
    assert isinstance(product.get("title"), str) and product["title"].strip()
    assert isinstance(product.get("category"), str)
    assert type(product.get("price")) in (int, float)


def assert_list_response(response):
    assert response.status_code == 200, response.text[:500]
    assert "application/json" in response.headers.get("Content-Type", "").lower()
    body = response.json()
    assert isinstance(body, dict)
    assert isinstance(body.get("products"), list)
    for field in ("total", "skip", "limit"):
        assert type(body.get(field)) is int, f"{field} is not an integer"
        assert body[field] >= 0
    for product in body["products"]:
        assert_product(product)
    return body


def test_api_001_get_default_products(api_client):
    """API-001: default list contains up to 30 products."""
    body = assert_list_response(api_client("/products"))
    assert body["skip"] == 0
    assert body["limit"] == 30
    assert len(body["products"]) == min(30, body["total"])


def test_api_002_get_product_by_existing_id(api_client):
    """API-002: single product has matching ID and documented fields."""
    response = api_client("/products/1")
    assert response.status_code == 200, response.text[:500]
    product = response.json()
    assert_product(product)
    assert product["id"] == 1
    assert isinstance(product.get("description"), str)


@pytest.mark.contract_pending
@pytest.mark.skip(reason="API-003: 404 status/error schema for unknown product ID is not documented; confirm before enforcing")
def test_api_003_get_nonexistent_product(api_client):
    """API-003: proposed behavior, not yet an agreed API contract."""
    response = api_client("/products/999999")
    assert response.status_code == 404
    assert response.json().get("message")


def test_api_004_limit_products(api_client):
    """API-004: limit=10 returns 10 unique products."""
    body = assert_list_response(api_client("/products", limit=10))
    assert body["total"] >= 10
    assert body["skip"] == 0
    assert body["limit"] == 10
    ids = [product["id"] for product in body["products"]]
    assert len(ids) == 10
    assert len(set(ids)) == 10


def test_api_005_products_pagination(api_client):
    """API-005: skip=10 selects positions 11–20 from the same ordering."""
    baseline = assert_list_response(api_client("/products", limit=20, skip=0))
    assert baseline["total"] >= 20
    body = assert_list_response(api_client("/products", limit=10, skip=10))
    assert body["skip"] == 10
    assert body["limit"] == 10
    assert len(body["products"]) == 10
    assert body["total"] == baseline["total"]
    expected_ids = [product["id"] for product in baseline["products"][10:20]]
    actual_ids = [product["id"] for product in body["products"]]
    assert actual_ids == expected_ids


def test_api_006_search_products(api_client):
    """API-006: documented 'phone' search returns structured nonempty results.

    The matching algorithm is not documented: do not assert title substring.
    """
    body = assert_list_response(api_client("/products/search", q="phone"))
    assert body["total"] > 0
    assert len(body["products"]) > 0
    assert body["skip"] == 0
    assert body["total"] >= len(body["products"])


def test_api_007_products_sorted_by_ascending_price(api_client):
    """API-007: ascending price is nondecreasing (ties permitted)."""
    body = assert_list_response(api_client("/products", sortBy="price", order="asc"))
    prices = [product["price"] for product in body["products"]]
    assert len(prices) >= 2
    assert all(previous <= following for previous, following in zip(prices, prices[1:]))


def test_api_008_products_filtered_by_category(api_client):
    """API-008: category endpoint returns only smartphones."""
    slug = "smartphones"
    categories_response = api_client("/products/category-list")
    assert categories_response.status_code == 200
    assert slug in categories_response.json()
    body = assert_list_response(api_client(f"/products/category/{slug}"))
    assert body["total"] > 0
    assert body["total"] >= len(body["products"])
    assert len(body["products"]) > 0
    assert all(product["category"] == slug for product in body["products"])
