# DummyJSON Products API — Test Cases

**Module:** Products (catalog)  
**Base URL:** `https://dummyjson.com`  
**Method:** GET for all cases  
**Test suite version:** 1.0  
**Status:** Ready for manual review; not executed  
**Source of truth:** [Official Products API documentation](https://dummyjson.com/docs/products)  
**Scope:** API-001 through API-008

## Common prerequisites

- Internet access to the public DummyJSON API.
- Any HTTP client (Postman, curl, browser for GET) capable of reading the HTTP status and JSON response.
- No authentication is required for the documented public product endpoints.
- Do not rely on a fixed catalog size, product order without explicit sorting, or an unchanging dataset.
- Treat a transport outage or rate-limit response as an environment/infrastructure issue, not an API functional assertion.
- This document defines **test designs, not execution results**. Do not mark a case Passed until it is run.

## Response conventions

For product-list endpoints, the documented response is a JSON object containing `products` (array), `total` (integer), `skip` (integer), and `limit` (integer). Product examples include `id` (integer), `title` (string), `category` (string), and `price` (number).

## Test case index

| ID | Title | Type | Priority | Endpoint |
| --- | --- | --- | --- | --- |
| API-001 | Retrieve the default product list | Positive | P1 | `GET /products` |
| API-002 | Retrieve a product by an existing ID | Positive | P1 | `GET /products/1` |
| API-003 | Retrieve a product by a nonexistent ID | Negative / contract clarification | P1 | `GET /products/999999` |
| API-004 | Limit the product list to 10 items | Positive / boundary | P1 | `GET /products?limit=10` |
| API-005 | Skip the first 10 products and return the next 10 | Positive | P1 | `GET /products?limit=10&skip=10` |
| API-006 | Search products by query | Positive | P2 | `GET /products/search?q=phone` |
| API-007 | Sort products by ascending price | Positive | P1 | `GET /products?sortBy=price&order=asc` |
| API-008 | Filter products by a category | Positive | P1 | `GET /products/category/smartphones` |

---

## API-001 — Retrieve the default product list

- **Type / Priority:** Positive / P1
- **Preconditions:** Common prerequisites; no query parameters.
- **Request:** `GET https://dummyjson.com/products`
- **Test data:** None.
- **Steps:**
  1. Send the GET request.
  2. Record the HTTP status and parse the body as JSON.
  3. Inspect the top-level keys and first returned product.
- **Expected results:**
  1. HTTP 200; response body is valid JSON.
  2. Root is an object with `products` (array), `total` (non-negative integer), `skip` (integer equal to 0), `limit` (integer equal to 30, as documented default).
  3. `products` contains 30 entries if at least 30 products are available; generally, `len(products) = min(30, total)`.
  4. Every returned product has an integer `id`, nonempty string `title`, string `category`, and numeric `price`.
- **Traceability:** Products docs → Get all products.

## API-002 — Retrieve a product by an existing ID

- **Type / Priority:** Positive / P1
- **Preconditions:** Product ID `1` exists in the documented example (alternatively, obtain a currently existing ID from API-001 before executing).
- **Request:** `GET https://dummyjson.com/products/1`
- **Test data:** `id=1`.
- **Steps:**
  1. Send the GET request with an existing ID.
  2. Parse JSON and inspect product fields.
- **Expected results:**
  1. HTTP 200; body is a JSON object, not a list wrapper.
  2. `id` equals the requested ID (`1`).
  3. `title` is a nonempty string, `category` is a string, `price` is numeric, `description` is a string.
- **Traceability:** Products docs → Get a single product.
- **Note:** If the fixture dataset changes, replace `1` with an ID obtained from the list endpoint.

## API-003 — Retrieve a product by a nonexistent ID

- **Type / Priority:** Negative / P1
- **Preconditions:** Verify the chosen ID does not exist (e.g., `999999`; do not assume a particular catalog maximum forever).
- **Request:** `GET https://dummyjson.com/products/999999`
- **Test data:** `id=999999`.
- **Steps:**
  1. Check that the ID is not among available products, or choose a clearly out-of-range ID.
  2. Send the GET request.
  3. Inspect the HTTP status and error response.
- **Proposed expected results (requires contract confirmation):**
  1. HTTP 404 Not Found.
  2. The body indicates that the requested product was not found and does not return a valid product object with the requested ID.
- **Specification gap:** The official Products documentation demonstrates successful lookup but does **not** explicitly define the status or JSON schema for an unknown product ID. Record observed behavior and verify the contract before making these assertions mandatory in automated tests.
- **Traceability:** Products docs → Get a single product (negative behavior not specified).

## API-004 — Limit the product list to 10 items

- **Type / Priority:** Positive, limit boundary / P1
- **Preconditions:** At least 10 products available in catalog.
- **Request:** `GET https://dummyjson.com/products?limit=10`
- **Test data:** `limit=10`, implicit `skip=0`.
- **Steps:**
  1. Send GET with `limit=10`.
  2. Parse JSON and inspect the product list and pagination metadata.
- **Expected results:**
  1. HTTP 200; valid JSON list wrapper.
  2. `limit=10`, `skip=0`, `total >= 10`.
  3. Exactly 10 products are returned, each with a unique integer `id`.
- **Traceability:** Products docs → Limit and skip products.

## API-005 — Skip the first 10 products and return the next 10

- **Type / Priority:** Positive / P1
- **Preconditions:** At least 20 products available. Execute comparison calls in close succession if catalog changes are possible.
- **Request:** `GET https://dummyjson.com/products?limit=10&skip=10`
- **Comparison request:** `GET https://dummyjson.com/products?limit=20&skip=0`
- **Test data:** `limit=10`, `skip=10`.
- **Steps:**
  1. Request the first 20 products as a comparison baseline and record the ordered `id` values.
  2. Request `limit=10&skip=10`.
  3. Compare the response metadata and the returned IDs with baseline positions 11–20.
- **Expected results:**
  1. Both requests return HTTP 200 and valid JSON.
  2. Paginated response contains 10 products with `limit=10`, `skip=10`.
  3. The paginated response IDs match baseline IDs at indices 10–19 (zero-based) in the same order.
  4. `total` agrees between the two responses if the underlying dataset is unchanged.
- **Traceability:** Products docs → Limit and skip products.

## API-006 — Search products by query

- **Type / Priority:** Positive / P2
- **Preconditions:** Public product search is available.
- **Request:** `GET https://dummyjson.com/products/search?q=phone`
- **Test data:** `q=phone` (official example).
- **Steps:**
  1. Send GET with the URL-encoded query value `phone`.
  2. Inspect status, root response structure, and each returned product.
  3. Record the number of products and total search results.
- **Expected results:**
  1. HTTP 200 and valid JSON.
  2. Response contains `products` (array), `total` (non-negative integer), `skip` and `limit` (integers).
  3. Search returns at least one product for the documented example query, assuming the example dataset is available.
  4. Returned products have the documented product fields (`id`, `title`, `category`, `price`).
- **Specification gap:** The docs do not state which product fields are searched or whether matching is substring-, token-, or fuzzy-based. Do **not** require every product title to contain `phone` (the official example includes results with other titles). Exact relevance semantics need separate contract clarification.
- **Traceability:** Products docs → Search products.

## API-007 — Sort products by ascending price

- **Type / Priority:** Positive / P1
- **Preconditions:** At least two products are available; use non-filtered catalog.
- **Request:** `GET https://dummyjson.com/products?sortBy=price&order=asc`
- **Test data:** `sortBy=price`, `order=asc`.
- **Steps:**
  1. Send GET with both sorting parameters.
  2. Extract `price` values in the order returned.
  3. Compare each adjacent pair of prices.
- **Expected results:**
  1. HTTP 200; valid JSON object with product list.
  2. Every product has a numeric `price`.
  3. Prices are nondecreasing: for every adjacent pair, `price[i] <= price[i + 1]`.
  4. Equal prices may appear in any relative order; no secondary sort order is asserted.
- **Traceability:** Products docs → Sort products (`sortBy` accepts field names; `order` accepts `asc`/`desc`).

## API-008 — Filter products by category

- **Type / Priority:** Positive / P1
- **Preconditions:** Category `smartphones` appears in `GET /products/category-list` (official example).
- **Request:** `GET https://dummyjson.com/products/category/smartphones`
- **Test data:** category slug `smartphones`.
- **Steps:**
  1. Optionally confirm the slug appears in `GET /products/category-list`.
  2. Send GET to the category endpoint.
  3. Inspect response metadata and categories of returned products.
- **Expected results:**
  1. HTTP 200; valid JSON with `products` (array), `total`, `skip`, `limit`.
  2. At least one product is returned for this documented example category, assuming the example dataset is available.
  3. Every returned item has `category = "smartphones"`.
  4. `total` is at least the number of returned products.
- **Traceability:** Products docs → Get products by a category / Get products category list.

---

## Review and automation notes

1. **API-003**: Confirm the undocumented 404/error-body contract before promoting its expected results to automated pass/fail assertions.
2. **API-006**: Search relevance is only partially specified. Validate success, shape, and nonempty documented example; do not assume title-only matching.
3. **Catalog drift**: Prefer schema checks and relational assertions over hardcoded catalog totals, complete product names, or specific price values.
4. **Future enhancements**: Add parametrized boundary cases for `limit`/`skip`, zero results, malformed IDs, combined filtering and sorting, and response schema checks in separate test design iterations.
5. **Execution**: These cases have not yet been run; there are no Pass/Fail results at the time of writing.

## References

- [DummyJSON — Products API](https://dummyjson.com/docs/products)
- [DummyJSON — API overview](https://dummyjson.com/docs)
