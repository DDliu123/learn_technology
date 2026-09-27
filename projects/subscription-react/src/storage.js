/**
 * localStorage 读写 —— 与阶段 3 的 storage.js / 阶段 2 的 storage.py 是同一职责的第三版。
 * 关键差异：localStorage 只能存字符串，对象必须 JSON.stringify；读取失败要降级，不能让页面白屏。
 */

const STORAGE_KEY = "subscription-react/subs";

export function loadSubscriptions() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return null; // 第一次打开，没有数据
    const data = JSON.parse(raw);
    if (!Array.isArray(data)) throw new Error("数据不是数组");
    return data;
  } catch {
    // 数据损坏（用户手动改坏 / 旧格式）：降级到种子，给抢救机会
    return null;
  }
}

export function saveSubscriptions(subs) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(subs));
}
