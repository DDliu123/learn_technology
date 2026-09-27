# 阶段 4 · 第 3 课：useEffect 与 localStorage 持久化 + 上线

> 项目：`projects/subscription-react/`
> 本课产出：刷新数据不丢（useEffect + localStorage）+ Tailwind 接入 + 构建部署到 Pages 子站

---

## 1. useEffect：state 变了就"顺便"做点事

```jsx
useEffect(() => {
  saveSubscriptions(subs);
}, [subs]);   // 依赖数组：只有 subs 变化才执行
```

| 项 | 说明 |
|---|---|
| 第一个参数 | 副作用函数（读写文件、网络、订阅 localStorage 都算"副作用"，不是渲染） |
| 第二个参数 | **依赖数组**。空 `[]` = 只在挂载时跑一次；`[subs]` = subs 变就跑；不写 = 每次渲染都跑 |
| 返回值 | 可选的清理函数（定时器、监听器用完要_unregister） |

**为什么用 useEffect 而不是在 `setSubs` 里直接 save**：`setSubs` 只是"申请更新"，那一刻 `subs` 还是旧值。useEffect 等 DOM 更新后、拿到最新 `subs` 再存，时机对。

**初始化读取**：放在 `useState` 的惰性初值里，而不是 useEffect —— 首屏直接是正确数据，不用先空再闪一下：

```jsx
useState(() => loadSubscriptions() ?? structuredClone(SUBSCRIPTIONS));
```

---

## 2. localStorage 三件套（与阶段 3 同源）

| 规则 | 写法 |
|---|---|
| 只存字符串 | `JSON.stringify(subs)` |
| 读要解析 | `JSON.parse(raw)` |
| 损坏要兜底 | `try/catch` 返回 `null`，App 用种子数据接住 |

`storage.js` 的读函数返回 `null` 表示"没数据 / 数据坏了"。App 用 `??` 兜底 —— 这正是阶段 3 网页版的同一套防御，只是 key 不同（`subscription-react/subs`），避免两个版本互相覆盖。

**SSR 渲染测试里没有 localStorage**：`scratch/react-check/storage.test.mjs` 自己造一个内存版挂到 `globalThis.localStorage` 再测。否则 Node 里 `localStorage.getItem` 直接抛 `ReferenceError`。

---

## 3. Tailwind v4 接入

装：`npm install -D tailwindcss @tailwindcss/vite`（本机 npm 代理慢，换 npmmirror 源才装上）

| 改动 | 文件 |
|---|---|
| 插件加入 `plugins: [react(), tailwindcss()]` | `vite.config.js` |
| 顶部一行 `@import "tailwindcss";` | `src/index.css` |
| JSX 里直接写工具类 | `App.jsx` 的 `.stats` 改成 `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4` |

**迁移策略**：不一次性重写全部 CSS。挑一个元素（概览卡网格）切到 Tailwind 工具类，其余保留原 `index.css`。这样既能看到"class 里写样式"的写法，又不会把已经调好的界面搞崩。

Tailwind 的 `sm:` / `lg:` 是断点前缀，对应媒体查询；`grid-cols-4` 在 ≥1024px 生效，窄屏自动降列 —— 比阶段 1 手写 `@media` 少写很多。

---

## 4. 部署到 Pages 子站

Pages 一个仓库只给**一个**站点源（根目录或 `/docs`）。教程站已经占了 `/docs` 根，React 应用只能做子目录。

```js
// vite.config.js
base: isProd ? "/learn_technology/subscription-react/" : "/",   // 线上子路径，否则 JS/CSS 404
build.outDir: isProd ? "../../docs/subscription-react" : "dist", // 直接构建到发布目录
```

`base` 必须和线上路径一致 —— 这是 Vite 上线最多的坑，路径不对页面白屏、控制台一堆 404。

构建即上线：`npm run build` → push → Pages 自动构建。

实测：<https://ddliu123.github.io/learn_technology/subscription-react/> 返回 200，JS/CSS 资源 200。

---

## 5. 本机踩坑

| 现象 | 解法 |
|---|---|
| `npm install tailwindcss` 300 秒超时 | 代理对 npm 官方源慢；`--registry=https://registry.npmmirror.com` 1 分钟装完 |
| `outDir` 在 root 外时 Vite 默认不清理 | 显式 `emptyOutDir: true`（只清该子目录） |
| SSR 测试 `localStorage is not defined` | Node 里 `globalThis.localStorage = 内存版` |
| `NODE_ENV` 判断生产 | `vite build` 会自动设为 `production`，无需手传 |

---

## 6. 验证结果

```
npm run lint            → 0 warnings, 0 errors
npm run build           → 23 modules → docs/subscription-react/（CSS 9.75KB / JS 225KB gzip 70.8KB）
money.test.mjs          ✅ 337 / 4044 / 排序不污染 / 空数组 0
storage.test.mjs        ✅ 空→null / 往返一致 / 损坏JSON→null / 非数组→null
render.test.mjs         ✅ 全量渲染 / 数值正确 / 默认排序 / 表单 / 空列表兜底
Pages                   → subscription-react/ 200，JS+CSS 200
```

---

## 7. 作业

1. 跑 `npm run dev`，加一条订阅，刷新页面 —— 数据还在（之前刷新会重置）。
2. 打开 F12 → Application → Local Storage，手动把 `subscription-react/subs` 的值改成 `{坏` 再刷新，应看到降级到种子数据而不是白屏。
3. 把 `.card` 或 `.bill-table` 也迁一个到 Tailwind 工具类，体会"删 CSS 规则、class 里写样式"。
4. **对照思考**：阶段 3 的 `commit()`（先存后画）在 React 里对应哪两行？`useEffect` 和"画"是同一时刻吗？

> 阶段 4 收口。下一步：把教程站本身升级成笔记发布站（阶段 4 的后半段，或直接进入阶段 5 后端 FastAPI）。
