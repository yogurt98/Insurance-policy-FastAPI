# app/tests/test_policies.py
import pytest
from httpx import AsyncClient
from datetime import date


@pytest.mark.asyncio
async def test_create_policy_with_validation(client: AsyncClient):
    # 先注册这个账号
    await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testadmin",
            "email": "admin@insurance.ca",
            "role": "admin",
            "password": "Password123!"
        }
    )
    # 登录获取 token
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "Password123!"}
    )
    # 看看为什么没拿到 token
    if login_resp.status_code != 200:
        print(f"DEBUG: Login failed with {login_resp.json()}")

    token = login_resp.json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/policies/",
        json={
            "policy_number": "TEST123456",
            "customer_id": 99999,
            "product_type": "Auto",
            "premium": 1250.75,
            "start_date": "2025-04-01",
            "end_date": "2026-04-01",
            "risk_score": 45.0
        },
        headers=headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["policy_number"] == "TEST123456"
    assert data["osfi_compliance_flag"] is not None


@pytest.mark.asyncio
async def test_create_policy_high_risk_fraud(client: AsyncClient):
    # 在获取 token 的代码前加上注册：
    await client.post("/api/v1/auth/register", json={
        "username": "testadmin", "email": "admin@insurance.ca", "role": "admin", "password": "Password123!"
    })

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]

    response = await client.post(
        "/api/v1/policies/",
        json={
            "policy_number": "HIGH999999",
            "customer_id": 88888,
            "product_type": "Life",
            "premium": 15000.0,
            "start_date": "2025-03-01",
            "end_date": "2026-03-01",
            "risk_score": 92.0
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 400
    assert "风险分数过高" in response.json()["detail"] or "反欺诈" in response.json()["detail"]


@pytest.mark.asyncio
async def test_bulk_upload_csv(client: AsyncClient):
    # 在获取 token 的代码前加上注册：
    await client.post("/api/v1/auth/register", json={
        "username": "testadmin", "email": "admin@insurance.ca", "role": "admin", "password": "Password123!"
    })

    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "testadmin", "password": "Password123!"}
    )
    token = login_resp.json()["access_token"]

    # 创建一个简单的 CSV 内容
    csv_content = """policy_number,customer_id,product_type,premium,start_date,end_date,risk_score
TEST000001,11111,Auto,890.5,2025-01-01,2026-01-01,30.0
TEST000002,22222,Home,1450.0,2025-02-01,2026-02-01,55.0"""

    files = {"file": ("test.csv", csv_content, "text/csv")}

    response = await client.post(
        "/api/v1/policies/bulk-upload",
        files=files,
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code in (200, 202)
    data = response.json()
    assert "accepted" in data["message"] or "process" in data["message"]