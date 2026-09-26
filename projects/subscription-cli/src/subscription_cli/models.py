"""数据模型 —— 第 2 课：从字典升级到 dataclass。

为什么要有类：
- 字典：sub["price"]  写错键名要等运行到才报错
- 类  ：sub.price     编辑器能自动补全，写错属性立刻标红
"""

from dataclasses import asdict, dataclass


@dataclass
class Subscription:
    """一条订阅记录。"""

    name: str
    price: float          # 月费
    category: str         # 分类：视频 / 音乐 / AI 工具 ...
    next_billing: str     # 下次扣费日，格式 YYYY-MM-DD

    def to_dict(self) -> dict:
        """转回字典 —— JSON 只认字典，存盘前必须转换。"""
        return asdict(self)


# 初始种子数据：数据文件不存在时用它建第一份账单
DEMO_SUBSCRIPTIONS: list[Subscription] = [
    Subscription("Netflix", 68.0, "视频", "2026-10-01"),
    Subscription("Spotify", 58.0, "音乐", "2026-10-05"),
    Subscription("ChatGPT Plus", 145.0, "AI 工具", "2026-10-08"),
    Subscription("Notion", 45.0, "效率工具", "2026-10-12"),
    Subscription("iCloud", 21.0, "存储", "2026-10-20"),
]
