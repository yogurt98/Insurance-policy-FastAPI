# app/tests/test_auth.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testuser",
            "email": "testuser@insurance.ca",
            "role": "underwriter",
            "password": "TestPassword123!"
        }
    )
    assert response.status_code == 201
    if response.status_code != 201:
        print(f"REGISTER FAILED: {response.json()}") # 打印具体是哪个字段没过校验
    data = response.json()
    assert data["username"] == "testuser"
    assert data["role"] == "underwriter"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    # 先注册
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "loginuser",
            "email": "login@insurance.ca",
            "role": "admin",
            "password": "LoginPass123!"
        }
    )

    # 再登录
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "loginuser", "password": "LoginPass123!"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()