# 阶段 2 · 第 3 课：CLI 交互与阶段收口

目标：完成可用产品的最后一块 —— 增删改查命令。产出：`cli.py` + argparse 入口。时长约 2 小时。

---

## 1. CLI 的两种形态

| 形态    | 样子                              | 适用            |
| ----- | ------------------------------- | ------------- |
| 子命令   | `subscription-cli add Netflix …` | 可被脚本调用、可自动化测试 |
| 交互菜单  | 输入 `1/2/3/4` 选择                | 给不熟悉命令的人用     |

本课两者都实现：**给了子命令就执行，不给就进菜单**。这也是成熟 CLI 工具（git、docker）的常见设计。

---

## 2. argparse

```python
parser = argparse.ArgumentParser(prog="subscription-cli", description="...")
sub = parser.add_subparsers(dest="command")          # 子命令容器

p_add = sub.add_parser("add", help="新增订阅")
p_add.add_argument("name", help="服务名称")
p_add.add_argument("price", type=float, help="月费")   # type= 自动转类型
p_add.set_defaults(func=lambda args: cmd_add(...))   # 绑定处理函数
```

关键点：

| 写法                        | 作用                                    |
| ------------------------- | ------------------------------------- |
| `type=float`              | 自动把字符串转成 float，格式不对直接报错               |
| `add_subparsers(dest=...)` | 子命令名存到 `args.command`                  |
| `set_defaults(func=...)`   | 把「命令」和「执行」绑在一起，主流程只需 `args.func(args)` |
| `--help`                  | argparse 自动生成，不用自己写说明                 |

`main(argv=None)` 允许传参数列表进来 —— **这是让命令行程序可测试的关键**（测试时传 `["add", "X", "68", ...]`，不用真的跑终端）。

---

## 3. 交互菜单

```python
while True:
    print(菜单)
    choice = input("请选择：").strip()
    if choice == "0":
        break                      # 退出循环
    elif choice in actions:
        actions[choice]()          # 用字典替代 if-else 长链
    else:
        print("无效选项")
```

要点：`input()` 永远返回字符串，转数字要 `float()`/`int()`；字典映射动作比一长串 `elif` 更好维护。

---

## 4. rich：让终端变好看

```python
from rich.console import Console
from rich.table import Table

table = Table(title="订阅账单")
table.add_column("名称", style="bold")
table.add_column("月费", justify="right")
table.add_row("Netflix", "¥88.00")
console.print(table)
console.print("[green]已添加[/green]")     # 颜色标记
```

**rich 顺带解决了第 2 课的中文错位问题** —— 它按字符的实际显示宽度（全角 2 列）计算表格，f-string 的 `{:<10}` 做不到这点。

---

## 5. 数据修改的唯一铁律

```
先 load → 在内存里改 → 整体 save
```

绝不能在多个地方各自 save：A 读的旧数据晚一步写回，会把 B 的新增覆盖掉。

```python
def add_subscription(sub):
    subs = load_subscriptions()      # 1. 读最新
    subs.append(sub)                 # 2. 改内存
    save_subscriptions(subs)         # 3. 整体写回
    return subs
```

---

## 6. 分层的结果

| 文件            | 职责                       |
| ------------- | ------------------------ |
| `models.py`   | 数据模型                     |
| `storage.py`  | 读写 JSON                  |
| `bill.py`     | **纯计算**：不碰输入、不碰打印        |
| `cli.py`      | **展示与交互**：不做计算           |
| `__init__.py` | 命令解析与入口                  |

阶段 3 要把它改成网页版 —— 那时候只需重写展示层，`bill.py` 整个可以复用。**这就是分层的价值**，不是为了好看。

---

## 7. 实跑结果

```bash
uv run subscription-cli list     # 表格 + 月度支出 ¥357.00
uv run subscription-cli add "Claude Pro" 158 "AI 工具" 2026-10-15
uv run subscription-cli stats    # 6 项，月 ¥515.00，年 ¥6,180.00，AI 工具占 ¥303.00
uv run subscription-cli remove "Claude Pro"
uv run subscription-cli --help   # 自动生成用法说明
```

删了不存在的服务会提示「没找到」，不会崩。

---

## 8. 常见坑

| 现象                          | 原因                              |
| --------------------------- | ------------------------------- |
| `SystemExit: 2`             | argparse 参数错误，属正常退出，不是 bug      |
| 中文参数要加引号                    | `add Claude Pro 158 …` 会被当成两个参数 |
| `TypeError: can't compare`   | 排序字段类型不一致，检查有没有混了 str 和 float   |
| 改了代码运行结果没变                  | `uv run` 用的是已安装的包，改代码后重跑即可自动重装 |

---

## 9. 作业

1. 加一个 `due` 子命令：列出 7 天内要扣费的订阅（提示：`datetime.date.today()`、`datetime.strptime(s.next_billing, "%Y-%m-%d")`）。
2. 给 `add` 加一步校验：月费为负数时拒绝并提示。
3. 按阶段 1 定的笔记模板，写下阶段 2 的学习笔记 —— 重点是「AI 哪里写砸了、我怎么改的」。

阶段 2 完成标准：**CLI 能完成增删改查，数据持久保存。** 之后进入阶段 3 —— 前端 JavaScript，把同一个产品做成网页版。
