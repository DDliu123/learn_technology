# subscription-cli

CLI 版订阅账单管家 —— 阶段 2 的练习项目。管理付费订阅，统计月度/年度支出。

## 运行

```bash
cd projects/subscription-cli
uv sync                        # 首次：按 uv.lock 装依赖

uv run subscription-cli list   # 查看账单
uv run subscription-cli add "Netflix" 68 "视频" 2026-10-01
uv run subscription-cli remove "Netflix"
uv run subscription-cli stats  # 支出统计
uv run subscription-cli        # 不带参数 → 交互菜单
```

## 结构

| 文件           | 职责                                |
| ------------ | --------------------------------- |
| `models.py`  | `Subscription` 数据模型（dataclass）    |
| `storage.py` | JSON 读写：load / save / add / remove |
| `bill.py`    | 纯计算：月度、年度、分组、排序                   |
| `cli.py`     | 展示与交互：rich 表格、各项命令实现              |
| `__init__.py` | argparse 命令解析与入口                  |

分层原则：**计算不碰输入输出，展示不做计算**。这样换网页版时只需重写 `cli.py`，`bill.py` 可以原样复用。

## 数据

存于 `data/subscriptions.json`（首次运行自动创建）。该文件已在 `.gitignore` 中，不入库。
