/**
 * 纯计算函数 —— 与阶段 2 的 bill.py、阶段 3 的 app.js 完全一致。
 * 把计算独立成模块的好处：换框架（CLI / 原生 JS / React）它都不用改。
 */

export function monthlyCost(subs) {
  return subs.reduce((total, s) => total + s.price, 0);
}

export function annualCost(subs) {
  return monthlyCost(subs) * 12;
}

export function mostExpensive(subs) {
  return subs.reduce((top, s) => (s.price > top.price ? s : top));
}

/** sort 是原地排序，先展开复制一份，避免改坏原数据 */
export function sortByPrice(subs) {
  return [...subs].sort((a, b) => b.price - a.price);
}

export function sortByNextBilling(subs) {
  return [...subs].sort((a, b) => a.nextBilling.localeCompare(b.nextBilling));
}

export function formatMoney(amount) {
  return (
    "¥" +
    amount.toLocaleString("zh-CN", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    })
  );
}
