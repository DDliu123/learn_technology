# 阶段 5 · 第 1 课：FastAPI 入门与第一个接口

> 项目：`projects/shortlink-api/`
> 本课产出：理解「后端 / API / REST」是什么，跑起第一个 FastAPI 服务，3 个接口返回正确 JSON
> 技术栈：Python 3.13 + **FastAPI** + uvicorn，包管理 **uv**（不写 pip / venv）

---

## 1. 后端、API、REST 到底是什么关系

| 词 | 一句人话 | 本项目的对应 |
|---|---|---|
| 后端 | 一直运行、管数据和规则的程序 | 这个 FastAPI 服务 |
| API | 前后端约定的「请求进去、响应出来」的接口 | `GET /links`、`POST /shorten` … |
| REST | 一套用 URL + HTTP 方法表达「对资源的增删改查」的约定 | 用 HTTP 方法区分意图（见下） |

前端（阶段 3/4 的 React）只管界面；数据存在哪、规则怎么算，归后端。两者通过 **HTTP** 对话：
前端发请求 → 后端返回 JSON。

**HTTP 方法即意图**（REST 核心约定）：

| 方法 | 含义 | 类比 |
|---|---|---|
| `GET` | 取数据，不改状态 | 查 |
| `POST` | 新建一条 | 增 |
| `PUT` / `PATCH` | 改一条 | 改 |
| `DELETE` | 删一条 | 删 |

---

## 2. FastAPI 怎么把一个函数变成接口

```python
from fastapi import FastAPI

app = FastAPI(title="短链接服务", version="0.1.0")

@app.get("/health")          # 装饰器：把这个函数绑到 GET /health
def health():
    return {"status": "ok"}  # 返回 dict → 自动变成 JSON 响应
```

| 行 | 作用 |
|---|---|
| `FastAPI(...)` | 创建应用实例；`title`/`version` 进 Swagger 文档 |
| `@app.get("/health")` | 路由装饰器：URL 路径 + HTTP 方法 |
| `return {...}` | FastAPI 自动序列化成 JSON，并加 `Content-Type: application/json` |

**为什么不用自己写 `json.dumps`**：FastAPI（底层 Starlette）自动处理序列化、状态码、响应头，还能按函数签名自动生成文档。

---

## 3. 项目结构（与阶段 2 的 CLI 同款 src 布局）

```
projects/shortlink-api/
├── pyproject.toml          uv 管理依赖（fastapi / uvicorn / httpx）
├── src/shortlink_api/
│   ├── __init__.py
│   ├── app.py              本课：app 实例 + 3 个路由
│   └── __main__.py         `uv run python -m shortlink_api` 启动入口
└── README.md
```

`STORE: dict[str, dict] = {}` 是**内存存储**：短码 → `{url, code}`。现在它是空的，服务重启即清空；阶段 6 换数据库。

---

## 4. 启动与验证

```bash
uv run fastapi dev src/shortlink_api/app.py --port 8000
# 等价于 uv run python -m shortlink_api
```

`fastapi dev` 自带热重载（改代码自动重启）和漂亮日志。启动后：

| 地址 | 看到什么 |
|---|---|
| `http://127.0.0.1:8000/` | `{"message":"短链接服务已启动","docs":"/docs"}` |
| `http://127.0.0.1:8000/health` | `{"status":"ok"}` |
| `http://127.0.0.1:8000/links` | `[]`（还没数据） |
| `http://127.0.0.1:8000/docs` | **Swagger 交互文档**，自动生成，可直接点试 |

> 验证请求用 `curl`（命令行），不依赖浏览器：
> `curl -s http://127.0.0.1:8000/health`

---

## 5. 本机踩坑

| 现象 | 解法 |
|---|---|
| `uv run fastapi` 命令不存在 | 只装 `fastapi` 不够；`uv add "fastapi[standard]"` 才会带上 uvicorn 和 fastapi-cli |
| 端口被占 `Address already in use` | 换 `--port 8001`，或结束占用进程 |
| 返回中文乱码 | FastAPI 默认 `ensure_ascii=False` 输出 UTF-8，正常不会；curl 乱码是终端编码问题，不影响接口 |

---

## 6. 验证结果

```
uv run fastapi dev  →  Uvicorn running on http://127.0.0.1:8000
GET /               →  {"message":"短链接服务已启动","docs":"/docs"}
GET /health         →  {"status":"ok"}
GET /links          →  []
/docs               →  200，Swagger 页面可交互
```

---

## 7. 作业

1. 跑 `uv run fastapi dev`，浏览器打开 `http://127.0.0.1:8000/docs`，点开 `/health` 的 "Try it out" → Execute，看响应。
2. 在 `app.py` 里给 `/` 的返回多加一个字段（如 `"time": "2026"`），保存后看终端是否自动重载，再 curl 验证。
3. **对照思考**：阶段 3 网页版数据存在 `localStorage`（浏览器里）；本课数据存在 `STORE`（服务器内存）。两者「谁刷新都不丢」吗？重启浏览器 vs 重启服务，结果分别是什么？

> 下一课：用 **Pydantic** 定义「短链」的数据形状，写 `POST /shorten` 真正创建一条短链（返回 201），并演示字段校验失败返回 422。
