"""阶段 7：鉴权依赖（需要同时用到 auth 和 store，所以单独一个模块）。

把「当前登录用户」变成一个路由参数：
    def xxx(current_user: User = Depends(get_current_user))
FastAPI 会自动：取 Authorization 头 → 校验 JWT → 查库 → 把 User 对象注入进来。
没带 token 或 token 失效 → 直接 401，路由函数根本不会被执行。
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .auth import decode_token
from .models import User
from .store import get_user

# 告诉 Swagger：token 要去 POST /token 拿。
# 有了它，/docs 右上角出现锁图标，能直接登录并自动带上 Authorization 头。
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="登录已失效，请重新登录",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = decode_token(token)
    if username is None:
        raise credentials_error
    user = get_user(username)
    if user is None:  # token 里的用户已被删除
        raise credentials_error
    return user
