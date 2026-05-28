"""
Small client script showing how a consumer can call the Library API.

Run:
    python scripts/sample_client.py

Optional:
    LIBRARY_API_BASE_URL=http://127.0.0.1:8000 python scripts/sample_client.py
"""

from __future__ import annotations

import os

import requests

BASE_URL = os.getenv("LIBRARY_API_BASE_URL", "http://127.0.0.1:8000")


def call(method: str, path: str, payload: dict | None = None) -> dict:
    response = requests.request(method, f"{BASE_URL}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def main() -> None:
    print(f"Using API: {BASE_URL}")

    member = call(
        "POST",
        "/members",
        {
            "name": "Sample User",
            "email": "sample.user@example.com",
            "phone": "9999999999",
        },
    )
    print("Created member:", member)

    book = call(
        "POST",
        "/books",
        {
            "title": "Sample Book",
            "author": "Sample Author",
            "description": "Demo title",
        },
    )
    print("Created book:", book)

    borrowing = call(
        "POST",
        "/borrowings/borrow",
        {"member_id": member["id"], "book_id": book["id"]},
    )
    print("Borrowed book:", borrowing)

    returned = call("POST", f"/borrowings/{borrowing['id']}/return")
    print("Returned book:", returned)


if __name__ == "__main__":
    main()
