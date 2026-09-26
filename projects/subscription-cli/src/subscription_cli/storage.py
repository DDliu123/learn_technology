"""数据读写 —— 第 2 课：pathlib、JSON、异常处理。

三个必须记住的点：
1. open() 一律用 with，自动关闭文件
2. Windows 上必须写 encoding="utf-8"，否则中文乱码
3. json.dump 加 ensure_ascii=False，否则中文变成 \\uXXXX
"""

import json
from pathlib import Path

from subscription_cli.models import DEMO_SUBSCRIPTIONS, Subscription

# Path 用 / 拼接路径，跨平台不用管斜杠方向
DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "subscriptions.json"


def load_subscriptions() -> list[Subscription]:
    """读取订阅数据。文件不存在或损坏时，返回种子数据。"""
    if not DATA_FILE.exists():
        # 第一次运行：用种子数据建一份文件，保证程序总能跑下去
        save_subscriptions(DEMO_SUBSCRIPTIONS)
        return DEMO_SUBSCRIPTIONS

    try:
        # with 会在代码块结束后自动关闭文件，忘记 close 也不会泄漏
        with DATA_FILE.open(encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️ {DATA_FILE} 内容已损坏，改用种子数据（原文件未覆盖）")
        return DEMO_SUBSCRIPTIONS

    # 字典 → dataclass：**解包
    return [Subscription(**item) for item in raw]


# ------------------------------------------------------------------
# 增删改：所有修改都要「先读 → 改内存 → 整体写回」
# 千万不要在别的模块里各自 save，会互相覆盖
# ------------------------------------------------------------------


def add_subscription(sub: Subscription) -> list[Subscription]:
    """新增一条订阅，返回更新后的完整列表。"""
    subs = load_subscriptions()
    subs.append(sub)
    save_subscriptions(subs)
    return subs


def remove_subscription(name: str) -> tuple[list[Subscription], bool]:
    """按名称删除，返回 (更新后的列表, 是否删除成功)。"""
    subs = load_subscriptions()
    remaining = [s for s in subs if s.name != name]
    removed = len(remaining) != len(subs)

    if removed:
        save_subscriptions(remaining)
    return remaining, removed


def save_subscriptions(subs: list[Subscription]) -> None:
    """保存订阅数据。"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)   # 目录不存在就建，已存在不报错
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(
            [s.to_dict() for s in subs],
            f,
            ensure_ascii=False,   # 中文原样写入，不转义
            indent=2,             # 缩进，文件可读可 diff
        )
