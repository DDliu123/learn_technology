import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import { defineConfig } from "vite";

// 部署到 GitHub Pages 子站：仓库站点根在 /docs，本应用挂在 /subscription-react/ 子路径。
// Pages 一个仓库只给一个站点源（根目录或 /docs），所以 React 应用只能做子目录，
// 不能像 Vercel 那样每个项目一个独立域名。base 必须和线上路径一致，否则 JS/CSS 路径 404。
const isProd = process.env.NODE_ENV === "production";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // 开发服务器跑在根路径（/），构建产物才用 Pages 子路径
  base: isProd ? "/learn_technology/subscription-react/" : "/",
  build: {
    // 构建直接输出到 Pages 发布目录，push 后自动上线（单一副本，避免 projects 与 docs 两份不同步）
    outDir: isProd ? "../../docs/subscription-react" : "dist",
    // outDir 在 root 之外，显式开启只清空该子目录，避免遗留旧 chunk
    emptyOutDir: true,
  },
});
