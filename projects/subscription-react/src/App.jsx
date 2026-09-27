import { useEffect, useState } from "react";
import SiteHeader from "./components/SiteHeader.jsx";
import StatCard from "./components/StatCard.jsx";
import BillTable from "./components/BillTable.jsx";
import BillForm from "./components/BillForm.jsx";
import { SUBSCRIPTIONS, createId } from "./data.js";
import { loadSubscriptions, saveSubscriptions } from "./storage.js";
import {
  annualCost,
  formatMoney,
  monthlyCost,
  mostExpensive,
  sortByNextBilling,
  sortByPrice,
} from "./money.js";

export default function App() {
  // 惰性初值：首次渲染时优先读 localStorage，没有才用种子数据
  const [subs, setSubs] = useState(() => loadSubscriptions() ?? structuredClone(SUBSCRIPTIONS));
  const [sortMode, setSortMode] = useState("date");

  // useEffect：subs 每次变化都把最新值写回 localStorage
  // 第二个参数是「依赖数组」—— 只有里面的变量变了才重新执行
  useEffect(() => {
    saveSubscriptions(subs);
  }, [subs]);

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
        <section className="stats grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
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
        <p>阶段 4 · React &nbsp;·&nbsp; 数据已写入 localStorage，刷新不丢；与阶段 3 网页版共用同一套数据结构</p>
      </footer>
    </>
  );
}
