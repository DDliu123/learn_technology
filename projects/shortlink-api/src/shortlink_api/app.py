"""阶段 5–6：FastAPI 应用入口与路由。

路由函数职责单一：解析请求 → 调 store 层 → 拼响应 / 抛状态码。
- 数据形状由 models.py 定义（阶段 6 起是 SQLModel 表模型）
- 存储由 store.py 负责（阶段 6 起是 SQLite，不再是内存 dict）
本文件只管 HTTP 层，不碰存储实现。
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse

from .database import create_db_and_tables
from .models import LinkStats, ShortLink, ShortenRequest
from .store import (
    CodeTakenError,
    create_link,
    delete_link,
    get_link,
    get_stats,
    list_links,
    record_visit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期钩子：启动时建表。

    lifespan 是 FastAPI 推荐的启动/收尾写法（替代旧的 @app.on_event("startup")）。
    启动时执行一次 create_db_and_tables()，确保表存在再开始接请求。
    """
    create_db_and_tables()
    yield


app = FastAPI(title="短链接服务", version="0.1.0", lifespan=lifespan)


@app.get("/")
def root():
    """访问根路径返回一句欢迎语，证明服务在跑、能返回 JSON。"""
    return {"message": "短链接服务已启动", "docs": "/docs"}


@app.get("/health")
def health():
    """健康检查：部署和监控常用，返回 200 + ok 即代表进程活着。"""
    return {"status": "ok"}


@app.get("/links", response_model=list[ShortLink])
def links(search: str | None = None, sort: str = "created_at"):
    """列出短链，支持查询参数：

    - `?search=xxx`：在短码和原网址里模糊匹配
    - `?sort=code|url|created_at`：排序（默认 created_at 倒序）

    函数参数不是路径参数 → FastAPI 自动把它当成 URL 查询参数（?search=...）。
    """
    return list_links(search=search, sort=sort)


@app.post("/shorten", response_model=ShortLink, status_code=status.HTTP_201_CREATED)
def shorten(req: ShortenRequest):
    """创建一个短链。

    - 请求体 ShortenRequest：不符合 Pydantic 规则 → 自动 422。
    - 成功 → 201（REST 约定新建用 201）。
    - 自定义短码已占用 → 409。
    """
    try:
        return create_link(req)
    except CodeTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="自定义短码已存在"
        )


@app.get("/stats/{code}", response_model=LinkStats)
def stats(code: str):
    """查看某条短链的点击统计。短链不存在 → 404。

    用 /stats/{code} 而不是 /{code}/stats：后者和通配路由 /{code} 挨着容易混淆，
    前者路径更清晰，Swagger 里也好找。
    """
    result = get_stats(code)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
    return result


@app.get("/{code}")
def redirect(code: str, request: Request):
    """按短码跳转到原网址（307），并记一次访问。不存在 → 404。

    用 RedirectResponse 真正让浏览器跳转。固定路由（/links、/stats/{code} 等）
    定义在它之前 —— FastAPI 按定义顺序匹配，固定路径优先于 {code} 通配。
    """
    link = get_link(code)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
    # 先记访问，再跳转。user_agent 从请求头里取，便于以后分析来源。
    record_visit(code, user_agent=request.headers.get("user-agent"))
    return RedirectResponse(url=link.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def remove(code: str):
    """删除一条短链。成功 204（无内容）；不存在 → 404。"""
    if not delete_link(code):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
