"""阶段 6 第 1 课：用 SQLModel 定义数据模型。

SQLModel 把 Pydantic 和 SQLAlchemy 合二为一：
- 一个类**既是** Pydantic 模型（负责 JSON 校验/序列化），**又是** SQLAlchemy 表（负责落库）。
- 请求模型（ShortenRequest）只做校验 → 普通 SQLModel，不加 `table=True`。
- 表模型（ShortLink）加 `table=True` → 既能存进数据库，也能直接当接口返回值。

对比阶段 5：以前 `ShortLink` 只是个 Pydantic 类，存在内存 dict 里；现在它成了数据库表，
多了一个数据库主键 `id`，`created_at` 用 `default_factory` 在入库时自动填。
"""
from datetime import datetime, timezone
from typing import Optional

from pydantic import AnyHttpUrl, field_validator
from sqlmodel import SQLModel, Field


class ShortenRequest(SQLModel):
    """POST /shorten 的请求体。只做校验，不是数据库表。"""

    # AnyHttpUrl 内置类型：自动校验「是不是合法 URL」，不合法 → 422；合法会规范成带方案。
    url: AnyHttpUrl
    # 可选自定义短码
    code: Optional[str] = None

    @field_validator("code")
    @classmethod
    def code_must_be_alnum(cls, v: Optional[str]) -> Optional[str]:
        # 自定义校验：短码只能字母+数字，避免路径里出现 / ? # 等非法字符。
        if v is not None and not v.isalnum():
            raise ValueError("自定义短码只能含字母和数字")
        return v


class ShortLink(SQLModel, table=True):
    """短链表。table=True → 同时是数据库表和接口响应模型。"""

    __tablename__ = "short_link"

    # 数据库主键。Optional + default=None：插入时由数据库自增生成。
    id: Optional[int] = Field(default=None, primary_key=True)
    # 短码：建唯一索引，既是查询条件也是「不能重复」的约束（409 的来源）。
    code: str = Field(index=True, unique=True)
    # 原网址，存字符串
    url: str
    # 创建时间（UTC，ISO 8601）。default_factory：插入时自动填，不用调用方传。
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Visit(SQLModel, table=True):
    """访问记录表：每次有人点短链，就写一条。

    「统计」和「短链」分开成两张表，而不是在 short_link 上加一个 clicks 字段：
    日志型数据要保留每一次的时间，才能画出趋势；只有一个总数就丢掉了全部细节。
    """

    __tablename__ = "visit"

    id: Optional[int] = Field(default=None, primary_key=True)
    # 被访问的短码。加索引：统计查询基本都按 code 过滤，没索引大表会很慢。
    code: str = Field(index=True)
    visited_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    # 浏览器标识，便于后面做「设备/来源」这类简单分析
    user_agent: Optional[str] = None


class LinkStats(SQLModel):
    """GET /stats/{code} 的响应模型。只做输出，不是表。"""

    code: str
    url: str
    clicks: int
    created_at: str
    # 最近几次访问时间（倒序，最多 5 条）
    recent_visits: list[str] = []
