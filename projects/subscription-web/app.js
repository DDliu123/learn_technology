"use strict";

/* ==========================================================
   1. 数据 —— 对象的数组，对应 Python 的 list[dict]
   第 2 课会把它换成从 localStorage 读取
   ========================================================== */
const SUBSCRIPTIONS = [
  { name: "Netflix", price: 68, category: "视频", nextBilling: "2026-10-01" },
  { name: "Spotify", price: 58, category: "音乐", nextBilling: "2026-10-05" },
  { name: "ChatGPT Plus", price: 145, category: "AI 工具", nextBilling: "2026-10-08" },
  { name: "Notion", price: 45, category: "效率工具", nextBilling: "2026-10-12" },
  { name: "iCloud", price: 21, category: "存储", nextBilling: "2026-10-20" },
];

/* ==========================================================
   2. 计算 —— 只做数字运算，不碰页面
   与 Python 版 bill.py 的函数一一对应，方便对照理解
   ========================================================== */

/** reduce 相当于 Python 的 sum / functools.reduce：(累计值, 当前项) => 新累计值 */
function monthlyCost(subs) {
  return subs.reduce((total, s) => total + s.price, 0);
}

function annualCost(subs) {
  return monthlyCost(subs) * 12;
}

function mostExpensive(subs) {
  return subs.reduce((top, s) => (s.price > top.price ? s : top));
}

/** sort 会【原地】修改数组，所以先用展开符 [...subs] 复制一份，避免污染原数据 */
function sortByPrice(subs) {
  return [...subs].sort((a, b) => b.price - a.price);
}

function sortByNextBilling(subs) {
  return [...subs].sort((a, b) => a.nextBilling.localeCompare(b.nextBilling));
}

/* ==========================================================
   3. 渲染 —— 把数据变成页面上的 DOM 节点
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
 * 用 textContent 而不是 innerHTML —— 它把内容当纯文本处理，
 * 用户输入里就算写了 <script> 也只会被当成字符串显示。
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
  // replaceChildren：一次性清空旧内容并塞入新节点，比手动循环删行可靠
  tbody.replaceChildren(...subs.map((s) => createRow(s)));
  document.getElementById("empty-tip").hidden = subs.length > 0;
}

/** 数据变化 → 重新渲染。这是所有前端框架的核心思想，先用手写版理解它 */
function refresh(subs) {
  renderStats(subs);
  renderTable(subs);
}

/* ==========================================================
   4. 事件 —— 网页是「等着被打断」，不像 CLI 从头跑到尾
   ========================================================== */
document.addEventListener("DOMContentLoaded", () => {
  refresh(sortByNextBilling(SUBSCRIPTIONS));

  document.getElementById("sort-price").addEventListener("click", () => {
    refresh(sortByPrice(SUBSCRIPTIONS));
  });

  document.getElementById("sort-date").addEventListener("click", () => {
    refresh(sortByNextBilling(SUBSCRIPTIONS));
  });
});
