"""阶段 7：密码哈希 + JWT 签发/校验（纯加密层，不碰数据库）。

刻意不 import store：store 需要这里的 hash_password，如果这里又 import store 就成循环导入了。
「依赖数据库」的那部分（get_current_user）放在 deps.py，由它同时 import 两边。
"""
import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

# 签名密钥。**生产必须用环境变量设成随机长字符串，绝不能写死在代码里提交**。
# 默认值只用于本地开发；注意密钥太短 PyJWT 会警告（HS256 建议 ≥32 字节）。
SECRET_KEY = os.getenv(
    "SHORTLINK_SECRET", "dev-only-secret-please-replace-with-random-32byte-string"
)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def hash_password(plain: str) -> str:
    """明文 → 哈希。

    bcrypt 自带随机盐：同一个密码哈希两次结果不同，所以撞库/彩虹表失效。
    """
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """登录校验：拿用户提交的明文和库里存的哈希比对。

    哈希不可逆（没法从哈希反推明文），只能「正着再算一遍看是否一致」。
    """
    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:  # 库里哈希格式不对（脏数据）时按"不匹配"处理
        return False


def create_access_token(
    username: str, expires_delta: timedelta | None = None
) -> str:
    """签发 JWT。

    payload 放两样：
    - sub（subject）：这是谁
    - exp（expiration）：什么时候过期，过期后 token 自动作废
    """
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> str | None:
    """解 JWT。签名不对 / 已过期 / 被人改过 → 返回 None。

    所有失败统一吞掉返回 None，由调用方决定怎么报错 —— 不把细节抛给前端（避免泄露信息）。
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.PyJWTError:
        return None
    return payload.get("sub")
