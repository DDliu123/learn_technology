"""订阅账单计算 —— 第 2 课：改用 dataclass，属性访问取代字典取值。

知识点：
- 类型注解写具体类型：list[Subscription] 比 list[dict] 信息量大
- 编辑器能据此自动补全 s.price，写错属性立刻标红
"""

from subscription_cli.models import Subscription

Money = float


def monthly_cost(subs: list[Subscription]) -> Money:
    """月支出：所有订阅月费求和。"""
    return sum(s.price for s in subs)


def annual_cost(subs: list[Subscription]) -> Money:
    """年支出：复用月支出，避免重复逻辑。"""
    return monthly_cost(subs) * 12


def format_money(amount: Money) -> str:
    """金额格式化：¥1,234.00。"""
    return f"¥{amount:,.2f}"


def most_expensive(subs: list[Subscription]) -> Subscription:
    """最贵的一项。"""
    return max(subs, key=lambda s: s.price)


def group_by_category(subs: list[Subscription]) -> dict[str, list[Subscription]]:
    """按类别分组。"""
    groups: dict[str, list[Subscription]] = {}
    for s in subs:
        groups.setdefault(s.category, []).append(s)
    return groups


def sort_by_next_billing(subs: list[Subscription]) -> list[Subscription]:
    """按下次扣费日排序：YYYY-MM-DD 格式的字符串可以直接比大小。"""
    return sorted(subs, key=lambda s: s.next_billing)


def print_summary(subs: list[Subscription]) -> None:
    """打印账单摘要。"""
    print("=" * 54)
    print(f"订阅数量：{len(subs)} 项\n")

    print(f"{'名称':<16}{'月费':>10}  {'分类':<10}{'下次扣费':>12}")
    print("-" * 54)
    for s in sort_by_next_billing(subs):
        print(f"{s.name:<16}{format_money(s.price):>10}  {s.category:<10}{s.next_billing:>12}")

    print("-" * 54)
    print(f"月度支出：{format_money(monthly_cost(subs))}")
    print(f"年度支出：{format_money(annual_cost(subs))}")

    top = most_expensive(subs)
    print(f"最贵的一项：{top.name}（{format_money(top.price)}）")

    print("-" * 54)
    print("分类统计：")
    for category, items in group_by_category(subs).items():
        print(f"  {category}: {format_money(monthly_cost(items))}（{len(items)} 项）")
    print("=" * 54)
