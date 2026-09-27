# PROJECT.md

> 给 AI 读的项目说明。每次让 AI 写代码前，先让它读这个文件。
> 结构、技术栈、约定有变化时必须更新本文件。

## 项目

一名 AI 产品经理的软件开发学习仓库，产出可运行产品 + 公开笔记。
当前阶段：**阶段 4（React）进行中**。

## 技术栈

| 层      | 选型                        | 备注                     |
| ------ | ------------------------- | ---------------------- |
| 前端     | HTML/CSS → JavaScript → **React 19 + Vite** → Tailwind | 浏览器只跑 JS，Python 不可替代前端 |
| 后端     | **Python 3.13 + FastAPI** | 类型提示即校验                |
| 包管理    | **uv**                    | 已取代 pip，禁止手写 venv      |
| 运行时     | **Node.js**（可选）         | 跑前端构建工具；纯静态页不一定需要 |
| 数据库    | PostgreSQL（Supabase/Neon）+ SQLModel | 阶段 6 引入        |
| 部署     | 前端 Vercel；后端 Render/Railway | 阶段 9 引入              |
| 移动端    | 微信小程序（调 HTTP 接口）          | 阶段 10 引入               |

## 目录约定

```
docs/                       GitHub Pages 发布目录，每次 push 后自动更新
├── index.html              教程站首页（含 Demo 区块）
└── subscription/           阶段 3：网页版订阅管家（既是源码也是线上页面）
└── subscription-react/     阶段 4：React 版构建产物（由 projects/subscription-react 的 npm run build 生成）
projects/                   不需要发布页面的项目源码
├── subscription-cli/       阶段 2：Python CLI 版订阅管家（uv 管理）
└── subscription-react/     阶段 4：React 版，需 build，产物为 dist/（不入库）
articles/                   公开笔记稿（md + 配图，用户自维护）
README.md                   对外说明：在做什么、路线、进度
PROJECT.md          本文件：给 AI 的项目上下文
学习路线-总览.md        阶段地图与 AI 协作原则
courses/阶段N-名称/    每课课件 md
scratch/            临时练习，不入 git
```

站点地址：<https://ddliu123.github.io/learn_technology/>
Demo —— 网页版订阅管家（原生 JS）：<https://ddliu123.github.io/learn_technology/subscription/>
Demo —— 订阅管家 v2（React）：<https://ddliu123.github.io/learn_technology/subscription-react/>

新网页要上线：Pages 一个仓库只给一个站点，来源只能是根目录或 /docs，所以新页面一律放 `docs/<子目录>/`，
禁止「源码一份 + docs 里再复制一份」——两边迟早不同步。

## 命令约定

```bash
uv init <项目名> --app --vcs none   # 建项目；外层已有仓库时加 --vcs none（旧参数 --no-git 已废弃）
uv run <命令>                        # 跑代码（自动管虚拟环境）
uv add/remove <包名>                 # 增删依赖
node <脚本>.js                       # 跑 JS：也可套一层假 DOM，测试浏览器里的纯计算逻辑
node <脚本>.mjs                      # ESM 脚本：React 组件可用 vite ssrLoadModule + renderToStaticMarkup 无浏览器渲染测试
npm install / npm run dev / build    # 前端项目；npm 缓存目录已改到 ~/.npm-cache（见下）
git add -A && git commit -m "类型: 说明"   # 每完成一个可运行功能就提交
```

提交类型只用：`init` `feat` `fix` `docs` `refactor` `chore`。

## 本机环境备注

- Node 装在 `C:\SoftWare\nodejs`，默认缓存目录无写权限 → 已建议 `npm config set cache "C:/Users/wise/.npm-cache"`；未设置时用环境变量 `npm_config_cache` 临时绕过。
- 一些网络请求（VS Code 插件市场等）会被本机代理的 TLS 中间证书拦截，报 `Cert does not contain a DNS name`，必要时需手动安装。

## 给 AI 的规则

1. 先讲方案再写代码；代码产出后逐行解释关键行。
2. 明确语言边界：「这是 Python + uv，不用 pip」/「这是 React + Tailwind，不引组件库」。
3. 报错先解释原因，再给修复，不要只丢一段代码。
4. 不确定就问，不要用猜测的 API 糊弄。
5. 改了结构/技术栈，提醒我更新 PROJECT.md。
