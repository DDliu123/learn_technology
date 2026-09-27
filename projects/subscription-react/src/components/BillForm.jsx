import { useState } from "react";

const EMPTY_DRAFT = { name: "", price: "", category: "", nextBilling: "" };

/**
 * 受控表单：输入框的 value 由 state 决定，每次输入都写回 state。
 * 校验通过后通过 props 回调 onAdd 把数据交给父组件 —— 子组件不碰父组件的数据。
 */
export default function BillForm({ onAdd }) {
  const [draft, setDraft] = useState(EMPTY_DRAFT);
  const [error, setError] = useState("");

  function handleChange(event) {
    const { name, value } = event.target;
    // 展开旧值再覆盖一个字段：[name] 是计算属性名，一个函数处理所有输入框
    setDraft((prev) => ({ ...prev, [name]: value }));
  }

  function handleSubmit(event) {
    event.preventDefault(); // 不写这行，浏览器会刷新页面，state 全丢

    const price = Number(draft.price);
    if (!draft.name.trim() || !Number.isFinite(price) || price < 0 || !draft.nextBilling) {
      setError("请填完整：名称、月费（≥0）、下次扣费日期");
      return;
    }

    setError("");
    onAdd({
      name: draft.name.trim(),
      price,
      category: draft.category.trim() || "未分类",
      nextBilling: draft.nextBilling,
    });
    setDraft(EMPTY_DRAFT); // 提交后清空表单
  }

  return (
    <section className="card">
      <h2>添加订阅</h2>
      <form className="bill-form" onSubmit={handleSubmit}>
        <label>
          名称
          <input
            name="name"
            value={draft.name}
            onChange={handleChange}
            placeholder="ChatGPT Plus"
          />
        </label>
        <label>
          月费（元）
          <input
            name="price"
            type="number"
            min="0"
            step="0.01"
            value={draft.price}
            onChange={handleChange}
            placeholder="145"
          />
        </label>
        <label>
          分类
          <input
            name="category"
            list="category-list"
            value={draft.category}
            onChange={handleChange}
            placeholder="AI 工具"
          />
          <datalist id="category-list">
            <option value="视频"></option>
            <option value="音乐"></option>
            <option value="AI 工具"></option>
            <option value="效率工具"></option>
            <option value="存储"></option>
          </datalist>
        </label>
        <label>
          下次扣费
          <input
            name="nextBilling"
            type="date"
            value={draft.nextBilling}
            onChange={handleChange}
          />
        </label>
        <button type="submit">添加</button>
      </form>

      {/* 条件渲染：error 为空字符串时整段不渲染 */}
      {error && <p className="tip">{error}</p>}
    </section>
  );
}
