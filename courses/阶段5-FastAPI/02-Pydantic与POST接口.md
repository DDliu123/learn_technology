# 阶段 5 · 第 2 课：Pydantic 与 POST /shorten 创建接口

> 项目：`projects/shortlink-api/`
> 本课产出：用 Pydantic 定义数据形状，写出 `POST /shorten` 真正创建短链，跑通 201 / 422 / 409
> 文件：`models.py`（数据形状）、`store.py`（内存存储）、`app.py`（路由）

---

## 1. 为什么用 Pydantic：请求/响应模型分开

前端发来的 JSON 和后端回的 JSON，字段往往不同。分开定义有两个好处：
- **校验**：进来的不对，直接拒（不用你手写 `if`）。
- **契约**：文档自动生成，调用方知道该传什么、会收到什么。

```python
class ShortenRequest(BaseModel):       # 请求：前端发什么
    url: AnyHttpUrl                    # 内置类型，自动校验「是不是合法 URL」
    code: str | None = None            # 可选自定义短码

class ShortLink(BaseModel):            # 响应：后端回什么
    code: str
    url: str
    created_at: str
```

`AnyHttpUrl` 是 Pydantic 内置类型：传 `"not-a-url"` 直接 422；传 `"https://x.com"` 会被规范成带方案的 URL。

---

## 2. 自定义校验：field_validator

内置类型管不了的规则，用装饰器写：

```python
@field_validator("code")
@classmethod
def code_must_be_alnum(cls, v: str | None) -> str | None:
    if v is not None and not v.isalnum():
        raise ValueError("自定义短码只能含字母和数字")
    return v
```

抛 `ValueError` → FastAPI 自动转成 **422**，错误信息原样带回去。

---

## 3. 存储层单独成模块（store.py）

```python
STORE: dict[str, ShortLink] = {}        # 内存表：code -> 短链

def create_link(req: ShortenRequest) -> ShortLink:
    if req.code is not None:
        if req.code in STORE:
            raise CodeTakenError(req.code)   # 自定义短码已存在，交给路由转 409
        code = req.code
    else:
        code = _generate_code()              # 随机 6 位（secrets，非 random）
    link = ShortLink(code=code, url=str(req.url), created_at=now_iso())
    STORE[code] = link
    return link
```

路由只调 `create_link`，不碰存储细节。**阶段 6 把 `STORE` 换成数据库，app.py 一行不用改** —— 这就是分层的好处。

---

## 4. 路由：POST /shorten

```python
@app.post("/shorten", response_model=ShortLink, status_code=status.HTTP_201_CREATED)
def shorten(req: ShortenRequest):
    try:
        return create_link(req)
    except CodeTakenError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="自定义短码已存在")
```

| 点 | 说明 |
|---|---|
| 参数 `req: ShortenRequest` | FastAPI 自动读 JSON body、按模型校验；失败直接 422，不到这行 |
| `status_code=201` | REST 约定「新建成功」用 201，不是默认 200 |
| `CodeTakenError → 409` | 自定义短码撞车是「冲突」，用 409 而不是 422 |

**状态码语义**（本课重点）：

| 码 | 含义 | 本课触发 |
|---|---|---|
| 200 | 成功（查询/返回） | GET /links |
| 201 | 已创建 | POST /shorten 成功 |
| 422 | 请求体校验失败 | url 不是 URL / code 含非法字符 |
| 409 | 冲突 | 自定义短码已存在 |

---

## 5. 本机踩坑

| 现象 | 解法 |
|---|---|
| 改了文件，新接口还是 404 | `fastapi dev` 热重载有时对「新增模块 + 改 import」不灵；**杀掉进程干净重启**即可（本课实测踩到） |
| `AnyHttpUrl` 把 `https://x.com` 变 `https://x.com/` | 正常规范化，存储和跳转都一致，别手动改回去 |
| `curl` 发 POST 必须带 `-H "Content-Type: application/json"` | 否则 FastAPI 按表单解析，422 |

---

## 6. 验证结果（curl）

```
POST /shorten {"url":"https://example.com/blog/post-1"}        → 201 {"code":"SpmAMR",...}
POST /shorten {"url":"...","code":"mynews"}                    → 201 {"code":"mynews",...}
GET  /links                                                  → 200 [两条]
POST /shorten {"url":"not-a-url"}                            → 422 url_parsing
POST /shorten {"url":"https://x.com","code":"a-b"}           → 422 自定义短码只能含字母和数字
POST /shorten {"url":"...","code":"mynews"}                  → 409 自定义短码已存在
```

`/docs` 里每个接口都能直接填 body 试，字段类型和示例由 Pydantic 自动生成。

---

## 7. 作业

1. 打开 `/docs`，用 `POST /shorten` 填一个你常去的网址，拿到短码。
2. 用同一个 `code` 再发一次，确认返回 409；换个不同 `code` 确认 201。
3. 故意把 `url` 写成 `ftp:/坏`，看 422 的 `detail` 里 `loc` 和 `msg` 长什么样（这就是前端做错误提示要解析的字段）。
4. **对照思考**：阶段 2 CLI 里你自己写 `if not url:` 校验；这里校验写在哪？谁帮你返回 422？

> 下一课：加 `GET /{code}` 重定向（307）+ 404 错误处理，`DELETE /{code}`（204），并用 FastAPI 的 `TestClient` 写「无浏览器」自动化测试。
