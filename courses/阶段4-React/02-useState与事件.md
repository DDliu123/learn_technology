# 阶段 4 · 第 2 课：useState 与事件处理

> 项目：`projects/subscription-react/`
> 本课产出：把阶段 3 的增删改查搬进 React，手动重画那一步真的消失了

---

## 1. useState：让组件"记住"东西

```jsx
const [subs, setSubs] = useState(() => structuredClone(SUBSCRIPTIONS));
```

| 元素 | 含义 |
|---|---|
| `subs` | 当前值 |
| `setSubs` | 唯一能改它的函数 |
| `useState(初值)` | 只在**首次渲染**时算一次 |
| `useState(() => ...)` | 惰性初始化 —— 开销大的初值用这种写法 |

**两条铁律**

1. **绝不直接赋值**：`subs.push(x)` 或 `subs = x` 界面不会更新（React 不知道数据变了）。
2. **换掉而不是改动**：`setSubs((prev) => [...prev, item])` —— 与阶段 3 的"不可变更新"是同一条规则。

```jsx
setSubs((prev) => [...prev, { id: createId(), ...data }]);   // 增
setSubs((prev) => prev.filter((s) => s.id !== id));           // 删
```

用 `prev =>` 回调形式而不是直接给新值：连续多次 set 时不会互相覆盖。

---

## 2. 派生数据不要再存一份 state

```jsx
const visible = sortMode === "price" ? sortByPrice(subs) : sortByNextBilling(subs);
const top = subs.length > 0 ? mostExpensive(subs) : null;
```

能算出来的，就别 `useState` 存。存两份就要维护两份同步 —— 这是状态 bug 的主要来源。

state 里只放**算不出来的东西**：数据本身、当前排序方式、表单草稿、是否加载中。

---

## 3. 事件处理

| 写法 | 结果 |
|---|---|
| `onClick={handleReset}` | ✅ 传函数引用 |
| `onClick={() => onRemove(sub.id)}` | ✅ 需要参数时包箭头函数 |
| `onClick={onRemove(sub.id)}` | ❌ **渲染时立刻执行**，页面一打开就全删了 |

**表单三条**

```jsx
function handleSubmit(event) {
  event.preventDefault();          // ① 漏了就刷新页面，state 全丢
  // ② 校验
  // ③ onAdd(data) 交给父组件，自己不改数据
}
```

**受控输入**：`value={draft.name}` + `onChange`。一个函数处理全部输入框：

```jsx
setDraft((prev) => ({ ...prev, [name]: value }));   // [name] 是计算属性名
```

对比阶段 3 的 `form.elements.name.value`（非受控）：React 里输入框的值由 state 决定，所以清空表单只需 `setDraft(EMPTY_DRAFT)`。

---

## 4. 数据流：子不碰父的数据

```
App 持有 subs
 ├─ <BillForm onAdd={handleAdd} />        子调父的函数，把新数据交上去
 └─ <BillTable subs={visible} onRemove={handleRemove} />   子只说"删哪个 id"
```

props 只读。**子组件永远不修改收到的数据**，只通过回调告诉父组件"发生了什么"。阶段 3 的事件委托在 React 里不需要了 —— 每一行都有自己明确的 `onClick`。

---

## 5. 本课文件

| 文件 | 变化 |
|---|---|
| `src/App.jsx` | 新增 `useState(subs)` / `useState(sortMode)`，四个处理函数 |
| `src/components/BillForm.jsx` | **新增**：受控表单 + 校验 + 分类下拉建议 |
| `src/components/BillTable.jsx` | 新增 `onRemove` props，行内删除按钮 |
| `src/index.css` | 新增 `.card-head` / `.actions` / `.bill-form` / `.tip` |

---

## 6. 不用浏览器也能验证

`scratch/react-check/` 两个脚本：

```bash
node money.test.mjs      # 计算层：337 / 4044 / 排序不污染 / 空数组 0
node render.test.mjs     # 组件层：把 React 渲染成 HTML 字符串再断言
```

`render.test.mjs` 用的是 Vite 自带的 SSR 加载器 + `renderToStaticMarkup`：

```js
const server = await createServer({ root: ROOT, appType: "custom" });
const { default: App } = await server.ssrLoadModule("/src/App.jsx");
const html = renderToStaticMarkup(createElement(App));
```

**必须 `createElement(App)`，不能 `App()`** —— 直接调用会在渲染上下文外触发 `useState` 报错。

实测输出：

```
✅ 组件渲染测试通过：App 全量渲染 / 统计数值正确 / 默认排序 / 表单存在 / 空列表兜底
   渲染 HTML 长度：2343 字符
```

---

## 7. 本机踩坑

| 现象 | 原因 / 解法 |
|---|---|
| `npm view` 报缓存目录无写权限 | Node 装在 `C:\SoftWare`，执行 `npm config set cache "C:/Users/wise/.npm-cache"` |
| Node 里 `import("C:/...")` 报 `ERR_UNSUPPORTED_ESM_URL_SCHEME` | Windows 绝对路径必须先转 `pathToFileURL(...).href` |

---

## 8. 作业

1. 跑 `npm run dev`，添加一条真在付的订阅，看统计卡是否**不用手动重画**就更新。
2. 加"编辑"功能：点行内「编辑」把该条填回表单，提交后按 id 替换（提示：App 里加 `editingId` state）。
3. 排序按钮做成切换：再点一次反向排序（`sortMode` 存 `"price-asc"` / `"price-desc"`）。
4. 加"平均月费"卡片（派生数据，别存 state）。

> 下一课：`useEffect` + localStorage，让刷新后数据不丢；再用 Vite 构建产物发布到子站。
