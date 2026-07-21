from scripts.seed_rbac import ROLES

import pytest_asyncio


@pytest_asyncio.fixture
def current_user_permissions():
    return ROLES["Viewer"]


async def test_create_medicine_forbidden_for_viewer(client, category_and_supplier):
    category, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "Paracetamol 500mg",
        "category_id": str(category.id),
        "supplier_id": str(supplier.id),
    })

    assert response.status_code == 403