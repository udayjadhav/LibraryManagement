import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db import Base, get_db
from app.main import app

# Keep tests file-free by using in-memory async SQLite.
TEST_DATABASE_URL = "sqlite+aiosqlite://"
engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)


@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


def test_ui_root_is_served():
    response = client.get("/")
    assert response.status_code == 200
    assert "Neighborhood Library UI" in response.text


def test_create_and_update_book():
    created = client.post(
        "/books",
        json={
            "title": "The Hobbit",
            "author": "J.R.R. Tolkien",
            "description": "Fantasy",
        },
    )
    assert created.status_code == 201
    assert created.json()["is_borrowed"] is False

    updated = client.put(
        f"/books/{created.json()['id']}", json={"title": "The Hobbit (Updated)"}
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "The Hobbit (Updated)"


def test_book_duplicate_is_rejected_case_insensitive():
    first = client.post(
        "/books",
        json={"title": "Dune", "author": "Frank Herbert", "description": "Sci-fi"},
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/books",
        json={"title": " dune ", "author": " FRANK HERBERT ", "description": "Classic"},
    )
    assert duplicate.status_code == 409
    assert (
        duplicate.json()["detail"] == "Book with same title and author already exists"
    )


def test_book_duplicate_on_update_is_rejected():
    first = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    second = client.post("/books", json={"title": "1984", "author": "George Orwell"})
    assert first.status_code == 201
    assert second.status_code == 201

    duplicate_update = client.put(
        f"/books/{second.json()['id']}",
        json={"title": " dune ", "author": " FRANK HERBERT "},
    )
    assert duplicate_update.status_code == 409
    assert (
        duplicate_update.json()["detail"]
        == "Book with same title and author already exists"
    )


def test_member_duplicate_email_is_rejected_case_insensitive():
    first = client.post(
        "/members",
        json={"name": "Alice", "email": "alice@example.com"},
    )
    assert first.status_code == 201

    duplicate = client.post(
        "/members",
        json={"name": "Another", "email": " ALICE@EXAMPLE.COM "},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "Member email already exists"


def test_member_duplicate_email_on_update_is_rejected_case_insensitive():
    first = client.post(
        "/members", json={"name": "Alice", "email": "alice@example.com"}
    )
    second = client.post("/members", json={"name": "Bob", "email": "bob@example.com"})
    assert first.status_code == 201
    assert second.status_code == 201

    duplicate_update = client.put(
        f"/members/{second.json()['id']}", json={"email": " ALICE@EXAMPLE.COM "}
    )
    assert duplicate_update.status_code == 409
    assert duplicate_update.json()["detail"] == "Member email already exists"


def test_member_borrow_return_flow():
    member = client.post(
        "/members",
        json={"name": "Alice", "email": "alice@example.com", "phone": "1234567890"},
    )
    book = client.post("/books", json={"title": "Dune", "author": "Frank Herbert"})
    assert member.status_code == 201
    assert book.status_code == 201

    borrowing = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert borrowing.status_code == 201
    borrowing_id = borrowing.json()["id"]

    # Active borrowings should include the new checkout.
    active = client.get("/borrowings")
    assert active.status_code == 200
    assert len(active.json()) == 1

    # Trying to borrow an already borrowed book should fail.
    second_try = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert second_try.status_code == 409

    returned = client.post(f"/borrowings/{borrowing_id}/return")
    assert returned.status_code == 200
    assert returned.json()["returned_at"] is not None

    # Active-only listing becomes empty after return.
    active_after_return = client.get("/borrowings")
    assert active_after_return.status_code == 200
    assert active_after_return.json() == []


def test_list_borrowings_by_member():
    m1 = client.post("/members", json={"name": "A", "email": "a@example.com"})
    m2 = client.post("/members", json={"name": "B", "email": "b@example.com"})
    b1 = client.post("/books", json={"title": "Book A", "author": "Author A"})
    b2 = client.post("/books", json={"title": "Book B", "author": "Author B"})

    client.post(
        "/borrowings/borrow",
        json={"member_id": m1.json()["id"], "book_id": b1.json()["id"]},
    )
    client.post(
        "/borrowings/borrow",
        json={"member_id": m2.json()["id"], "book_id": b2.json()["id"]},
    )

    m1_borrowings = client.get(f"/borrowings?member_id={m1.json()['id']}")
    assert m1_borrowings.status_code == 200
    assert len(m1_borrowings.json()) == 1
    assert m1_borrowings.json()[0]["member_id"] == m1.json()["id"]


def test_active_only_false_includes_returned_records():
    member = client.post(
        "/members", json={"name": "Filter", "email": "filter@example.com"}
    )
    book = client.post(
        "/books", json={"title": "Filter Book", "author": "Filter Author"}
    )
    borrowing = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert borrowing.status_code == 201
    returned = client.post(f"/borrowings/{borrowing.json()['id']}/return")
    assert returned.status_code == 200

    active_only_true = client.get("/borrowings")
    assert active_only_true.status_code == 200
    assert active_only_true.json() == []

    active_only_false = client.get("/borrowings?active_only=false")
    assert active_only_false.status_code == 200
    assert len(active_only_false.json()) == 1
    assert active_only_false.json()[0]["returned_at"] is not None


def test_inactive_member_cannot_borrow():
    member = client.post(
        "/members",
        json={"name": "Inactive", "email": "inactive@example.com"},
    )
    book = client.post("/books", json={"title": "1984", "author": "George Orwell"})
    assert member.status_code == 201
    assert book.status_code == 201

    deactivated = client.put(f"/members/{member.json()['id']}", json={"active": False})
    assert deactivated.status_code == 200
    assert deactivated.json()["active"] is False

    response = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Inactive member cannot borrow books"


def test_borrow_missing_member_or_book():
    book = client.post(
        "/books", json={"title": "Sapiens", "author": "Yuval Noah Harari"}
    )
    member = client.post("/members", json={"name": "Bob", "email": "bob@example.com"})
    assert book.status_code == 201
    assert member.status_code == 201

    missing_member = client.post(
        "/borrowings/borrow",
        json={"member_id": 9999, "book_id": book.json()["id"]},
    )
    assert missing_member.status_code == 404
    assert missing_member.json()["detail"] == "Member not found"

    missing_book = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": 9999},
    )
    assert missing_book.status_code == 404
    assert missing_book.json()["detail"] == "Book not found"


def test_return_missing_borrowing():
    response = client.post("/borrowings/9999/return")
    assert response.status_code == 404
    assert response.json()["detail"] == "Borrowing record not found"


def test_double_return_is_rejected():
    member = client.post(
        "/members", json={"name": "Carol", "email": "carol@example.com"}
    )
    book = client.post(
        "/books", json={"title": "Clean Code", "author": "Robert Martin"}
    )
    borrowing = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert borrowing.status_code == 201

    first_return = client.post(f"/borrowings/{borrowing.json()['id']}/return")
    assert first_return.status_code == 200

    second_return = client.post(f"/borrowings/{borrowing.json()['id']}/return")
    assert second_return.status_code == 409
    assert second_return.json()["detail"] == "Book already returned"


def test_book_can_be_borrowed_again_after_return():
    member = client.post(
        "/members", json={"name": "Retry", "email": "retry@example.com"}
    )
    book = client.post("/books", json={"title": "Retry Book", "author": "Retry Author"})
    first_borrowing = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert first_borrowing.status_code == 201

    returned = client.post(f"/borrowings/{first_borrowing.json()['id']}/return")
    assert returned.status_code == 200

    second_borrowing = client.post(
        "/borrowings/borrow",
        json={"member_id": member.json()["id"], "book_id": book.json()["id"]},
    )
    assert second_borrowing.status_code == 201
