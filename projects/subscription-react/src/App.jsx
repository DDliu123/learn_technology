import { useState } from "react";
import SiteHeader from "./components/SiteHeader.jsx";
import StatCard from "./components/StatCard.jsx";
import BillTable from "./components/BillTable.jsx";
import BillForm from "./components/BillForm.jsx";
import { SUBSCRIPTIONS, createId } from "./data.js";
import {
  annualCost,
  formatMoney,
  monthlyCost,
  mostExpensive,
  sortByNextBilling,
  sortByPrice,
} from "./money.js";

export default function App() {
  // useState 返回 [当前值, 设置函数]。调用设置函数 → React 自动重新渲染
  const [subs, setSubs] = useState(() => structuredClone(SUBSCRIPTIONS));
  const [sortMode, setSortMode] = useState("date");

  // --- 修改数据：一律「基于旧值返回新数组」，绝不 push / splice 直接改 ---
  function handleAdd(data) {
    setSubs((prev) => [...prev, { id: createId(), ...data }]);
  }

  function handleRemove(id) {
    setSubs((prev) => prev.filter((s) => s.id !== id));
  }

  function handleReset() {
    if (!confirm("这会覆盖当前所有订阅，确定恢复示例数据？")) return;
    setSubs(structuredClone(SUBSCRIPTIONS));
  }

  // --- 派生数据：由 state 算出来，不要再存一份 state ---
  const visible = sortMode === "price" ? sortByPrice(subs) : sortByNextBilling(subs);
  const top = subs.length > 0 ? mostExpensive(subs) : null;

  return (
    <>
      <SiteHeader />

      <main className="container">
        <section className="stats">
          <StatCard label="订阅数量" value={String(subs.length)} />
          <StatCard label="月度支出" value={formatMoney(monthlyCost(subs))} accent />
          <StatCard label="年度支出" value={formatMoney(annualCost(subs))} />
          <StatCard
            label="最贵的一项"
            value={top ? `${top.name} · ${formatMoney(top.price)}` : "—"}
          />
        </section>

        <BillForm onAdd={handleAdd} />

        <section className="card">
          <div className="card-head">
            <h2>我的订阅</h2>
            <div className="actions">
              <button type="button" onClick={() => setSortMode("date")}>
                按下次扣费排序
              </button>
              <button type="button" onClick={() => setSortMode("price")}>
                按月费排序
              </button>
              <button type="button" onClick={handleReset}>
                恢复示例数据
              </button>
            </div>
          </div>

          <BillTable subs={visible} onRemove={handleRemove} />
        </section>
      </main>

      <footer className="site-footer">
        <p>阶段 4 · React &nbsp;·&nbsp; 数据存在内存里，刷新会重置 —— 第 3 课用 useEffect 落盘</p>
      </footer>
    </>
  );
}
