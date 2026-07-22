import uuid


# calls the real /users endpoint not db_session.add() - we want real hashing, service
async def _register_user(client, email: str = "auth_test@example.com", password: str = "supersecret123"):
    response = await client.post("/users", json={
        "email": email,
        "username": "auth_test_user",
        "password": password,
    })
    assert response.status_code == 201
    return email, password


# login
async def test_login_success(client):
    email, password = await _register_user(client)

    response = await client.post("/users/login", json={
        "email": email,
        "password": password,
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


async def test_login_wrong_password(client):
    email, _ = await _register_user(client)

    response = await client.post("/users/login", json={
        "email": email,
        "password": "wrong-password",
    })

    assert response.status_code == 401


async def test_login_nonexistent_email(client):
    response = await client.post("/users/login", json={
        "email": "nobody@example.com",
        "password": "whatever123",
    })

    assert response.status_code == 401


# refresh (the rotation mechanism)
async def test_refresh_success(client):
    email, password = await _register_user(client)
    login_response = await client.post("/users/login", json={"email": email, "password": password})
    original_refresh_token = login_response.json()["refresh_token"]

    response = await client.post("/auth/refresh", json={"refresh_token": original_refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert data["refresh_token"] != original_refresh_token


async def test_refresh_with_garbage_token(client):
    response = await client.post("/auth/refresh", json={"refresh_token": "not-a-real-token"})

    assert response.status_code == 401


# token reuse detection
async def test_refresh_reuse_detected(client):
    email, password = await _register_user(client)
    login_response = await client.post("/users/login", json={"email": email, "password": password})
    token_a = login_response.json()["refresh_token"]

    # Use token A once — legitimate rotation, gets token B.
    first_refresh = await client.post("/auth/refresh", json={"refresh_token": token_a})
    assert first_refresh.status_code == 200

    # Use token A again — it's now revoked. This should be caught as reuse.
    second_refresh = await client.post("/auth/refresh", json={"refresh_token": token_a})

    assert second_refresh.status_code == 401


async def test_refresh_reuse_revokes_entire_chain(client):
    email, password = await _register_user(client)
    login_response = await client.post("/users/login", json={"email": email, "password": password})
    token_a = login_response.json()["refresh_token"]

    first_refresh = await client.post("/auth/refresh", json={"refresh_token": token_a})
    token_b = first_refresh.json()["refresh_token"]

    # Trigger reuse detection using token A again.
    reuse_response = await client.post("/auth/refresh", json={"refresh_token": token_a})
    assert reuse_response.status_code == 401

    # Token B was legitimately issued, but the whole chain should now be dead.
    response = await client.post("/auth/refresh", json={"refresh_token": token_b})

    assert response.status_code == 401


# logout
async def test_logout_revokes_token(client):
    email, password = await _register_user(client)
    login_response = await client.post("/users/login", json={"email": email, "password": password})
    refresh_token = login_response.json()["refresh_token"]

    logout_response = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    assert logout_response.status_code == 204

    response = await client.post("/auth/refresh", json={"refresh_token": refresh_token})

    assert response.status_code == 401


async def test_logout_is_idempotent(client):
    email, password = await _register_user(client)
    login_response = await client.post("/users/login", json={"email": email, "password": password})
    refresh_token = login_response.json()["refresh_token"]

    first_logout = await client.post("/auth/logout", json={"refresh_token": refresh_token})
    second_logout = await client.post("/auth/logout", json={"refresh_token": refresh_token})

    assert first_logout.status_code == 204
    assert second_logout.status_code == 204