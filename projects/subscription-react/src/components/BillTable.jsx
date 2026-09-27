import { formatMoney } from "../money.js";

/** 子组件通过 props 拿到 onRemove 回调，把"要删谁"告诉父组件 —— 它自己不改数据 */
function BillRow({ sub, onRemove }) {
  return (
    <tr>
      <td>{sub.name}</td>
      <td className="num">{formatMoney(sub.price)}</td>
      <td>{sub.category}</td>
      <td>{sub.nextBilling}</td>
      <td>
        {/* 必须包一层箭头函数：写成 onClick={onRemove(sub.id)} 会在渲染时立刻执行 */}
        <button type="button" className="link-danger" onClick={() => onRemove(sub.id)}>
          删除
        </button>
      </td>
    </tr>
  );
}

export default function BillTable({ subs, onRemove }) {
  if (subs.length === 0) {
    return <p className="empty">还没有订阅记录，先在上面添加一条。</p>;
  }

  return (
    <table className="bill-table">
      <thead>
        <tr>
          <th>名称</th>
          <th className="num">月费</th>
          <th>分类</th>
          <th>下次扣费</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {/* map 渲染列表：每个元素必须带 key，React 靠它判断"哪一行变了" */}
        {subs.map((sub) => (
          <BillRow key={sub.id} sub={sub} onRemove={onRemove} />
        ))}
      </tbody>
    </table>
  );
}
