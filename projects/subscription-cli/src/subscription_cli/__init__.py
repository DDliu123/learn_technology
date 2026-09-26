"""订阅账单管家 CLI —— 第 1 课版本：跑通计算逻辑。"""

from subscription_cli.bill import DEMO_SUBSCRIPTIONS, print_summary


def main() -> None:
    print_summary(DEMO_SUBSCRIPTIONS)
