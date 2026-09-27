"""阶段 7：存储层。短链归属到用户，管理操作按 owner 隔离。

约定：
- 「跳转」是公开的（别人点短链不该要求登录），所以 get_link / record_visit 不校验 owner。
- 「管理」（列表 / 删除 / 统计）必须只能操作自己的，越权抛 NotOwnerError → 403。
"""
import secrets
import string

from sqlmodel import Session, func, or_, select

from .auth import hash_password, verify_password
from .database import engine
from .models import (
    LinkStats,
    ShortLink,
    ShortenRequest,
    User,
    UserCreate,
    Visit,
)

# 短码字符集：大小写字母 + 数字，共 62 个，足够短且 URL 安全。
ALPHABET = string.ascii_letters + string.digits


class CodeTakenError(Exception):
    """短码已存在 → 409。"""


class UserExistsError(Exception):
    """用户名已被注册 → 409。"""


class NotOwnerError(Exception):
    """想操作别人的短链 → 403。"""


def _generate_code(length: int = 6) -> str:
    # secrets 比 random 更适合生成不可预测令牌。
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


# ---------- 用户 ----------


def create_user(req: UserCreate) -> User:
    """注册：明文密码在这里被哈希，之后**只存哈希**。"""
    with Session(engine) as session:
        if _find_user(session, req.username) is not None:
            raise UserExistsError(req.username)
        user = User(
            username=req.username,
            hashed_password=hash_password(req.password),  # ← 明文到此为止，绝不落库
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def _find_user(session: Session, username: str) -> User | None:
    return session.exec(select(User).where(User.username == username)).first()


def get_user(username: str) -> User | None:
    with Session(engine) as session:
        return _find_user(session, username)


def get_user_by_credentials(username: str, password: str) -> User | None:
    """登录校验：先按用户名找人，再比对密码哈希。任一不对都返回 None（不透露是哪一步错）。"""
    user = get_user(username)
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ---------- 短链 ----------


def _find_by_code(session: Session, code: str) -> ShortLink | None:
    return session.exec(select(ShortLink).where(ShortLink.code == code)).first()


def create_link(req: ShortenRequest, owner: str) -> ShortLink:
    """创建短链，归属人是当前登录用户。"""
    with Session(engine) as session:
        if req.code is not None:
            if _find_by_code(session, req.code) is not None:
                raise CodeTakenError(req.code)
            code = req.code
        else:
            code = _generate_code()
            attempts = 0
            while _find_by_code(session, code) is not None and attempts < 10:
                code = _generate_code()
                attempts += 1
            if _find_by_code(session, code) is not None:
                raise RuntimeError("短码生成冲突，请重试")

        link = ShortLink(code=code, url=str(req.url), owner=owner)
        session.add(link)
        session.commit()
        session.refresh(link)
        return link


def get_link(code: str) -> ShortLink | None:
    """按短码取一条。**公开**：跳转用，不校验归属。"""
    with Session(engine) as session:
        return _find_by_code(session, code)


def list_links(
    search: str | None = None, sort: str = "created_at", owner: str | None = None
) -> list[ShortLink]:
    """列出短链。传了 owner 就只看这个人的 —— 这就是「登录隔离」。"""
    with Session(engine) as session:
        statement = select(ShortLink)
        if owner is not None:
            statement = statement.where(ShortLink.owner == owner)
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(ShortLink.code.like(pattern), ShortLink.url.like(pattern))
            )
        if sort == "code":
            statement = statement.order_by(ShortLink.code)
        elif sort == "url":
            statement = statement.order_by(ShortLink.url)
        else:
            statement = statement.order_by(ShortLink.created_at.desc())
        return list(session.exec(statement).all())


def delete_link(code: str, owner: str) -> bool:
    """删除自己的短链。

    返回 True = 删成功；False = 短码不存在；抛 NotOwnerError = 存在但不是你的。
    """
    with Session(engine) as session:
        link = _find_by_code(session, code)
        if link is None:
            return False
        if link.owner != owner:
            raise NotOwnerError(code)
        session.delete(link)
        session.commit()
        return True


def record_visit(code: str, user_agent: str | None = None) -> None:
    """记一次访问。跳转是公开的，所以不校验归属；统计写失败也不能挡住跳转。"""
    with Session(engine) as session:
        session.add(Visit(code=code, user_agent=user_agent))
        session.commit()


def get_stats(code: str, owner: str, recent_limit: int = 5) -> LinkStats | None:
    """统计：只能看自己的。不是你的 → 返回 None（对外表现为 404，不暴露「它存在」）。"""
    with Session(engine) as session:
        link = _find_by_code(session, code)
        if link is None or link.owner != owner:
            return None
        clicks = session.exec(
            select(func.count(Visit.id)).where(Visit.code == code)
        ).one()
        recent = list(
            session.exec(
                select(Visit.visited_at)
                .where(Visit.code == code)
                .order_by(Visit.visited_at.desc())
                .limit(recent_limit)
            ).all()
        )
        return LinkStats(
            code=link.code,
            url=link.url,
            clicks=clicks,
            created_at=link.created_at,
            recent_visits=recent,
        )
