"use strict";

/* ==========================================================
   1. 存储层 —— 对应 Python 版的 storage.py
   localStorage：浏览器给每个站点的一小块键值存储
   特点：只存字符串（对象必须 JSON.stringify）、同源隔离、容量约 5MB
   ========================================================== */
const STORAGE_KEY = "subscription-web/subs";

const SEED_SUBSCRIPTIONS = [
  { id: "seed-1", name: "Netflix", price: 68, category: "视频", nextBilling: "2026-10-01" },
  { id: "seed-2", name: "Spotify", price: 58, category: "音乐", nextBilling: "2026-10-05" },
  { id: "seed-3", name: "ChatGPT Plus", price: 145, category: "AI 工具", nextBilling: "2026-10-08" },
  { id: "seed-4", name: "Notion", price: 45, category: "效率工具", nextBilling: "2026-10-12" },
  { id: "seed-5", name: "iCloud", price: 21, category: "存储", nextBilling: "2026-10-20" },
];

function loadSubscriptions() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (raw === null) {
    return structuredClone(SEED_SUBSCRIPTIONS); // 首次访问：给一份示例数据
  }
  try {
    // 手贱改坏了 localStorage 里的内容，这里会抛错 —— 必须兜住
    return JSON.parse(raw);
  } catch (err) {
    console.warn("本地数据已损坏，回退到示例数据", err);
    return structuredClone(SEED_SUBSCRIPTIONS);
  }
}

function saveSubscriptions(subs) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(subs));
}

/**
 * 网络/文件加载 —— 第 3 课：异步 fetch
 * async 函数里可以用 await，返回值会被自动包成 Promise
 * 两个 await 各等一件事：
 *   ① await fetch(url)        等响应【头】到了（状态码、响应头）
 *   ② await response.json()   等响应【体】下载并解析完 —— 忘了这个 await，拿到的是 Promise 不是数据
 */
async function fetchSubscriptions(url) {
  const response = await fetch(url);
  if (!response.ok) {
    // fetch 的坑：HTTP 404/500 都【不会】抛异常，只有网络断了才会。
    // 所以必须手动检查 response.ok，否则会拿着一个错误页面去 JSON.parse
    throw new Error(`HTTP ${response.status} ${response.statusText}`);
  }
  return response.json();
}

/* ==========================================================
   2. 数据变更 —— 全部返回【新数组】，不改原数据
   ========================================================== */

/** crypto.randomUUID 依赖安全上下文（https 或 localhost），file:// 下可能没有，故留兜底 */
function createId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function addSubscription(subs, data) {
  return [...subs, { id: createId(), ...data }];
}

function removeSubscription(subs, id) {
  return subs.filter((s) => s.id !== id);
}

/* ==========================================================
   3. 计算 —— 只做数字运算，不碰页面
   与 Python 版 bill.py 的函数一一对应
   ========================================================== */

/** reduce 相当于 Python 的 sum：(累计值, 当前项) => 新累计值 */
function monthlyCost(subs) {
  return subs.reduce((total, s) => total + s.price, 0);
}

function annualCost(subs) {
  return monthlyCost(subs) * 12;
}

function mostExpensive(subs) {
  return subs.reduce((top, s) => (s.price > top.price ? s : top));
}

/** sort 会【原地】修改数组，所以先用展开符 [...subs] 复制一份 */
function sortByPrice(subs) {
  return [...subs].sort((a, b) => b.price - a.price);
}

function sortByNextBilling(subs) {
  return [...subs].sort((a, b) => a.nextBilling.localeCompare(b.nextBilling));
}

/* ==========================================================
   4. 渲染 —— 数据 → DOM 节点
   ========================================================== */

/** 金额格式化：¥145.00（对应 Python 的 f"¥{v:,.2f}"） */
function formatMoney(amount) {
  const text = amount.toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
  return "¥" + text;
}

/**
 * 创建一个带类名和文字的节点。
 * 用 textContent 而不是 innerHTML —— 前者把内容当纯文本处理，
 * 用户输入里就算写了 <script> 也只会被当成字符串显示（防 XSS）。
 */
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined) {
    node.textContent = text;
  }
  return node;
}

function createRow(sub) {
  const tr = document.createElement("tr");
  tr.appendChild(el("td", "", sub.name));
  tr.appendChild(el("td", "num", formatMoney(sub.price)));
  tr.appendChild(el("td", "", sub.category));
  tr.appendChild(el("td", "", sub.nextBilling));

  // 删除按钮把目标 id 存在 data-remove 属性上，事件委托时读回来
  const cell = document.createElement("td");
  const button = el("button", "link-danger", "删除");
  button.type = "button";
  button.dataset.remove = sub.id;
  cell.appendChild(button);
  tr.appendChild(cell);

  return tr;
}

function createStat(label, value, accent = false) {
  const box = el("div", "stat");
  box.appendChild(el("div", "stat-label", label));
  const valueNode = el("p", "stat-value", value);
  if (accent) {
    valueNode.classList.add("accent");
  }
  box.appendChild(valueNode);
  return box;
}

