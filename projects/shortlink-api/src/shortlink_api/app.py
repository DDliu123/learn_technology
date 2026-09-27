"""阶段 5 第 1–2 课：FastAPI 应用入口与路由。

路由函数职责单一：解析请求 → 调 store 层 → 拼响应 / 抛状态码。
数据形状由 models.py 定义，存储由 store.py 负责，本文件不碰具体存储实现。
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse

from .models import ShortLink, ShortenRequest
from .store import CodeTakenError, create_link, delete_link, get_link, list_links

# 创建应用实例。title / version 进 Swagger 文档（/docs）。
app = FastAPI(title="短链接服务", version="0.1.0")


@app.get("/")
def root():
    """访问根路径返回一句欢迎语，证明服务在跑、能返回 JSON。"""
    return {"message": "短链接服务已启动", "docs": "/docs"}


@app.get("/health")
def health():
    """健康检查：部署和监控常用，返回 200 + ok 即代表进程活着。"""
    return {"status": "ok"}


@app.get("/links", response_model=list[ShortLink])
def links():
    """列出当前所有短链。response_model 让返回的 ShortLink 列表按模型序列化、写入文档。"""
    return list_links()


@app.post("/shorten", response_model=ShortLink, status_code=status.HTTP_201_CREATED)
def shorten(req: ShortenRequest):
    """创建一个短链。

    - 请求体是 ShortenRequest：FastAPI 自动按 Pydantic 校验（url 必须合法、code 只能字母数字）。
      校验失败 → 自动返回 422，并带字段级错误，无需手写判断。
    - status_code=201：REST 约定「新建成功」用 201（而不是默认的 200）。
    - 自定义短码已存在 → 转成 409 Conflict。
    """
    try:
        return create_link(req)
    except CodeTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="自定义短码已存在"
        )


@app.get("/{code}")
def redirect(code: str):
    """按短码跳转到原网址。

    用 RedirectResponse 真正让浏览器跳转（不能返回 (307, {...}) 元组，那只是给 body 设了状态码）。
    307 = 临时重定向，保留原请求方法。不存在 → 404。
    放在 /links 等固定路由之后：FastAPI 按定义顺序匹配，固定路径优先于 {code} 通配。
    """
    link = get_link(code)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
    return RedirectResponse(url=link.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)


@app.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def remove(code: str):
    """删除一条短链。成功返回 204（无内容）；本就不存在 → 404。"""
    if not delete_link(code):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
