"""阶段 7：带登录与归属隔离的接口测试（无浏览器，TestClient）。

跑法：uv run python tests/test_api.py
要点：
- engine 在 import app 时创建，所以环境变量必须**在 import 之前**设好（阶段 6 的坑）。
- 阶段 7 起管理接口都要带 token，测试里先注册登录再操作。
"""
import os
from pathlib import Path

os.environ["SHORTLINK_DB_URL"] = "sqlite:///./test_shortlink.db"
Path("test_shortlink.db").unlink(missing_ok=True)

from fastapi.testclient import TestClient  # noqa: E402

from shortlink_api.app import app  # noqa: E402

ALICE = {"username": "alice", "password": "secret123"}
BOB = {"username": "bob", "password": "bobpass123"}


def login(client, user):
    """登录拿 token，返回带 Authorization 的请求头。"""
    r = client.post("/token", data={"username": user["username"], "password": user["password"]})
    assert r.status_code == 200, r.text
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def main():
    with TestClient(app) as client:
        # 1) 健康检查（公开）
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"

        # 2) 注册 → 201，且响应里绝不能出现密码
        r = client.post("/register", json=ALICE)
        assert r.status_code == 201, r.text
        body = r.json()
        assert body["username"] == "alice"
        assert "password" not in body and "hashed_password" not in body

        # 3) 重复注册 → 409
        r = client.post("/register", json=ALICE)
        assert r.status_code == 409

        # 4) 密码太短 → 422（Pydantic 在入口就拦住）
        r = client.post("/register", json={"username": "carl", "password": "123"})
        assert r.status_code == 422

        # 5) 密码错 → 401
        r = client.post("/token", data={"username": "alice", "password": "wrong"})
        assert r.status_code == 401

        # 6) 不带 token 创建短链 → 401
        r = client.post("/shorten", json={"url": "https://example.com/a"})
        assert r.status_code == 401

        # 7) 登录后创建 → 201，owner 自动记为 alice
        headers = login(client, ALICE)
        r = client.post("/shorten", json={"url": "https://example.com/a"}, headers=headers)
        assert r.status_code == 201, r.text
        code = r.json()["code"]
        assert r.json()["owner"] == "alice"

        # 8) 不带 token 看列表 → 401；带 token 只能看到自己的
        assert client.get("/links").status_code == 401
        r = client.get("/links", headers=headers)
        assert r.status_code == 200
        assert [item["code"] for item in r.json()] == [code]

        # 9) 跳转是公开的（不带 token 也能跳），并会记一次访问
        r = client.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "https://example.com/a"

        # 10) 统计只能看自己的
        r = client.get(f"/stats/{code}", headers=headers)
        assert r.status_code == 200
        assert r.json()["clicks"] == 1
        assert client.get(f"/stats/{code}").status_code == 401  # 无 token

        # 11) 别人（bob）注册后，看不到也删不掉 alice 的链
        client.post("/register", json=BOB)
        bob_headers = login(client, BOB)
        assert client.get("/links", headers=bob_headers).json() == []  # bob 看不到
        r = client.delete(f"/{code}", headers=bob_headers)
        assert r.status_code == 403, r.text  # 越权删除 → 403
        r = client.get(f"/stats/{code}", headers=bob_headers)
        assert r.status_code == 404  # 别人的统计对自己表现为"不存在"

        # 12) 自己删自己的 → 204；再删 → 404
        r = client.delete(f"/{code}", headers=headers)
        assert r.status_code == 204
        assert client.delete(f"/{code}", headers=headers).status_code == 404

        # 13) 伪造 token → 401
        r = client.get("/links", headers={"Authorization": "Bearer fake.token.here"})
        assert r.status_code == 401

    print("ALL TESTS PASSED ✅")


if __name__ == "__main__":
    main()
