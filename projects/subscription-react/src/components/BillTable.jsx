import { formatMoney } from "../money.js";

/** 一行订阅。拆成独立组件的好处：结构清楚，将来加"编辑/删除"只改这一处 */
function BillRow({ sub }) {
  return (
    <tr>
      <td>{sub.name}</td>
      <td className="num">{formatMoney(sub.price)}</td>
      <td>{sub.category}</td>
      <td>{sub.nextBilling}</td>
    </tr>
  );
}

export default function BillTable({ subs }) {
  if (subs.length === 0) {
    return <p className="empty">还没有订阅记录。</p>;
  }

  return (
    <table className="bill-table">
      <thead>
        <tr>
          <th>名称</th>
          <th className="num">月费</th>
          <th>分类</th>
          <th>下次扣费</th>
        </tr>
      </thead>
      <tbody>
        {/* map 渲染列表：每个元素必须带 key，React 靠它判断"哪一行变了" */}
        {subs.map((sub) => (
          <BillRow key={sub.id} sub={sub} />
        ))}
      </tbody>
    </table>
  );
}
