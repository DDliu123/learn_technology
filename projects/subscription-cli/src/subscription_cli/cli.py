"""命令行功能实现 —— 第 3 课：argparse 子命令 + 交互式菜单。

两种用法都支持：
    uv run subscription-cli list                 # 子命令，可被脚本调用
    uv run subscription-cli                      # 无参数时进入交互菜单
"""

from rich.console import Console
from rich.table import Table

from subscription_cli import storage
from subscription_cli.bill import annual_cost, format_money, group_by_category, monthly_cost
from subscription_cli.models import Subscription

console = Console()


def render_table(subs: list[Subscription]) -> None:
    """用 rich 画表格 —— 它按字符显示宽度计算，中文不会错位。"""
    table = Table(title="订阅账单", title_justify="left")
    table.add_column("名称", style="bold")
    table.add_column("月费", justify="right")
    table.add_column("分类")
    table.add_column("下次扣费", justify="right")

    for s in sorted(subs, key=lambda x: x.next_billing):
        table.add_row(s.name, format_money(s.price), s.category, s.next_billing)

    console.print(table)


def cmd_list() -> None:
    """列出所有订阅。"""
    subs = storage.load_subscriptions()
    if not subs:
        console.print("[yellow]还没有任何订阅，用 add 加一条吧。[/yellow]")
        return
    render_table(subs)
    console.print(f"月度支出：[bold]{format_money(monthly_cost(subs))}[/bold]")


def cmd_add(name: str, price: float, category: str, next_billing: str) -> None:
    """新增订阅。"""
    sub = Subscription(name, price, category, next_billing)
    storage.add_subscription(sub)
    console.print(f"[green]已添加[/green] {name} {format_money(price)}")


def cmd_remove(name: str) -> None:
    """删除订阅。"""
    _, removed = storage.remove_subscription(name)
    if removed:
        console.print(f"[green]已删除[/green] {name}")
    else:
        console.print(f"[red]没找到[/red] {name}")


def cmd_stats() -> None:
    """支出统计。"""
    subs = storage.load_subscriptions()
    if not subs:
        console.print("[yellow]暂无数据。[/yellow]")
        return

    console.print(f"订阅数量：{len(subs)} 项")
    console.print(f"月度支出：[bold red]{format_money(monthly_cost(subs))}[/bold red]")
    console.print(f"年度支出：[bold red]{format_money(annual_cost(subs))}[/bold red]")

    console.print("\n分类统计：")
    for category, items in sorted(group_by_category(subs).items(), key=lambda kv: -monthly_cost(kv[1])):
        console.print(f"  {category}: {format_money(monthly_cost(items))}（{len(items)} 项）")


MENU = """
[1] 查看账单    [2] 添加订阅    [3] 删除订阅    [4] 支出统计    [0] 退出
"""


def interactive() -> None:
    """交互菜单：while 循环 + input，直到用户选退出。"""
    actions = {"1": cmd_list, "4": cmd_stats}

    while True:
        console.print(MENU)
        choice = input("请选择：").strip()

        if choice == "0":
            console.print("再见 👋")
            break
        elif choice in actions:
            actions[choice]()
        elif choice == "2":
            name = input("名称：").strip()
            price = float(input("月费：").strip())
            category = input("分类：").strip()
            next_billing = input("下次扣费日(YYYY-MM-DD)：").strip()
            cmd_add(name, price, category, next_billing)
        elif choice == "3":
            cmd_remove(input("要删除的名称：").strip())
        else:
            console.print("[red]无效选项，请重新输入。[/red]")
