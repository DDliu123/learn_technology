# 阶段 2 · 第 2 课：文件、JSON 与数据持久化

目标：让程序关掉再打开数据还在。产出：`models.py` + `storage.py`。时长约 2 小时。

---

## 1. 为什么需要持久化

第 1 课的数据写死在代码里 —— 改一个价格要改源码。真实程序的数据必须存在**代码之外**。

```
代码（不变的逻辑）  ←→  数据文件（变化的内容）
```

---

## 2. pathlib：路径处理

```python
from pathlib import Path

DATA_DIR = Path("data")                    # 相对当前工作目录
DATA_FILE = DATA_DIR / "subscriptions.json"  # 用 / 拼接，不用管 Windows 反斜杠

DATA_FILE.exists()                          # 判断存在
DATA_DIR.mkdir(parents=True, exist_ok=True)  # 建目录，已存在不报错
```

别再拼字符串路径（`"data" + "\\" + "x.json"`），跨平台必出问题。

---

## 3. 文件读写

```python
with open(path, "w", encoding="utf-8") as f:   # w 覆盖写，a 追加，r 读
    f.write(...)
```

| 要点                     | 说明                                  |
| ---------------------- | ----------------------------------- |
| 必须用 `with`             | 代码块结束自动关闭文件，忘记 `close()` 也不会泄漏     |
| **必须写 `encoding="utf-8"`** | Windows 默认 GBK，不写就中文乱码          |
| 模式                     | `r` 读 / `w` 覆盖写 / `a` 追加 / `x` 新建 |

---

## 4. JSON：最通用的数据格式

```python
json.dump(data, f, ensure_ascii=False, indent=2)   # 写
data = json.load(f)                                 # 读
```

| Python   | JSON      |
| -------- | --------- |
| `dict`   | 对象 `{}`   |
| `list`   | 数组 `[]`   |
| `str`    | 字符串       |
| `int/float` | 数字     |
| `bool`   | `true/false` |
| `None`   | `null`    |

两个参数必加：`ensure_ascii=False`（中文原样写入，否则变成 `\u89c6`）、`indent=2`（文件可读、可 diff）。

JSON **不能存自定义类**，所以存盘前要用 `asdict()` 转回字典，读出来再用 `Subscription(**item)` 还原。

---

## 5. 从字典升级到 dataclass

```python
@dataclass
class Subscription:
    name: str
    price: float
    category: str
    next_billing: str
```

| 对比         | 字典              | dataclass     |
| ---------- | --------------- | ------------- |
| 取值         | `sub["price"]`  | `sub.price`   |
| 写错时        | 运行到才报 KeyError  | 编辑器立刻标红       |
| 自动补全       | 无               | 有             |
| 存 JSON     | 直接用             | 先 `asdict()`  |

升级后 `bill.py` 全部从 `s["price"]` 改成 `s.price` —— 这就是类型注解的价值：改数据结构时，所有要改的地方都能被静态检查揪出来。

---

## 6. 异常处理

```python
try:
    with DATA_FILE.open(encoding="utf-8") as f:
        raw = json.load(f)
except json.JSONDecodeError:
    print("文件损坏，改用种子数据")
```

原则：**只捕获你知道怎么处理的异常**，别写 `except Exception: pass`（会把真实 bug 一起吞掉）。

本课的降级策略：文件不存在 → 用种子数据建一份；文件损坏 → 提示并返回种子数据，**不覆盖原文件**（留给用户抢救的机会）。

---

## 7. `if __name__ == "__main__"`

```python
if __name__ == "__main__":
    main()
```

| 运行方式                        | `__name__` 的值          | main() 是否执行 |
| --------------------------- | ---------------------- | ----------- |
| `python xx.py`              | `"__main__"`           | ✅ 执行        |
| `from xx import main`        | 模块名 `"subscription_cli"` | ❌ 不执行       |

作用：一个文件既能当脚本运行，又能被别的模块安全地 import。

---

## 8. 本次改动

| 文件                   | 内容                                       |
| -------------------- | ---------------------------------------- |
| `models.py`（新增）       | `Subscription` dataclass + 种子数据           |
| `storage.py`（新增）      | `load_subscriptions` / `save_subscriptions` |
| `bill.py`（改）          | 全部改为属性访问 `s.price`，新增按扣费日排序              |
| `__init__.py`（改）      | 读文件 → 打印摘要 → 显示数据文件路径                    |
| `.gitignore`（新增）      | `data/` 不入库（账单是隐私数据）                     |

验证结果：

- 首次运行自动生成 `data/subscriptions.json`
- 改 JSON 里 Netflix 价格为 88 → 重跑月支出从 ¥337.00 变 ¥357.00 ✅
- 故意把 JSON 写坏 → 打印警告并降级到种子数据，程序不崩 ✅

---

## 9. 踩坑：中文对齐不齐

`f"{s.category:<10}"` 按**字符数**对齐，而中文字符在终端占 2 列宽，所以含中文的列会看起来参差：

```
AI 工具       2026-10-08     ← 比纯中文行短，视觉错位
效率工具        2026-10-12
```

三种解法：用 `wcwidth` 库按显示宽度算、改用制表符 `\t`、或接受不完美。CLI 工具里这是常见妥协，第 3 课用 `rich` 库可彻底解决。

---

## 10. 作业

1. 手动在 `data/subscriptions.json` 里加一条订阅，重跑确认出现在列表里。
2. 给 `storage.py` 加 `add_subscription(sub)`：读 → append → 存（注意先读再写，别覆盖）。
3. 把 JSON 改成非法格式跑一次，确认不崩；再改回来。

下一课：完成 CLI 交互（增删改查菜单 + 命令行参数），阶段 2 收口。
