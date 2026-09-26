# 阶段 3 · 第 2 课：localStorage 持久化 + 表单增删改查

> 对应阶段 2 第 2 课（Python 的 `storage.py`）—— 同一个问题，两种解法，建议对照着看。

---

## 1. 对照：文件存储 vs localStorage

| Python CLI | JS 网页 | 说明 |
|---|---|---|
| `data/subscriptions.json` | `localStorage` 键值库 | 都是"程序之外的持久化位置" |
| `json.load(f)` | `JSON.parse(str)` | 字符串 → 对象 |
| `json.dump(obj, f)` | `JSON.stringify(obj)` | 对象 → 字符串 |
| `ensure_ascii=False, indent=2` | `JSON.stringify(obj, null, 2)` | 第三个参数是缩进 |
| `DATA_FILE.exists()` | `getItem(k) === null` | 判断有没有存过 |
| `except JSONDecodeError` | `try { JSON.parse } catch (e) {}` | 内容坏了要兜住 |
| 直接打开文件看 | F12 → Application → Local Storage | 调试入口 |

**localStorage 三个硬约束**

1. **只能存字符串** —— 对象必须 `JSON.stringify`，读出来必须 `JSON.parse`。存了对象进去会变成 `"[object Object]"`。
2. **同源隔离** —— 每个「协议+域名+端口」一套，`localhost:5500` 和 `localhost:3000` 互不相通。这也是它的安全边界：**不能跨站读取**。
3. **容量约 5MB** —— 只适合存用户偏好、小规模业务数据。真要存几万条得上 IndexedDB。

**另一个性质**：它随浏览器走。**换设备、换浏览器、清缓存 → 数据没了**。所以真实产品里它只能当本地草稿，重要数据必须存服务器（阶段 5 之后解决）。

---

## 2. 本课三个必知的心法

### ① `event.preventDefault()` —— 漏写就白干

```js
form.addEventListener("submit", (event) => {
  event.preventDefault();  // 少了这一行：浏览器刷新页面，JS 内存里的状态全丢
  ...
});
```

表单提交的默认行为是"向服务器发请求并刷新页面"。我们的逻辑全在前端内存里，一刷新就没了。

### ② 事件委托 —— 动态元素的唯一可靠解法

表格行是 JS **动态生成**的，绑定事件时它还不存在：

```js
// ❌ 拿不到：这些行此刻还没被创建
document.querySelectorAll("tr .delete").forEach((b) => b.addEventListener(...));

// ✅ 委托：监听挂在一直存在的父容器上，靠事件冒泡找目标
tbody.addEventListener("click", (event) => {
  const button = event.target.closest("button[data-remove]");
  if (!button) return;                       // 点在行空白处就忽略
  commit(removeSubscription(state.subs, button.dataset.remove));
});
```

`event.target` 是真正被点的元素（可能是按钮里的文字节点），`closest()` 往上找最近匹配的祖先。

### ③ 不可变更新 —— 改数据返回新数组

```js
function addSubscription(subs, data) {
  return [...subs, { id: createId(), ...data }];   // 返回新数组，subs 不变
}
```

Python 里习惯 `list.append()` 原地改。前端为什么反着来：**如果到处都是原地修改，"什么时候该重画界面"就没人知道了**。返回新对象 = 明确的变更信号 —— 这正是 React 的核心约定，先在这里养成习惯。

顺带，`sort()` 也是原地的（第 1 课已踩过），两处都需要 `[...]` 拷贝。

---

## 3. 两个隐蔽的坑

**坑一：`form.name` 不是你那个输入框**

```js
form.name        // ❌ HTMLFormElement 自己的 name 属性
form.elements.name  // ✅ 名为 "name" 的控件
```

`name` / `id` / `method` / `length` 都是表单元素自身的属性，会和你的控件名撞车。**取表单值一律走 `form.elements`**。

**坑二：别用数组下标当身份**

列表会排序、会增删，**下标会变**。用下标删除会在排序后删错行。所以每条数据要有稳定 `id`：

```js
id: crypto.randomUUID(); // 需要安全上下文（https / localhost），file:// 下可能没有 → 已加兜底
```

---

## 4. 浏览器沙箱：为什么「导出」这么别扭

浏览器**不允许 JS 直接写用户硬盘**，所以"存文件"只能靠制造一次下载：

```js
const blob = new Blob([json], { type: "application/json" });
const url = URL.createObjectURL(blob);   // 内存里的临时地址
link.href = url; link.download = "subscriptions.json"; link.click();
URL.revokeObjectURL(url);                // 用完释放，否则内存泄漏
```

导出的 JSON 结构与 CLI 版 `data/subscriptions.json` **完全一致** —— 同一份数据能在命令行和网页之间来回搬运。

---

## 5. 架构：单一数据出口

```js
function commit(nextSubs) {   // 唯一改数据的地方
  state.subs = nextSubs;
  saveSubscriptions(nextSubs); // 落盘
  render();                    // 重画
}
```

对应阶段 2 的铁律：**先读 → 改内存 → 整体写回**。分散在各处的 `save` 迟早互相覆盖，一个出口也方便将来加"撤销"或"同步到服务器"。

状态也从「无状态」变成「有状态」了：

```js
const state = { subs: [], sortMode: "date" };  // 数据 + 界面状态放一起
```

**演进对照**：第 1 课是 `refresh(subs)`（外部传数据），现在是 `render()`（内部读 state）。多了"当前排哪种序"这类界面状态，就必须有一个地方统一存放。

---

## 6. 本课文件变化

| 文件 | 变化 |
|---|---|
| `index.html` | 新增表单区（`<datalist>` 做可选可填的分类下拉）、表格加「操作」列、底部导出/重置按钮 |
| `style.css` | 表单 Grid（`auto-fit` 自动降列）、输入框 focus 描边、`.tip` / `.tip.ok` 提示条、`.link-danger` 删除按钮 |
| `app.js` | 新增存储层（load/save）、变更层（add/remove/createId）、state 与 commit、四类事件（提交/委托删除/排序/导出/重置） |

---

## 7. 验证（Node 假浏览器，跑了 8 组断言）

```
存储往返 ✅   新增不改原数组 ✅   按 id 删除 ✅
数据损坏回退种子 ✅   id 唯一 ✅   排序不污染 ✅   HTML/JS 的 id 一致 ✅
月度 ¥337.00 → 新增 Claude Pro ¥158 → ¥495.00 → 删除回到 5 条
```

> 沙箱坑记一笔：`vm` 是全新 realm，浏览器内置的 `structuredClone` 不在其中，测试时要手动注入 —— 这类"同一个 API 在不同运行时里存在与否不同"的差异，是前端工程里最常见的麻烦来源。

---

## 8. 作业

1. 添加两条真实订阅，按 F12 → Application → Local Storage 找到 `subscription-web/subs`，**手动改坏 JSON 内容后刷新**，确认页面回退到示例数据而不是白屏。
2. 加「编辑」功能：点编辑 → 表单回填该项 → 提交时替换而不是新增（提示：表单里藏一个 `<input type="hidden" name="id">`）。
3. 给导出按钮加判断：数据为空时不导出，提示「没有可导出的订阅」。
4. **进阶**（对应阶段 2 的 `due` 作业）：新增一个统计卡片「7 天内待扣费」，用 `new Date()` 和日期差判断。

> 下一课：fetch + 异步 + 部署上线，并把这个页面挂到你的教程站上。