function renderStats(subs) {
  const box = document.getElementById("stats");
  if (subs.length === 0) {
    box.replaceChildren(createStat("订阅数量", "0"));
    return;
  }
  const top = mostExpensive(subs);
  box.replaceChildren(
    createStat("订阅数量", String(subs.length)),
    createStat("月度支出", formatMoney(monthlyCost(subs)), true),
    createStat("年度支出", formatMoney(annualCost(subs))),
    createStat("最贵的一项", `${top.name} · ${formatMoney(top.price)}`)
  );
}

function renderTable(subs) {
  const tbody = document.getElementById("bill-body");
  // replaceChildren：一次性清空旧内容并塞入新节点
  tbody.replaceChildren(...subs.map((s) => createRow(s)));
  document.getElementById("empty-tip").hidden = subs.length > 0;
}

function renderTip(message, ok = false) {
  const tip = document.getElementById("tip");
  tip.textContent = message;
  tip.classList.toggle("ok", ok);
  tip.hidden = false;
}

function setLoading(button, loading) {
  button.disabled = loading;
  button.textContent = loading ? "载入中…" : "载入示例数据";
  button.classList.toggle("is-loading", loading);
}

/* ==========================================================
   5. 状态与渲染入口
   ========================================================== */

const state = { subs: [], sortMode: "date" };

function sortedSubs() {
  return state.sortMode === "price" ? sortByPrice(state.subs) : sortByNextBilling(state.subs);
}

function render() {
  const subs = sortedSubs();
  renderStats(subs);
  renderTable(subs);
}

/** 唯一的数据出口：改内存 → 落盘 → 重画。任何修改都走这里，避免漏存 */
function commit(nextSubs) {
  state.subs = nextSubs;
  saveSubscriptions(nextSubs);
  render();
}

/* ==========================================================
   6. 事件 —— 网页是「等着被打断」，不像 CLI 从头跑到尾
   ========================================================== */
document.addEventListener("DOMContentLoaded", () => {
  state.subs = loadSubscriptions();
  render();

  // --- 新增：表单提交 ---
  const form = document.getElementById("bill-form");
  form.addEventListener("submit", (event) => {
    // 不写这一行，浏览器会按默认行为刷新页面，内存里的数据全丢
    event.preventDefault();

    // 注意：必须用 form.elements.xxx。写 form.name 拿到的是表单元素自身的 name 属性
    const fields = form.elements;
    const name = fields.name.value.trim();
    const price = Number(fields.price.value);
    const category = fields.category.value.trim() || "未分类";
    const nextBilling = fields.nextBilling.value;

    if (!name || !Number.isFinite(price) || price < 0 || !nextBilling) {
      renderTip("请填完整：名称、月费（≥0）、下次扣费日期");
      return;
    }

    document.getElementById("tip").hidden = true;
    commit(addSubscription(state.subs, { name, price, category, nextBilling }));
    form.reset();
    fields.name.focus();
  });

  // --- 删除：事件委托 ---
  // 行是动态生成的，无法直接给它绑事件；把监听挂在一直存在的父容器上，
  // 用 event.target 找到真正被点的元素即可。
  document.getElementById("bill-body").addEventListener("click", (event) => {
    const button = event.target.closest("button[data-remove]");
    if (!button) return; // 点在了行空白处，忽略
    commit(removeSubscription(state.subs, button.dataset.remove));
    renderTip("已删除一条订阅", true);
  });

  // --- 排序切换 ---
  document.getElementById("sort-price").addEventListener("click", () => {
    state.sortMode = "price";
    render();
  });

  document.getElementById("sort-date").addEventListener("click", () => {
    state.sortMode = "date";
    render();
  });

  // --- 导出：浏览器不能直接写本地文件，只能「制造下载」 ---
  document.getElementById("export").addEventListener("click", () => {
    const json = JSON.stringify(state.subs, null, 2);
    const blob = new Blob([json], { type: "application/json" });
    const url = URL.createObjectURL(blob); // 内存里的临时地址
    const link = document.createElement("a");
    link.href = url;
    link.download = "subscriptions.json";
    link.click();
    URL.revokeObjectURL(url); // 用完释放，否则内存泄漏
    renderTip("已导出 subscriptions.json（格式与 CLI 版的数据文件一致）", true);
  });

  // --- 恢复示例数据 ---
  document.getElementById("reset").addEventListener("click", () => {
    if (!confirm("这会覆盖当前所有订阅，确定恢复示例数据？")) return;
    commit(structuredClone(SEED_SUBSCRIPTIONS));
    renderTip("已恢复示例数据", true);
  });

  // --- 异步载入示例数据（fetch）---
  document.getElementById("import").addEventListener("click", async (event) => {
    const button = event.currentTarget;
    setLoading(button, true);
    try {
      const list = await fetchSubscriptions("sample.json");
      if (!confirm(`即将载入 ${list.length} 条订阅并覆盖当前数据，继续？`)) return;
      // 文件里的数据不带 id，进来时补一个
      commit(list.map((item) => ({ id: createId(), ...item })));
      renderTip(`已载入 ${list.length} 条订阅`, true);
    } catch (err) {
      console.error(err);
      renderTip(
        "载入失败：" + err.message + "。提示：直接双击打开的 file:// 页面无法读取本地 JSON（浏览器安全限制），请用 Live Server 或在线地址访问。"
      );
    } finally {
      // finally 无论成功失败都会走到 —— 最适合放「收起加载状态」这类收尾动作
      setLoading(button, false);
    }
  });
});
