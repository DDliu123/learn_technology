"""阶段 5 第 2 课：内存存储层。

原则：存储逻辑单独放一个模块，路由函数（app.py）只关心「接请求、调存储、拼响应」。
以后把这里从 dict 换成数据库（阶段 6），app.py 一行都不用改。

注意：STORE 是进程内存里的 dict，重启服务数据全没。这是阶段性取舍——
阶段 5 先搞懂 REST / Pydantic / 状态码，持久化留到阶段 6 用 SQLModel + 数据库。
"""
import secrets
import string

from .models import ShortLink, ShortenRequest, now_iso

# 短码字符集：大小写字母 + 数字，共 62 个，足够短且 URL 安全。
ALPHABET = string.ascii_letters + string.digits

# 全局内存表：code -> ShortLink
STORE: dict[str, ShortLink] = {}


class CodeTakenError(Exception):
    """自定义短码已存在。由调用方（app.py）转成 HTTP 409。"""


def _generate_code(length: int = 6) -> str:
    # secrets 比 random 更适合「生成不可预测令牌」这类场景。
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def create_link(req: ShortenRequest) -> ShortLink:
    """创建一条短链。返回新建的 ShortLink。"""
    if req.code is not None:
        # 用户指定了短码：已占用就报错，不悄悄覆盖。
        if req.code in STORE:
            raise CodeTakenError(req.code)
        code = req.code
    else:
        # 随机生成 6 位短码；极小概率撞车，重抽几次。
        code = _generate_code()
        attempts = 0
        while code in STORE and attempts < 10:
            code = _generate_code()
            attempts += 1
        if code in STORE:
            raise RuntimeError("短码生成冲突，请重试")

    link = ShortLink(code=code, url=str(req.url), created_at=now_iso())
    STORE[code] = link
    return link


def get_link(code: str) -> ShortLink | None:
    """按短码取一条；不存在返回 None（调用方转成 404）。"""
    return STORE.get(code)


def list_links() -> list[ShortLink]:
    """列出全部短链（当前不排序，阶段 6 接数据库后可按时间排序）。"""
    return list(STORE.values())


def delete_link(code: str) -> bool:
    """删除一条；删成功返回 True，本就不存在返回 False（调用方转成 404）。"""
    return STORE.pop(code, None) is not None
