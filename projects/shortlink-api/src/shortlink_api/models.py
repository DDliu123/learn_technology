"""阶段 5 第 2 课：用 Pydantic 定义「短链」的数据形状。

Pydantic 干两件事：
1. 校验 —— 进来的 JSON 不符合类型/规则，直接拒绝（自动返回 422）。
2. 文档 —— FastAPI 用模型的字段类型自动生成 Swagger 文档和请求示例。

核心概念：请求模型（前端发什么）和响应模型（后端回什么）分开写，
避免把内部字段（如存储时间）泄露给调用方，也方便以后改存储不影响接口契约。
"""
from datetime import datetime, timezone

from pydantic import BaseModel, AnyHttpUrl, field_validator


class ShortenRequest(BaseModel):
    """POST /shorten 的请求体：要缩短的网址，可选自定义短码。"""

    # AnyHttpUrl 是 Pydantic 内置类型：自动校验「是不是合法 URL」，不合法 → 422。
    # 例如 "not-a-url" 会被拒；"https://example.com" 会被规范化成带方案的 URL。
    url: AnyHttpUrl

    # 可选：用户想自己指定短码（如 "myproject"）。不传则服务器随机生成。
    code: str | None = None

    @field_validator("code")
    @classmethod
    def code_must_be_alnum(cls, v: str | None) -> str | None:
        # 自定义校验：短码只能字母+数字，避免路径里出现 / ? # 等非法字符。
        # 抛 ValueError → FastAPI 自动转成 422，并带上这个错误信息。
        if v is not None and not v.isalnum():
            raise ValueError("自定义短码只能含字母和数字")
        return v


class ShortLink(BaseModel):
    """对外返回的短链对象。"""

    code: str
    url: str
    # 创建时间（UTC，ISO 8601 字符串）。存储用，也回给前端展示。
    created_at: str


def now_iso() -> str:
    """统一的当前时间格式，避免各模块各写一遍。"""
    return datetime.now(timezone.utc).isoformat()
