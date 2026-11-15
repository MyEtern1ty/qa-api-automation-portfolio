# Running the DummyJSON API tests

These are **live integration tests** against the public [DummyJSON API](https://dummyjson.com/docs/products). The service requires Internet access; network failures do not automatically indicate product defects.

## Automated coverage

- API-001 Default product list
- API-002 Product lookup by existing ID
- API-003 Nonexistent product ID — **skipped until the undocumented 404/error-body contract is confirmed**
- API-004 Limit to 10 items
- API-005 Pagination with limit/skip
- API-006 Search for `phone` (response contract, not title-only matching)
- API-007 Ascending price sort
- API-008 Category filter

Seven tests are enabled and one is explicitly skipped. None have been declared Passed before execution. All are linked to IDs in [the manual test cases](test-cases/products.md).

## Local run

Install Python 3.12 or later, then run these commands in the repository root:

```bash
python -m venv .venv
# Windows (Git Bash): source .venv/Scripts/activate
# macOS / Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
python -m pytest -v
```

Set `DUMMYJSON_BASE_URL` to override the default `https://dummyjson.com`, if needed.

## GitHub Actions

Go to **Actions → DummyJSON API tests → Run workflow** to run the tests manually. A run also starts when a PR targets this repository or commits are pushed to `main`.

View the log under the `products-api` job. Download the `pytest-junit-results` artifact to inspect a machine-readable JUnit XML report (retained for 14 days).

## Interpretation

- **Passed:** assertion matched the live API response.
- **Failed:** an assertion, transport request, or JSON parsing failed; inspect the cause rather than assuming the API has a defect.
- **Skipped:** API-003 remains pending API contract clarification.

Do not commit tokens or credentials. The public product endpoints need no authentication.
