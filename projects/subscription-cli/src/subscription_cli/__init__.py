"""订阅账单管家 CLI —— 第 3 课：argparse 子命令 + 交互菜单。"""

import argparse

from subscription_cli.cli import cmd_add, cmd_list, cmd_remove, cmd_stats, interactive


def build_parser() -> argparse.ArgumentParser:
    """组装命令行解析器：一个主命令 + 四个子命令。"""
    parser = argparse.ArgumentParser(
        prog="subscription-cli",
        description="订阅账单管家：管理你的付费订阅与月度支出",
    )
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list", help="查看所有订阅")
    p_list.set_defaults(func=lambda args: cmd_list())

    p_add = sub.add_parser("add", help="新增订阅")
    p_add.add_argument("name", help="服务名称")
    p_add.add_argument("price", type=float, help="月费金额")
    p_add.add_argument("category", help="分类，如：视频 / AI 工具")
    p_add.add_argument("next_billing", help="下次扣费日 YYYY-MM-DD")
    p_add.set_defaults(
        func=lambda args: cmd_add(args.name, args.price, args.category, args.next_billing)
    )

    p_remove = sub.add_parser("remove", help="删除订阅")
    p_remove.add_argument("name", help="要删除的服务名称")
    p_remove.set_defaults(func=lambda args: cmd_remove(args.name))

    p_stats = sub.add_parser("stats", help="支出统计")
    p_stats.set_defaults(func=lambda args: cmd_stats())

    return parser


def main(argv: list[str] | None = None) -> None:
    """入口：给了子命令就执行，没给就进交互菜单。"""
    parser = build_parser()
    args = parser.parse_args(argv)

    if getattr(args, "command", None) is None:
        interactive()          # 不带任何参数 → 菜单模式
    else:
        args.func(args)


if __name__ == "__main__":
    main()
