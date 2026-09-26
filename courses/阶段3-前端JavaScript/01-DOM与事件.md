# 阶段 3 · 第 1 课：JavaScript 语法对照 + DOM 渲染与事件

> 项目：`projects/subscription-web/`（网页版订阅账单管家）
> 本课产出：能渲染出账单表格和概览卡片、带两个排序按钮的静态页面

---

## 1. 最大的思维转变

| | CLI（阶段 2） | 网页（阶段 3） |
|---|---|---|
| 执行方式 | 从头跑到尾，跑完进程结束 | 脚本加载后一直驻留，**等用户来打断** |
| 输出 | `print()` 到终端 | 修改 DOM 节点 |
| 输入 | `input()` / 命令行参数 | 点击、输入等**事件** |
| 状态 | 跑完就没了，要存文件 | 活在内存里，刷新页面就没了（第 2 课解决） |

**一句话**：Python 程序是一条**直线**，网页是一个**事件循环**。别用写 CLI 的思路写前端。

---

## 2. JS 语法对照（你已会 Python）

| Python | JavaScript | 备注 |
|---|---|---|
| `def f(x):` | `function f(x) {}` 或 `const f = (x) => {}` | 箭头函数是现在的主流写法 |
| 靠缩进分块 | 靠 `{}` 分块 | 缩进只为好看，错了不影响运行 |
| `None` | `null` / `undefined` | 没有值 vs 从未赋值 |
| 没有常量 | `const` / `let` | **默认用 const**，需要重新赋值才用 let，别用 var |
| f-string `f"{a}{b}"` | 模板字符串 `` `${a}${b}` `` | **反引号**，单引号里写 `${}` 不生效 |
| `[x*2 for x in l]` | `l.map((x) => x*2)` | 映射 |
| `[x for x in l if x>0]` | `l.filter((x) => x>0)` | 过滤 |
| `sum(l)` | `l.reduce((a,b)=>a+b, 0)` | 归约，**必须给初值 0** |
| `f"{v:,.2f}"` | `v.toLocaleString("zh-CN",{minimumFractionDigits:2})` | 数字格式化用这套 |
| `list.sort()` 原地 | `l.sort()` 也是原地 ⚠️ | 想要新数组：`[...l].sort(...)` |
| `print()` | `console.log()` | 输出到浏览器控制台（F12） |
| `# 注释` | `// 注释` | 文档注释用 `/** */` |

**只需先记住一条**：`=>` 就是 Python lambda 的升级版，一个参数时括号可省：`x => x * 2`。

---

## 3. DOM 四件事

浏览器把 HTML 变成一棵树（DOM），JS 就是在改这棵树。

| 动作 | API | 本课用例 |
|---|---|---|
| 查 | `document.getElementById(id)` / `querySelector(css选择器)` | 拿到 `bill-body` 容器 |
| 建 | `document.createElement("tr")` | 创建行和单元格 |
| 改 | `.textContent` / `.className` / `.classList.add()` | 填文字、加类名 |
| 插 | `parent.appendChild(child)` / `parent.replaceChildren(...)` | 把行塞进表格 |

`replaceChildren(...)`:一次性清空旧内容并塞入新节点 —— 比分两步（`innerHTML=""` 再循环 append）可靠且快。

---

## 4. 两条必守的规则

**① 不用 innerHTML 拼内容，用 textContent**

```js
td.textContent = userInput;   // ✅ 当纯文本处理，写什么都只是文字
td.innerHTML = userInput;     // ❌ 会被当成 HTML 解析，用户输 <script> 就能执行
```

这就是 XSS 攻击的入口。前端渲染用户数据的第一原则是：**默认不信任何输入**。用 `createElement + textContent` 天生的免疫。

**② 所有 DOM 操作必须等 DOM 就绪**

```html
<script src="app.js" defer></script>
```

`defer`：HTML 解析完才执行脚本。少了它，JS 里 `getElementById` 会返回 `null`（脚本在 `<head>` 里时元素还没生成）。

---

## 5. 本课踩到的坑

**`sort()` 是原地排序**，会直接改掉原数组：

```js
subs.sort((a, b) => b.price - a.price);   // ❌ subs 本身顺序变了
[...subs].sort((a, b) => b.price - a.price); // ✅ 先复制再排
```

Python 有 `sorted()` 返回新列表的习惯；JS 只有原地版，**复制靠展开符 `[...]`**。这个 bug 很隐蔽，因为它第一次运行总是对的。

**数字/日期排序**：金额用 `a - b`（数值相减）；日期字符串用 `a.localeCompare(b)`，别用一个减另一个（`NaN`）。

---

## 6. 本课文件

| 文件 | 内容 |
|---|---|
| `index.html` | 结构：页头 + 空的 `#stats` 容器 + 表格骨架 + `<script defer>` |
| `style.css` | 概览卡 Grid、按钮、表格数字列右对齐（`tabular-nums` 让金额上下对齐） |
| `app.js` | 四段：数据 → 计算 → 渲染 → 事件 |

**分层与 Python 版一致**：计算函数不碰 DOM、不知道什么叫表格。阶段 4 换 React 时，这一段能整个复用。

核心函数只有一句：

```js
function refresh(subs) {  // 数据变了 → 重画
  renderStats(subs);
  renderTable(subs);
}
```

React 的"数据驱动视图"就是把这个手动调用自动化而已。先手写一遍，以后学框架不会觉得魔法。

---

## 7. 验证方式（不用浏览器也能测）

Node 是**浏览器之外的 JS 运行时**，可以用它跑纯逻辑测试：`scratch/web-check/check.js` 给 app.js 喂了一套假的 `document`，验证了 5 组计算 + 渲染 + HTML/JS 的 id 一致性。结果与 CLI 版逐项吻合：

```
月度：¥337.00   年度：¥4,044.00   最贵：ChatGPT Plus
```

> 顺带踩到的一个 Node 坑：`vm` 里创建的数组原型属于另一个 realm，`deepStrictEqual` 会因原型不同而失败，改用 `join(",")` 比较值。

---

## 8. 作业

1. 在 `SUBSCRIPTIONS` 里删掉两项、加一项你真正在付的订阅，刷新页面看概览和表格是否同步变化。
2. 加一个 `.stat` 卡片：显示「平均每项的月费」（`monthlyCost / subs.length`，保留两位）。
3. 给表格加一列「年费」（`price * 12`），注意金额列都要加 `num` 类（右对齐 + 等宽数字）。
4. **进阶**：给"按月费排序"按钮加"再点一次反向排序"的效果（用一个变量记住当前方向）。

> 疑问留给第 2 课：现在刷新页面，数据会回到初始状态 —— 因为数据写死在代码里。第 2 课用 localStorage 把它变成真正的产品。
