from fastapi.testclient import TestClient
from main import app
from uuid import uuid4

client = TestClient(app)


def test_get_nonexistent_dish_returns_404():
    fake_id = str(uuid4())
    r = client.get(f"/menu/{fake_id}")
    assert r.status_code == 404
    assert r.json()["detail"] == f"Dish {fake_id} not found"


def test_update_nonexistent_dish_returns_404():
    fake_id = str(uuid4())
    payload = {"nombre": "Nope", "precio": 1.0}
    r = client.put(f"/menu/{fake_id}", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == f"Dish {fake_id} not found"


def test_delete_nonexistent_dish_returns_404():
    fake_id = str(uuid4())
    r = client.delete(f"/menu/{fake_id}")
    assert r.status_code == 404
    assert r.json()["detail"] == f"Dish {fake_id} not found"


def test_get_nonexistent_order_returns_404():
    fake_id = str(uuid4())
    r = client.get(f"/ordenes/{fake_id}")
    assert r.status_code == 404
    assert r.json()["detail"] == f"Order {fake_id} not found"


def test_update_nonexistent_order_returns_404():
    fake_id = str(uuid4())
    payload = {"estado": "entregado"}
    r = client.put(f"/ordenes/{fake_id}/estado", json=payload)
    assert r.status_code == 404
    assert r.json()["detail"] == f"Order {fake_id} not found"
