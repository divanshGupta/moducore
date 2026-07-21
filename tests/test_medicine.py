import uuid


async def test_create_medicine(client, category_and_supplier):
    category, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "Paracetamol 500mg",
        "category_id": str(category.id),
        "supplier_id": str(supplier.id),
    })

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Paracetamol 500mg"


async def test_create_medicine_missing_name(client, category_and_supplier):
    category, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "category_id": str(category.id),
        "supplier_id": str(supplier.id),
    })

    # HTTP 422 = unprocessable content
    assert response.status_code == 422


async def test_create_medicine_empty_name(client, category_and_supplier):
    category, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "",
        "category_id": str(category.id),
        "supplier_id": str(supplier.id),
    })

    assert response.status_code == 422


async def test_create_medicine_name_too_long(client, category_and_supplier):
    category, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "a" * 201,
        "category_id": str(category.id),
        "supplier_id": str(supplier.id),
    })

    assert response.status_code == 422


async def test_create_medicine_invalid_category(client, category_and_supplier):
    # _ is the idiomatic way to say "I am recieving this value because i have to unpack the tuple, but i am deliberately not using it."
    _, supplier = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "Paracetamol 500mg",
        "category_id": str(uuid.uuid4()),
        "supplier_id": str(supplier.id),
    })

    assert response.status_code == 400


async def test_create_medicine_invalid_supplier(client, category_and_supplier):
    category, _ = category_and_supplier

    response = await client.post("/medicines", json={
        "name": "Paracetamol 500mg",
        "category_id": str(category.id),
        "supplier_id": str(uuid.uuid4()),
    })

    assert response.status_code == 400
