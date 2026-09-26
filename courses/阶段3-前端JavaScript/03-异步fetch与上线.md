# 阶段 3 · 第 3 课：异步 fetch + 部署上线

> 产出：网页版订阅管家支持从 JSON 文件异步载入数据，并正式挂上线
> 在线地址：https://ddliu123.github.io/learn_technology/subscription/

---

## 1. JS 最难的一个概念：异步

**为什么要有异步**：网络请求慢（几十毫秒到几秒）。如果 JS 像 Python 一样等着它完成，整个页面会卡死 —— 按钮点不动、动画停住。所以 JS 的策略是"先别等，好了叫我"。

三种写法，历史演进：

| 写法 | 形态 | 问题 |
|---|---|---|
| 回调函数 | `getData(cb)` | 嵌套多了变成"回调地狱" |
| Promise | `getData().then(...).catch(...)` | 链式可读，但仍要记 `.then` |
| **async/await** | `const d = await getData()` | **看起来像同步代码，用就好** |

记住两句：

- `async` 修饰的函数**一定返回 Promise**
- 只有 `await` 能"解开"Promise，而且**只能在 async 函数里用**

---

## 2. fetch 的正确写法

```js
async function fetchSubscriptions(url) {
  const response = await fetch(url);        // ① 等响应【头】到达
  if (!response.ok) {                        // ② HTTP 404/500 不会自动抛错！必须手动判
    throw new Error(`HTTP ${response.status}`);
  }
  return response.json();                    // ③ 再等【体】下载并解析
}
```

**两个 await，各自等一件事**

| | 等什么 | 忘了会怎样 |
|---|---|---|
| `await fetch(url)` | 响应头（状态码、Header） | 拿到的是 Promise，不是响应 |
| `await response.json()` | 响应体下载 + JSON 解析 | 拿到的是 Promise，`undefined` 满天飞 |

**最大的坑**：`fetch` 只在网络断了时抛异常，**HTTP 404 / 500 它认为"请求成功"**。不检查 `response.ok`，就会把错误页面当成数据去解析，报出一个让人完全摸不着头脑的 JSON 语法错误。

---

## 3. 错误处理：try / catch / finally

```js
setLoading(button, true);
try {
  const list = await fetchSubscriptions("sample.json");
  commit(list.map((item) => ({ id: createId(), ...item })));
} catch (err) {
  renderTip("载入失败：" + err.message);   // 给用户看的
  console.error(err);                      // 给自己看的
} finally {
  setLoading(button, false);               // 成功失败都要执行
}
```

`finally` 天生适合放收尾动作：**关闭加载态、释放资源、隐藏遮罩**。写一次就覆盖成功和失败两条路径。

---

## 4. 浏览器安全：`file://` 下 fetch 会失败

**现象**：双击 HTML 文件直接打开，点"载入示例数据"必失败，控制台报：

```
Access to fetch at 'file:///.../sample.json' from origin 'null' has been blocked by CORS policy
```

**原因**：本地文件的 origin 是 `null`，不属于任何"源"，浏览器拒绝它读取任何资源。这不是 bug，是安全设计 —— 否则任何网页都能读你硬盘上的文件。

**解法（三选一）**

1. 用 **Live Server**（VS Code 插件）打开 → `http://127.0.0.1:5500` 有正常 origin
2. 部署到线上（本课做法）→ `https://` 有正常 origin
3. 让用户选文件：`<input type="file">` + `FileReader`（不经网络，不受此限制）

**顺带理解 CORS**：跨域请求时，服务器必须在响应头里明确允许（`Access-Control-Allow-Origin`），浏览器才把结果交给你的代码。阶段 5 写后端时会被这个拦一次，到时候就懂了 —— 前端拦你，是为了用户的数据不在你不知情时被偷走。

---

## 5. 部署：为什么项目挪到了 `docs/subscription/`

GitHub Pages 的规则很硬：

- 一个仓库**只能有一个站点**，来源只能是「根目录」或「`/docs`」
- 站点的子路径 = `/docs` 下的子目录

本仓库的站点已经给了教程站（`docs/`），所以网页版只能作为子目录存在。于是：

```
git mv projects/subscription-web docs/subscription
```

在线地址随之确定：

| 位置 | URL |
|---|---|
| 教程站首页 | `https://ddliu123.github.io/learn_technology/` |
| 网页版订阅管家 | `https://ddliu123.github.io/learn_technology/subscription/` |
| 示例数据文件 | `https://ddliu123.github.io/learn_technology/subscription/sample.json` |

**为什么不复制一份过去**：源码在 `projects/`、发布副本在 `docs/` 是最诱人的错误做法 —— 两边迟早不同步，你会遇到线上还是旧版本、本地却是新的。**单一副本，直接发布它**。代价只是 URL 里多一层路径。

**上线链路**（与阶段 1 相同，铁律不变）

```
git push → GitHub 自动构建（约 40 秒）→ 线上生效
```

红线：**本地改了没 push，线上永远不会变。**

---

## 6. 本课改动

| 文件 | 变化 |
|---|---|
| `app.js` | 新增 `fetchSubscriptions()`、`setLoading()`、"载入示例数据"按钮的 async 处理 |
| `index.html` | 工具条加 `<button id="import">` |
| `style.css` | `button:disabled` 样式（防止加载中重复点击） |
| `sample.json` | 静态数据文件，**不含 id**（外部数据源不该知道前端的内部标识） |
| `docs/index.html` | 新增 Demo 区块 + 阶段表状态更新（1/2 已完成，3 进行中） |

载入后补 `{ id: createId(), ...item }` —— 外部数据进来时在边界处补齐内部约定。

---

## 7. 验证

Node 侧 9 组断言全绿，其中异步三例：

```
✅ fetch 成功返回 5 条，月度 ¥337.00（与 CLI 版一致）
✅ HTTP 404 → 抛出 "HTTP 404"（证明 response.ok 检查生效）
✅ 网络错误 → 抛出 TypeError（证明网络层异常能穿透）
```

线上 HTTP 检查：`subscription/`、`sample.json`、`app.js` 全部 **200**。

---

## 8. 作业

1. 用 Live Server 打开本地页面点"载入示例数据"，再**关掉 Live Server、双击 index.html 直接打开**再点一次 —— 对比两次结果，截图记下 CORS 报错信息。
2. 加"导入文件"功能：`<input type="file" accept=".json">` + `FileReader`（提示：`reader.readAsText(file)`，`onload` 里 `JSON.parse(e.target.result)`）。这是绕过 `file://` 限制的正规做法。
3. 给 fetch 加一个超时控制（`AbortController` + `setTimeout`）。
4. **发布作业**：按路线里的笔记模板写阶段 3 的笔记，重点写第 4 点 —— AI 哪里写砸了、你怎么改的。

---

## 阶段 3 完成标准

✅ 网页能增删改订阅
✅ 数据存在浏览器、刷新不丢
✅ 能从外部文件异步载入
✅ 已在线可访问

下一阶段：**React** —— 阶段 4 会把这个手写 DOM 的项目重写成组件版，同时把教程站升级成真正的笔记发布站。届时你会明白这一阶段的「手写 `commit → render`」到底是在给什么打地基。
