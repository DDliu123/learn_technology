/**
 * 组件 = 返回 JSX 的函数，函数名必须大写开头。
 * props 是从父组件传进来的只读数据 —— 组件内部永远不要修改 props。
 */
export default function StatCard({ label, value, accent = false }) {
  return (
    <div className="stat">
      <div className="stat-label">{label}</div>
      {/* className 不能写成 class：class 是 JS 的关键字 */}
      <p className={accent ? "stat-value accent" : "stat-value"}>{value}</p>
    </div>
  );
}
