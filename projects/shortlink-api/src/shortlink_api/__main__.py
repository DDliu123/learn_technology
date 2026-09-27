"""允许 `uv run python -m shortlink_api` 直接启动开发服务器。

等价于 `uv run fastapi dev src/shortlink_api/app.py`，只是多一种启动方式。
reload=True：代码改动后自动重启，仅开发环境使用。
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("shortlink_api.app:app", host="127.0.0.1", port=8000, reload=True)
