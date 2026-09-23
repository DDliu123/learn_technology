# 阶段 0 · 第 2 课：VS Code 与 Git

目标：配好编辑器，掌握 Git 本地全流程（提交、比对、撤销）。时长约 1.5 小时。

---

## 1. VS Code 插件（本课已装）

| 插件                                  | 作用                     |
| ----------------------------------- | ---------------------- |
| Python + Pylance（自动带）               | Python 语法、补全、跳转定义      |
| Python Debugger                     | 断点调试                   |
| Ruff                                | 保存即格式化 + 查错（Python 标配） |
| Error Lens                          | 错误直接显示在代码行尾            |
| GitLens                             | 看每行代码是谁、哪次提交改的         |
| Even Bette&#x72;**&#x20;**&#x54;OML | `pyproject.toml` 高亮    |
| Chinese (Simplified)                | 中文界面                   |

前端阶段（阶段 1）再装：Prettier、ESLint、Tailwind CSS IntelliSense。

---

## 2. 关键设置（已写入用户 settings.json）

```jsonc
"editor.formatOnSave": true,                    // 保存即格式化
"files.autoSave": "afterDelay",                 // 自动保存
"files.eol": "\n",                              // 统一 LF
"terminal.integrated.defaultProfile.windows": "Git Bash",  // 终端用 Git Bash
"git.autofetch": true,                          // 自动拉取远端状态
"[python]": { "editor.defaultFormatter": "charliermarsh.ruff" }
```

打开方式：`Ctrl+Shift+P` → `Preferences: Open User Settings (JSON)`。

其他必会快捷键：`Ctrl+`` 开终端、`Ctrl+P` 搜文件、`Ctrl+Shift+F` 全局搜索、`F2\` 重命名。

---

## 3. Git：三个区

```
工作区（你编辑的文件）  →  暂存区（git add）  →  仓库（git commit）
        git restore  ←         git restore --staged  ←
```

| 命令                          | 作用             |
| --------------------------- | -------------- |
| `git init -b main`          | 建仓库（默认分支 main） |
| `git status`                | 看当前状态（最常用）     |
| `git add 文件` / `git add -A` | 加入暂存区          |
| `git commit -m "信息"`        | 提交到仓库          |
| `git log --oneline`         | 看提交历史          |
| `git diff`                  | 看**未暂存**的改动    |
| `git diff --staged`         | 看**已暂存**的改动    |
| `git restore 文件`            | 丢弃未提交的改动       |
| `git restore --staged 文件`   | 取消 add         |

---

## 4. 撤销的三档（重要）

| 场景          | 命令                        | 后果               |
| ----------- | ------------------------- | ---------------- |
| 改了文件，还没 add | `git restore 文件`          | 改动消失，回退到上次提交     |
| 已 add，还没提交  | `git restore --staged 文件` | 取消暂存，改动还在        |
| 已提交，想撤回     | `git reset --soft HEAD~1` | 回到上一次提交，改动保留在暂存区 |
| 已提交，确认丢弃    | `git reset --hard HEAD~1` | ⚠️ 改动彻底消失，慎用     |
| 已推送远端，要撤销   | `git revert <commit>`     | 生成一个"反做"提交，安全    |

原则：**未推送用 reset，已推送用 revert**。

---

## 5. 实操（已验证）

```bash
mkdir -p scratch/git-playground && cd scratch/git-playground
git init -b main
echo "# 学习笔记" > notes.md
git add notes.md && git commit -m "init: 创建学习笔记"   # 13cc48d
# 改文件后再提交
git add -A && git commit -m "docs: 补充三区概念"          # 76a83ed
git log --oneline
echo "临时乱写" >> notes.md && git restore notes.md      # 改动撤销，文件复原
```

---

## 6. 两个 Windows 专属坑

| 坑                                                | 处理                                                    |
| ------------------------------------------------ | ----------------------------------------------------- |
| 换行符：`LF will be replaced by CRLF` 警告，Linux 部署易出错 | 已设 `git config --global core.autocrlf input`（提交统一 LF） |
| 中文文件名/路径在部分 CLI 里乱码                              | 命令行用 Git Bash；脚本文件名尽量用英文                              |

已同步设置：`init.defaultBranch = main`（与 GitHub 默认一致）。

---

## 7. 提交信息规范

`<类型>: <一句话>`，类型只用这几个：

| 类型         | 用于      |
| ---------- | ------- |
| `init`     | 项目初始化   |
| `feat`     | 新功能     |
| `fix`      | 修 bug   |
| `docs`     | 文档      |
| `refactor` | 重构      |
| `chore`    | 依赖、配置杂项 |

规则：**每完成一个可运行的功能就 commit**，不要攒一堆。这是 AI 协作时代最重要的安全网——改崩了能立刻回到上一个能跑的版本。

---

## 8. 作业

1. 打开 VS Code，确认已装插件生效；按 \`Ctrl+\`\` 看终端是否为 Git Bash。
2. 在 `scratch/git-playground` 里再走一遍：改文件 → `git diff` → `git add` → 提交。
3. 故意改坏文件，用 `git restore` 救回来；再用 `git reset --soft HEAD~1` 撤回一次提交。

下一课：建立第一个真实仓库（README + PROJECT.md + .gitignore）并推送到 GitHub。
