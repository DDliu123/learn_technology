# PROJECT.md

> 给 AI 读的项目说明。每次让 AI 写代码前，先让它读这个文件。
> 结构、技术栈、约定有变化时必须更新本文件。

## 项目

一名 AI 产品经理的软件开发学习仓库，产出可运行产品 + 公开笔记。
当前阶段：**阶段 0（工具与工作流）**。

## 技术栈

| 层      | 选型                        | 备注                     |
| ------ | ------------------------- | ---------------------- |
| 前端     | HTML/CSS → JavaScript → React + Tailwind | 浏览器只跑 JS，Python 不可替代前端 |
| 后端     | **Python 3.13 + FastAPI** | 类型提示即校验                |
| 包管理    | **uv**                    | 已取代 pip，禁止手写 venv      |
| 数据库    | PostgreSQL（Supabase/Neon）+ SQLModel | 阶段 6 引入        |
| 部署     | 前端 Vercel；后端 Render/Railway | 阶段 9 引入              |
| 移动端    | 微信小程序（调 HTTP 接口）          | 阶段 10 引入               |

## 目录约定

```
README.md           对外说明：在做什么、路线、进度
PROJECT.md          本文件：给 AI 的项目上下文
学习路线-总览.md        阶段地图与 AI 协作原则
courses/阶段N-名称/    课件 md + 该阶段练习代码
scratch/            临时练习，不入 git
```

## 命令约定

```bash
uv init <项目名>     # 建项目；外层已有仓库时加 --no-git
uv run <命令>        # 跑代码（自动管虚拟环境）
uv add/remove <包名> # 增删依赖
git add -A && git commit -m "类型: 说明"   # 每完成一个可运行功能就提交
```

提交类型只用：`init` `feat` `fix` `docs` `refactor` `chore`。

## 给 AI 的规则

1. 先讲方案再写代码；代码产出后逐行解释关键行。
2. 明确语言边界：「这是 Python + uv，不用 pip」/「这是 React + Tailwind，不引组件库」。
3. 报错先解释原因，再给修复，不要只丢一段代码。
4. 不确定就问，不要用猜测的 API 糊弄。
5. 改了结构/技术栈，提醒我更新 PROJECT.md。
