# app/tests/test_bulk.py
import pytest

@pytest.mark.asyncio
async def test_bulk_upload_csv(client):
    # 注册 admin_ci
    await client.post("/api/v1/auth/register", json={
        "username": "admin_ci", "email": "ci@test.com", "role": "admin", "password": "Admin123!"
    })

    # 用刚刚注册的 admin_ci 登录 ✅
    login = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin_ci", "password": "Admin123!"}
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    csv_content = """policy_number,customer_id,product_type,premium,start_date,end_date,risk_score
    BULK_CI_001,3001,Auto,890,2025-05-01,2026-05-01,35
    BULK_CI_002,3002,Home,2100,2025-06-01,2026-06-01,60"""

    files = {"file": ("test_ci.csv", csv_content, "text/csv")}

    response = await client.post(
        "/api/v1/policies/bulk-upload",
        files=files,
        headers=headers
    )
    assert response.status_code in (200, 202)
    assert "accepted" in response.json()["message"].lower()