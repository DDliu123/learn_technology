"""订阅账单管家 CLI —— 第 2 课：数据落盘，关掉程序再打开数据还在。"""

from subscription_cli.bill import print_summary
from subscription_cli.storage import DATA_FILE, load_subscriptions


def main() -> None:
    subs = load_subscriptions()          # 读文件；首次运行自动创建
    print_summary(subs)
    print(f"\n数据文件：{DATA_FILE}")


# 直接运行本文件时才执行，被 import 时不执行 —— 保证模块可被复用
if __name__ == "__main__":
    main()
