"""阶段 6：用 FastAPI TestClient 做「无浏览器」自动化测试。

TestClient 在内存里模拟 HTTP 请求，直接打路由函数，不用真起服务、不用浏览器。
跑法：uv run python tests/test_api.py

阶段 6 新增要点：**测试要用独立数据库**，否则会往开发库 shortlink.db 里塞脏数据。
做法：在 import app 之前设环境变量，让 database.py 建 engine 时读到临时库地址。
顺序很重要——engine 在 import 时就创建了，晚设就没用。
"""
import os
from pathlib import Path

# 必须在 import app 之前设置：database.py 在导入时按环境变量建 engine。
os.environ["SHORTLINK_DB_URL"] = "sqlite:///./test_shortlink.db"
# 删掉上一次的测试库，保证每次从空库开始（结果可预测）。
Path("test_shortlink.db").unlink(missing_ok=True)

from fastapi.testclient import TestClient  # noqa: E402

from shortlink_api.app import app  # noqa: E402


def main():
    with TestClient(app) as client:
        # 1) 健康检查
        r = client.get("/health")
        assert r.status_code == 200 and r.json()["status"] == "ok"

        # 2) 创建一个短链（201）
        r = client.post("/shorten", json={"url": "https://example.com/a"})
        assert r.status_code == 201
        data = r.json()
        code = data["code"]
        assert data["url"] == "https://example.com/a"
        # 阶段 6：数据库主键 id 由数据库生成并回填
        assert data["id"] is not None

        # 3) 列表里包含它
        r = client.get("/links")
        assert any(item["code"] == code for item in r.json())

        # 4) 重定向：307 + Location 指向原网址（不跟随重定向才能断言到 307 本身）
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

        # 7) 删掉后列表里不该再有它
        r = client.get("/links")
        assert not any(item["code"] == code for item in r.json())

        # 8) 校验失败 → 422
        r = client.post("/shorten", json={"url": "not-a-url"})
        assert r.status_code == 422

        # 9) 重复自定义短码 → 409
        client.post("/shorten", json={"url": "https://x.com", "code": "dup"})
        r = client.post("/shorten", json={"url": "https://y.com", "code": "dup"})
        assert r.status_code == 409

        # 10) 访问统计：跳 3 次 → clicks 应该是 3
        r = client.post("/shorten", json={"url": "https://counted.com", "code": "cnt"})
        assert r.status_code == 201
        for _ in range(3):
            r = client.get("/cnt", follow_redirects=False)
            assert r.status_code == 307
        r = client.get("/stats/cnt")
        assert r.status_code == 200
        body = r.json()
        assert body["clicks"] == 3, body
        assert len(body["recent_visits"]) > 0
        # 注意：AnyHttpUrl 会把 "https://counted.com" 规范化成带尾斜杠的
        # "https://counted.com/"（阶段 5 讲过的行为），这里按规范化后的值断言。
        assert body["url"] == "https://counted.com/"

        # 11) 给不存在的短码查统计 → 404
        r = client.get("/stats/__not_exist__")
        assert r.status_code == 404

    print("ALL TESTS PASSED ✅")


if __name__ == "__main__":
    main()
