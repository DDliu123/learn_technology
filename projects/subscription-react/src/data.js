/** 第 1 课：数据写死在这里。第 3 课会换成从 localStorage 读取。
 *  注意：组件里不能直接用这个数组当 state 的初始值去修改 —— 见 App.jsx 的 structuredClone。 */

export const SUBSCRIPTIONS = [
  { id: "seed-1", name: "Netflix", price: 68, category: "视频", nextBilling: "2026-10-01" },
  { id: "seed-2", name: "Spotify", price: 58, category: "音乐", nextBilling: "2026-10-05" },
  { id: "seed-3", name: "ChatGPT Plus", price: 145, category: "AI 工具", nextBilling: "2026-10-08" },
  { id: "seed-4", name: "Notion", price: 45, category: "效率工具", nextBilling: "2026-10-12" },
  { id: "seed-5", name: "iCloud", price: 21, category: "存储", nextBilling: "2026-10-20" },
];

/** crypto.randomUUID 依赖安全上下文（https 或 localhost），file:// 下没有，故留兜底 */
export function createId() {
  if (typeof crypto !== "undefined" && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return `id-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}
