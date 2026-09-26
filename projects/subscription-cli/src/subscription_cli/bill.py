"""订阅账单计算 —— 第 1 课：类型、列表、字典、函数。

知识点对照：
- 类型注解   ：def f(x: int) -> float，写给自己和 AI 看的文档
- 列表推导   ：[表达式 for 元素 in 列表 if 条件]
- f-string   ：f"{变量:,.2f}" 控制小数位与千分位
"""

# 类型别名：让 Money 比 float 更有业务含义
Money = float

# 订阅数据用字典表示：键值对，取值用 sub["name"]
Subscription = dict[str, str | Money]


def monthly_cost(subs: list[Subscription]) -> Money:
    """月支出：所有订阅月费求和。"""
    return sum(sub["price"] for sub in subs)  # type: ignore


def annual_cost(subs: list[Subscription]) -> Money:
    """年支出：复用月支出函数，避免重复逻辑。"""
    return monthly_cost(subs) * 12


def format_money(amount: Money) -> str:
    """金额格式化：¥1,234.00。"""
    return f"¥{amount:,.2f}"


def most_expensive(subs: list[Subscription]) -> Subscription:
    """最贵的一项：max + key 参数是 Python 的惯用写法。"""
    return max(subs, key=lambda sub: sub["price"])  # type: ignore


def group_by_category(subs: list[Subscription]) -> dict[str, list[Subscription]]:
    """按类别分组：字典的好处是查一类数据不用遍历整个列表。"""
    groups: dict[str, list[Subscription]] = {}
    for sub in subs:
        category = sub["category"]  # type: ignore
        groups.setdefault(category, []).append(sub)
    return groups


def print_summary(subs: list[Subscription]) -> None:
    """打印账单摘要。"""
    print("=" * 40)
    print(f"订阅数量：{len(subs)} 项")

    for sub in subs:
        print(f"  {sub['name']:<16} {format_money(sub['price']):>10}  [{sub['category']}]")

    print("-" * 40)
    print(f"月度支出：{format_money(monthly_cost(subs))}")
    print(f"年度支出：{format_money(annual_cost(subs))}")

    top = most_expensive(subs)
    print(f"最贵的一项：{top['name']}（{format_money(top['price'])}）")

    print("-" * 40)
    print("分类统计：")
    for category, items in group_by_category(subs).items():
        print(f"  {category}: {format_money(monthly_cost(items))}（{len(items)} 项）")
    print("=" * 40)


# 模块级演示数据：先用假数据跑通计算，第 2 课再换成从文件读取
DEMO_SUBSCRIPTIONS: list[Subscription] = [
    {"name": "Netflix", "price": 68.0, "category": "视频"},
    {"name": "Spotify", "price": 58.0, "category": "音乐"},
    {"name": "ChatGPT Plus", "price": 145.0, "category": "AI 工具"},
    {"name": "Notion", "price": 45.0, "category": "效率工具"},
    {"name": "iCloud", "price": 21.0, "category": "存储"},
]
