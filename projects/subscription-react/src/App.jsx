import SiteHeader from "./components/SiteHeader.jsx";
import StatCard from "./components/StatCard.jsx";
import BillTable from "./components/BillTable.jsx";
import { SUBSCRIPTIONS } from "./data.js";
import {
  annualCost,
  formatMoney,
  monthlyCost,
  mostExpensive,
  sortByNextBilling,
} from "./money.js";

/**
 * 第 1 课：只做静态渲染 —— 数据写死、没有交互。
 * React 的核心公式：UI = f(state)
 * 你只描述「数据是这样时，界面长这样」，不用再手写 createElement / appendChild / 重画。
 */
export default function App() {
  const subs = sortByNextBilling(SUBSCRIPTIONS);
  const top = mostExpensive(subs);

  return (
    <>
      <SiteHeader />

      <main className="container">
        <section className="stats">
          <StatCard label="订阅数量" value={String(subs.length)} />
          <StatCard label="月度支出" value={formatMoney(monthlyCost(subs))} accent />
          <StatCard label="年度支出" value={formatMoney(annualCost(subs))} />
          <StatCard label="最贵的一项" value={`${top.name} · ${formatMoney(top.price)}`} />
        </section>

        <section className="card">
          <h2>我的订阅</h2>
          {/* 数据以 props 的形式传给子组件 */}
          <BillTable subs={subs} />
        </section>
      </main>

      <footer className="site-footer">
        <p>阶段 4 · React &nbsp;·&nbsp; 数据当前写死在 data.js，第 2、3 课逐步改为可交互与可持久化</p>
      </footer>
    </>
  );
}
