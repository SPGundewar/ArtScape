import pytest
from fastapi import HTTPException

import routes               # this will load app/routes.py when PYTHONPATH=./app
from routes import create_order
import models, schemas      # same style as routes.py uses


class FakeDB:
    """
    Minimal fake DB session that satisfies the methods used in create_order.
    """
    def __init__(self):
        self.added = []

    def add(self, obj):
        self.added.append(obj)

    def commit(self):
        pass

    def refresh(self, obj):
        pass


def make_fake_get(status_code, json_payload=None):
    """
    Returns a fake requests.get function that yields a response
    with given status and JSON payload.
    """
    if json_payload is None:
        json_payload = {}

    def fake_get(url, headers=None, timeout=None):
        class Resp:
            def __init__(self):
                self.status_code = status_code
            def json(self):
                return json_payload
        return Resp()
    return fake_get


def make_fake_post(status_code):
    """
    Returns a fake requests.post function that yields a response
    with given status.
    """
    def fake_post(url, headers=None, timeout=None):
        class Resp:
            def __init__(self):
                self.status_code = status_code
        return Resp()
    return fake_post


# ==============================
#  BLACK-BOX TESTS (ECP) – 5
# ==============================

def test_bb1_happy_path_user(monkeypatch):
    """
    BB1: Happy path – allowed role, artwork exists and unsold, mark_sold OK.
    Expect a confirmed order.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 1, "is_sold": False}))
    monkeypatch.setattr(routes.requests, "post",
                        make_fake_post(200))

    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    result = create_order(order_in=order_in, token=token, user=user, db=db)

    assert isinstance(result, models.Order)
    assert result.art_id == 1
    assert result.buyer == "alice"
    assert result.status == "confirmed"
    assert db.added and db.added[0] is result


def test_bb2_forbidden_role_artist():
    """
    BB2: Forbidden role – role not in {user, admin}.
    Expect HTTP 403.
    """
    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "artist1", "role": "artist"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 403
    assert "Only users or admins can place orders" in excinfo.value.detail


def test_bb3_artwork_not_found(monkeypatch):
    """
    BB3: Artwork does not exist – GET returns non-200.
    Expect HTTP 400 with 'Artwork not found'.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(404, {}))

    order_in = schemas.OrderCreate(art_id=999)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Artwork not found" in excinfo.value.detail


def test_bb4_artwork_already_sold(monkeypatch):
    """
    BB4: Artwork already sold – GET 200 but is_sold = True.
    Expect HTTP 400 with 'Artwork already sold'.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 1, "is_sold": True}))

    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Artwork already sold" in excinfo.value.detail


def test_bb5_mark_sold_fails(monkeypatch):
    """
    BB5: Mark-as-sold fails – GET 200 unsold, POST non-200.
    Expect HTTP 400 with 'Failed to reserve artwork'.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 1, "is_sold": False}))
    monkeypatch.setattr(routes.requests, "post",
                        make_fake_post(500))

    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Failed to reserve artwork" in excinfo.value.detail


# =========================================
#  WHITE-BOX TESTS (CONTROL FLOW) – 5
# =========================================

def test_wb1_happy_path_admin(monkeypatch):
    """
    WB1: Happy path via admin role.
    Path: allowed → GET 200, unsold → POST 200 → DB + return.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 42, "is_sold": False}))
    monkeypatch.setattr(routes.requests, "post",
                        make_fake_post(200))

    order_in = schemas.OrderCreate(art_id=42)
    token = "fake-token"
    user = {"sub": "admin-user", "role": "admin"}
    db = FakeDB()

    result = create_order(order_in=order_in, token=token, user=user, db=db)

    assert isinstance(result, models.Order)
    assert result.art_id == 42
    assert result.buyer == "admin-user"
    assert result.status == "confirmed"


def test_wb2_role_check_denied():
    """
    WB2: Role check fails at the first if.
    Path: denied → 403.
    """
    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "artist1", "role": "artist"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 403


def test_wb3_get_artwork_not_found(monkeypatch):
    """
    WB3: GET returns non-200.
    Path: allowed → GET 404 → 400 'Artwork not found'.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(404, {}))

    order_in = schemas.OrderCreate(art_id=123)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Artwork not found" in excinfo.value.detail


def test_wb4_artwork_already_sold_path(monkeypatch):
    """
    WB4: Artwork is already sold.
    Path: allowed → GET 200 → is_sold True → 400.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 1, "is_sold": True}))

    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Artwork already sold" in excinfo.value.detail


def test_wb5_mark_sold_fails_path(monkeypatch):
    """
    WB5: mark_sold fails.
    Path: allowed → GET 200, unsold → POST 500 → 400 'Failed to reserve artwork'.
    """
    monkeypatch.setattr(routes.requests, "get",
                        make_fake_get(200, {"id": 1, "is_sold": False}))
    monkeypatch.setattr(routes.requests, "post",
                        make_fake_post(500))

    order_in = schemas.OrderCreate(art_id=1)
    token = "fake-token"
    user = {"sub": "alice", "role": "user"}
    db = FakeDB()

    with pytest.raises(HTTPException) as excinfo:
        create_order(order_in=order_in, token=token, user=user, db=db)

    assert excinfo.value.status_code == 400
    assert "Failed to reserve artwork" in excinfo.value.detail
