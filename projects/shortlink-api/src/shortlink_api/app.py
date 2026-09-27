"""阶段 5–7：FastAPI 应用入口与路由。

分层：models.py 管数据形状，store.py 管存储，auth.py 管加密，deps.py 管鉴权，
本文件只管 HTTP —— 接请求、调下面几层、抛状态码。
"""
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm

from .auth import create_access_token
from .database import create_db_and_tables
from .deps import get_current_user
from .models import (
    LinkStats,
    ShortLink,
    ShortenRequest,
    User,
    UserCreate,
    UserRead,
)
from .store import (
    CodeTakenError,
    NotOwnerError,
    UserExistsError,
    create_link,
    create_user,
    delete_link,
    get_link,
    get_stats,
    get_user_by_credentials,
    list_links,
    record_visit,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动时建表（新表会建，老表结构不会改 —— 见阶段 6 迁移）。"""
    create_db_and_tables()
    yield


app = FastAPI(title="短链接服务", version="0.1.0", lifespan=lifespan)


# ---------- 公开接口 ----------


@app.get("/")
def root():
    return {"message": "短链接服务已启动", "docs": "/docs"}


@app.get("/health")
def health():
    """健康检查：部署和监控常用，返回 200 + ok 即代表进程活着。"""
    return {"status": "ok"}


# ---------- 注册 / 登录 ----------


@app.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(req: UserCreate):
    """注册。密码在这里被哈希，响应里**只回 id/username/created_at**，不含密码。

    用户名已存在 → 409。
    """
    try:
        return create_user(req)
    except UserExistsError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已被注册")


@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """登录换 token。

    用 **表单**（不是 JSON）提交 username/password —— 这是 OAuth2 密码流的约定，
    好处是 /docs 的锁图标能直接用这个接口登录。

    用户名或密码错 → 401。注意：不区分「用户不存在」和「密码错」，
    统一返回同一句提示，避免被人用错误信息探测哪些用户名存在。
    """
    user = get_user_by_credentials(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {
        "access_token": create_access_token(user.username),
        "token_type": "bearer",
    }


# ---------- 短链管理（需登录） ----------


@app.get("/links", response_model=list[ShortLink])
def links(
    search: str | None = None,
    sort: str = "created_at",
    current_user: User = Depends(get_current_user),
):
    """列出**我的**短链。加了 current_user 依赖 → 不带 token 直接 401。"""
    return list_links(search=search, sort=sort, owner=current_user.username)


@app.post("/shorten", response_model=ShortLink, status_code=status.HTTP_201_CREATED)
def shorten(
    req: ShortenRequest,
    current_user: User = Depends(get_current_user),
):
    """创建短链，归属人自动记为当前登录用户（不信任请求体里的 owner）。"""
    try:
        return create_link(req, owner=current_user.username)
    except CodeTakenError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="自定义短码已存在"
        )


@app.get("/stats/{code}", response_model=LinkStats)
def stats(
    code: str,
    current_user: User = Depends(get_current_user),
):
    """查看**我的**短链的点击统计。不是你的 → 404（不暴露它是否存在）。"""
    result = get_stats(code, owner=current_user.username)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
    return result


@app.delete("/{code}", status_code=status.HTTP_204_NO_CONTENT)
def remove(
    code: str,
    current_user: User = Depends(get_current_user),
):
    """删除**我的**短链。别人的 → 403；不存在 → 404。"""
    try:
        deleted = delete_link(code, owner=current_user.username)
    except NotOwnerError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="不能删除别人的短链"
        )
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")


# ---------- 跳转（公开，不要求登录） ----------


@app.get("/{code}")
def redirect(code: str, request: Request):
    """按短码跳转（307），并记一次访问。

    **公开接口**：别人点短链不该要求登录，所以这里没有 Depends(get_current_user)。
    产品取舍：跳转公开，管理（列表/删除/统计）必须登录且只能操作自己的。
    路由顺序：/links、/shorten、/stats/{code} 都定义在它之前，固定路径优先于 {code} 通配。
    """
    link = get_link(code)
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="短码不存在")
    record_visit(code, user_agent=request.headers.get("user-agent"))
    return RedirectResponse(url=link.url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
