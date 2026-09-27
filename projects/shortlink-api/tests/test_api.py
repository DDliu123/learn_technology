"""阶段 5 第 3 课：用 FastAPI TestClient 做「无浏览器」自动化测试。

TestClient 在内存里模拟 HTTP 请求，直接打路由函数，不用真起服务、不用浏览器。
跑法：uv run python tests/test_api.py
（和阶段 3/4 的 node xxx.test.mjs 一个思路：纯脚本断言，不引测试框架也能跑。）
"""
from fastapi.testclient import TestClient

from shortlink_api.app import app


def main():
    with TestClient(app) as client:
        # 1) 健康检查
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"

        # 2) 创建一个短链（201）
        r = client.post("/shorten", json={"url": "https://example.com/a"})
        assert r.status_code == 201
        code = r.json()["code"]
        assert r.json()["url"] == "https://example.com/a"

        # 3) 列表里包含它
        r = client.get("/links")
        assert any(item["code"] == code for item in r.json())

        # 4) 重定向：307 + Location 指向原网址（不跟随重定向，才能看到 307 本身）
        r = client.get(f"/{code}", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "https://example.com/a"

        # 5) 不存在的短码 → 404
        r = client.get("/__not_exist__")
        assert r.status_code == 404

        # 6) 删除 → 204；再删一次 → 404
        r = client.delete(f"/{code}")
        assert r.status_code == 204
        r = client.delete(f"/{code}")
        assert r.status_code == 404

        # 7) 校验失败 → 422
        r = client.post("/shorten", json={"url": "not-a-url"})
        assert r.status_code == 422

        # 8) 重复自定义短码 → 409
        client.post("/shorten", json={"url": "https://x.com", "code": "dup"})
        r = client.post("/shorten", json={"url": "https://y.com", "code": "dup"})
        assert r.status_code == 409

    print("ALL TESTS PASSED ✅")


if __name__ == "__main__":
    main()
