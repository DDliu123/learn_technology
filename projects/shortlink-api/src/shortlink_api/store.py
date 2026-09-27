"""阶段 6 第 1 课：存储层从「内存 dict」换成「SQLite（SQLModel Session）」。

关键变化：
- 数据不再存在进程内存，而在 shortlink.db 文件里；服务重启短链还在。
- 每个操作开一个 Session（会话 = 一次数据库事务），用完 `with` 自动关、自动提交/回滚。
- 查「按短码」用 select + where（code 是唯一索引列），不是按主键。

分层价值再次体现：app.py 的调用签名（create_link / get_link / list_links / delete_link）
完全没变，只改了内部实现。阶段 5 的路由一行都不用动。
"""
import secrets
import string

from sqlmodel import Session, func, or_, select

from .database import engine
from .models import LinkStats, ShortLink, ShortenRequest, Visit

# 短码字符集：大小写字母 + 数字，共 62 个，足够短且 URL 安全。
ALPHABET = string.ascii_letters + string.digits

# 自定义短码已存在时抛出，由 app.py 转成 409。
class CodeTakenError(Exception):
    pass


def _generate_code(length: int = 6) -> str:
    # secrets 比 random 更适合生成不可预测令牌。
    return "".join(secrets.choice(ALPHABET) for _ in range(length))


def _find_by_code(session: Session, code: str) -> ShortLink | None:
    """按短码查一条（code 是唯一索引列）。返回对象或 None。"""
    return session.exec(select(ShortLink).where(ShortLink.code == code)).first()


def create_link(req: ShortenRequest) -> ShortLink:
    with Session(engine) as session:
        if req.code is not None:
            # 用户指定短码：已占用 → 报错，不悄悄覆盖。
            if _find_by_code(session, req.code) is not None:
                raise CodeTakenError(req.code)
            code = req.code
        else:
            # 随机生成 6 位；极小概率撞车，重抽几次。
            code = _generate_code()
            attempts = 0
            while _find_by_code(session, code) is not None and attempts < 10:
                code = _generate_code()
                attempts += 1
            if _find_by_code(session, code) is not None:
                raise RuntimeError("短码生成冲突，请重试")

        # 不传 created_at：靠模型里的 default_factory 在入库时自动填。
        link = ShortLink(code=code, url=str(req.url))
        session.add(link)
        session.commit()
        session.refresh(link)  # 把数据库生成的主键 id、默认值 created_at 回填到对象
        return link


def get_link(code: str) -> ShortLink | None:
    with Session(engine) as session:
        return _find_by_code(session, code)


def list_links(
    search: str | None = None, sort: str = "created_at"
) -> list[ShortLink]:
    """列出短链，支持模糊搜索与排序。

    SQLModel 的查询是**逐步拼装**的：select → .where → .order_by，
    每个方法都返回新的语句对象，最后 exec 才真正发到数据库。
    对应 SQL：
        SELECT * FROM short_link
        WHERE code LIKE '%x%' OR url LIKE '%x%'
        ORDER BY created_at
    """
    with Session(engine) as session:
        statement = select(ShortLink)

        # WHERE：在短码或原网址里模糊匹配（SQL 的 LIKE）
        if search:
            pattern = f"%{search}%"
            statement = statement.where(
                or_(ShortLink.code.like(pattern), ShortLink.url.like(pattern))
            )

        # ORDER BY：按字段排序
        if sort == "code":
            statement = statement.order_by(ShortLink.code)
        elif sort == "url":
            statement = statement.order_by(ShortLink.url)
        else:  # 默认按创建时间倒序（最新的在前）
            statement = statement.order_by(ShortLink.created_at.desc())

        return list(session.exec(statement).all())


def delete_link(code: str) -> bool:
    with Session(engine) as session:
        link = _find_by_code(session, code)
        if link is None:
            return False
        session.delete(link)
        session.commit()
        return True


def record_visit(code: str, user_agent: str | None = None) -> None:
    """记一次访问。跳转前调用一次即可。

    这里单独提交一条，和「查短链」不是一个事务——
    即使统计写失败，也不该影响用户正常跳转（取舍：统计宁可少一条，不能挡住跳转）。
    """
    with Session(engine) as session:
        session.add(Visit(code=code, user_agent=user_agent))
        session.commit()


def get_stats(code: str, recent_limit: int = 5) -> LinkStats | None:
    """统计某条短链的点击情况。短链不存在返回 None（调用方转 404）。"""
    with Session(engine) as session:
        link = _find_by_code(session, code)
        if link is None:
            return None

        # 聚合查询：SELECT count(id) FROM visit WHERE code = ?
        # 用数据库的 COUNT 而不是把所有记录取出来数 —— 数据量大时差别巨大。
        clicks = session.exec(
            select(func.count(Visit.id)).where(Visit.code == code)
        ).one()

        # 最近几次访问时间
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
