# subscription-react

阶段 4：React 版订阅账单管家。组件化、受控表单、localStorage 持久化（数据刷新不丢）。

## 命令

```bash
npm install              # 装依赖（缓存目录已改到 ~/.npm-cache）
npm run dev              # 开发服务器 http://localhost:5173
npm run build            # 构建到 ../../docs/subscription-react（Pages 子站，自动上线）
npm run lint             # oxlint，0 错误
```

## 结构

| 文件 | 作用 |
|---|---|
| `src/money.js` | 纯计算，与阶段 2 `bill.py`、阶段 3 `app.js` 同构 |
| `src/data.js` | 种子数据 + `createId` |
| `src/storage.js` | localStorage 读写（损坏数据降级到种子） |
| `src/App.jsx` | 根组件：`useState` 管数据、`useEffect` 落盘 |
| `src/components/` | `SiteHeader` / `StatCard` / `BillTable` / `BillForm` |

## 部署说明

Pages 一个仓库只给一个站点源（根目录或 `/docs`），所以 React 应用只能做子目录。
`vite.config.js` 的 `base` 设为 `/learn_technology/subscription-react/`，`build.outDir` 直接指向 `../../docs/subscription-react` —— 单一副本，push 即上线。

## 技术栈

React 19 + Vite 8 + Tailwind v4 + oxlint。
