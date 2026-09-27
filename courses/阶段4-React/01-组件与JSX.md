# 阶段 4 · 第 1 课：React 心智模型、组件与 JSX

> 项目：`projects/subscription-react/`（Vite + React 19）
> 本课产出：把阶段 3 的原生 JS 版重写成组件版（静态渲染，暂无交互）

---

## 1. React 到底解决了什么

阶段 3 你手写的代码，本质在做两件事：

1. 把数据变成 DOM（`createRow` / `renderTable`）
2. 数据变了就把 DOM 重画一遍（`commit → render`）

React 把第 2 件自动化了。核心公式只有一行：

```
UI = f(state)
```

你只负责描述「state 是这个值时，界面长这样」，**剩下的时候数据一变，React 自己算差异、改 DOM**。你不再需要：

```js
tbody.replaceChildren(...);   // ❌ 不用再手动清空重画
```

**对照表（这一列是这一阶段的核心记忆点）**

| 阶段 3 原生 JS | 阶段 4 React |
|---|---|
| `document.createElement("tr")` | `<tr>...</tr>`（JSX） |
| `node.textContent = x` | `<td>{x}</td>` |
| `render()` 手动重画 | 改 state，自动重画 |
| `parent.appendChild(child)` | 组件嵌套 `<BillTable subs={subs} />` |
| 事件委托（父容器监听） | 直接写 `onClick={handler}` |
| 手写 `commit()` 统一出口 | `useState` + set 函数 |

---

## 2. Vite 项目与命令

```bash
npm create vite@latest subscription-react -- --template react   # 建项目
npm install      # 装依赖（生成 node_modules，不入库）
npm run dev      # 开发服务器 http://localhost:5173，改代码自动热更新
npm run build    # 产出 dist/（压缩后的静态文件，才能上线）
npm run preview  # 本地预览 dist/
```

| 目录/文件 | 作用 |
|---|---|
| `index.html` | 唯一入口 HTML，只有一个 `<div id="root">` |
| `src/main.jsx` | 挂载点：`createRoot(#root).render(<App />)` |
| `src/App.jsx` | 根组件 |
| `src/components/` | 子组件，一个文件一个组件 |
| `src/index.css` | 全局样式 |
| `dist/` | 构建产物，**不入库**（已在 .gitignore） |

**开发模式 vs 生产**：`npm run dev` 跑的是源码，改完立刻看到效果；线上跑的是 `npm run build` 出来的 `dist/`。这是前端和 Python 最大的不同 —— **多了一道构建**。

---

## 3. JSX 三条规则

**① `class` 要写 `className`**

```jsx
<div className="stat">      {/* ✅ */}
<div class="stat">           {/* ❌ class 是 JS 关键字 */}
```

**② `{}` 里放 JS 表达式**

```jsx
<StatCard value={formatMoney(monthlyCost(subs))} />
<StatCard value={`${top.name} · ${formatMoney(top.price)}`} />
```

`{}` 里可以是变量、函数调用、模板字符串 —— 但**不能是 if 语句**（用三元或 `&&`）。

**③ 列表渲染必须带 key**

```jsx
{subs.map((sub) => <BillRow key={sub.id} sub={sub} />)}
```

React 靠 key 判断"哪一行是同一个"。**别用数组下标当 key** —— 排序或删除后下标会错位，React 会把状态（比如输入框里的内容）安错行。这和阶段 3 用 id 而不是下标删除是同一个道理。

---

## 4. 组件与 props

```jsx
export default function StatCard({ label, value, accent = false }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      <p className={accent ? "stat-value accent" : "stat-value"}>{value}</p>
    </div>
  );
}
```

| 规则 | 说明 |
|---|---|
| 组件就是**返回 JSX 的函数** | 函数名**必须大写开头**，小写会被当成 HTML 标签 |
| props 是**只读**的 | 子组件不能改 props，要改得通知父组件（第 2 课） |
| 数据**单向流动** | 父 → 子。这是 React 可预测的根本原因 |
| 拆分标准 | 一段 JSX 被复用两次，或长到影响阅读，就拆 |

条件渲染：组件里可以直接 `if (subs.length === 0) return <p>空</p>;`（提前返回比三元清晰）。

---

## 5. 本课文件

| 文件 | 作用 |
|---|---|
| `src/data.js` | 种子数据（第 3 课换成 localStorage） |
| `src/money.js` | **纯计算函数，与阶段 2 的 bill.py、阶段 3 的 app.js 完全一致** |
| `src/components/SiteHeader.jsx` | 页头 |
| `src/components/StatCard.jsx` | 概览卡（props: label / value / accent） |
| `src/components/BillTable.jsx` | 表格 + 内部的 `BillRow` |
| `src/App.jsx` | 组合以上组件，计算后以 props 下发 |
| `src/index.css` | 沿用阶段 3 的配色与布局（视觉一致，方便对比两版） |

**注意 `money.js`**：它是从阶段 2 一路复用到现在的第三版。计算逻辑与框架无关 —— 这就是分层的好处，你已经在享受了。阶段 3 强调的"渲染层和计算层分开"，到 React 这里直接兑现。

---

## 6. 验证结果

```
npm run lint    → 0 warnings, 0 errors（oxlint，104 条规则）
npm run build   → ✓ 21 modules，dist/assets/index-*.js 222 KB（gzip 69.7 KB）
npm run dev     → VITE v8.3.1 ready，HTTP 200
```

产物里能 grep 到 `ChatGPT Plus`，说明数据已正确打包。

---

## 7. 本机踩坑（npm 缓存目录）

`npm view` 报 `Log files were not written due to an error writing to the directory: C:\SoftWare\nodejs\node_cache` —— 因为 Node 装在 `C:\SoftWare`，当前用户对该目录无写权限。

```bash
npm config set cache "C:/Users/wise/.npm-cache"    # 建议执行一次，改到用户目录
```

我在这个会话里用环境变量 `npm_config_cache` 绕过了，**你自己的终端建议执行上面那行全局设置**，否则以后每个 npm 命令都可能带一堆噪音报错。

---

## 8. 作业

1. 跑 `npm run dev`，在 `data.js` 里改一条价格，看浏览器是否**不刷新就自动更新**（HMR 热更新）。
2. 新增一个组件 `CategoryStat.jsx`：按分类统计月费并列出（提示：`Object.entries()` 分组，或直接 `filter` 出每个分类）。
3. 给 `BillTable` 加空状态之外的第二道判断：数据超过 6 条时在表格下方显示一句「订阅有点多了，考虑清理」。
4. **对照思考**（写进笔记）：阶段 3 手写了 `commit → render`，React 里对应哪几行？哪些代码被 React 吃掉了？

> 下一课：`useState` + 事件处理，把增删改查和排序做回来 —— 届时会清楚看到"手动重画"这一步真的消失了。
