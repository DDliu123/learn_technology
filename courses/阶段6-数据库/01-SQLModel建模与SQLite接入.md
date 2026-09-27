# 阶段 6 · 第 1 课：SQLModel 建模与 SQLite 接入（短链不再丢）

> 项目：`projects/shortlink-api/`
> 本课产出：把阶段 5 的**内存 dict**换成 **SQLite 数据库**，短链重启不丢
> 新增文件：`database.py`；改写：`models.py`、`store.py`、`app.py`
> 技术栈：Python + **SQLModel**（Pydantic + SQLAlchemy 二合一）+ SQLite，`uv add sqlmodel`

---

## 1. 为什么必须换掉内存 dict

阶段 5 的 `STORE: dict` 有三个致命短板：

| 短板 | 后果 |
|---|---|
| 存进程内存 | 服务一重启，短链**全没了** |
| 不能共享 | 开多个进程/部署多份实例时，数据各自一份，对不上 |
| 不好查 | 只能遍历；没法「按条件筛选 / 排序 / 统计」 |

数据库解决的就是这三件事：**持久化落盘 + 多实例共享 + 用 SQL 查询**。

---

## 2. SQLModel：一个类，既是校验模型又是数据库表

```python
class ShortenRequest(SQLModel):          # 只做校验，不是表
    url: AnyHttpUrl
    code: Optional[str] = None

class ShortLink(SQLModel, table=True):   # table=True → 同时是数据库表 + 接口响应模型
    __tablename__ = "short_link"
    id: Optional[int] = Field(default=None, primary_key=True)
    code: str = Field(index=True, unique=True)
    url: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
```

| 写法 | 含义 |
|---|---|
| `SQLModel` | 只有 Pydantic 能力（校验/序列化），当请求体用 |
| `SQLModel, table=True` | 额外成为数据库表，能增删查改 |
| `primary_key=True` | 主键，`Optional + default=None` 表示由数据库自增 |
| `unique=True` | 唯一约束——这是 409「短码重复」在数据库层的兜底 |
| `default_factory` | 入库时自动填，不用调用方传（比写死默认值安全） |

**不需要再写一遍响应模型**：`ShortLink` 直接当 `response_model`，序列化照样工作。

---

## 3. 引擎与建表（database.py）

```python
DATABASE_URL = os.getenv("SHORTLINK_DB_URL", "sqlite:///./shortlink.db")
engine = create_engine(DATABASE_URL, echo=False)   # echo=True 会打印每条 SQL，调试好用

def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)           # 按模型建表，幂等
```

`sqlite:///./shortlink.db` 是**文件型**库（落盘持久）；内存库是 `sqlite://`（重启即丢，只适合测试）。

启动时建表 —— FastAPI 推荐用 `lifespan`（替代旧的 `@app.on_event("startup")`）：

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="短链接服务", version="0.1.0", lifespan=lifespan)
```

---

## 4. 用 Session 做增删查改（store.py）

`Session` = 一次数据库会话（也是一次事务），用 `with` 自动收尾：

```python
def create_link(req: ShortenRequest) -> ShortLink:
    with Session(engine) as session:
        link = ShortLink(code=code, url=str(req.url))
        session.add(link)
        session.commit()      # 提交，真正写入磁盘
        session.refresh(link) # 把数据库生成的 id / created_at 回填到对象
        return link
```

| 操作 | 写法 |
|---|---|
| 新增 | `session.add(obj)` → `commit()` |
| 按条件查一条 | `session.exec(select(ShortLink).where(ShortLink.code == code)).first()` |
| 查全部 | `session.exec(select(ShortLink)).all()` |
| 删除 | `session.delete(obj)` → `commit()` |

**分层价值兑现**：`create_link / get_link / list_links / delete_link` 函数签名一个没变，
`app.py` 的路由**一行都没改**，就把存储从内存换成了数据库。

---

## 5. 本机踩坑

| 现象 | 解法 |
|---|---|
| `session.get(ShortLink, code)` 查不到 | `session.get` 只按**主键**查；`code` 不是主键，要用 `select + where` |
| 响应里 `id` 是 null | 忘了 `session.refresh(obj)`，数据库生成的默认值没回填 |
| 测试把开发库搞脏 | 测试前设 `SHORTLINK_DB_URL` 指向临时库，**且必须在 import app 之前设**（engine 导入时就建好了） |
| `create_all` 加了字段却不生效 | `create_all` 只建表不改结构；改结构要靠迁移（第 3 课讲） |

---

## 6. 验证结果

```
POST /shorten x2              → 201（id=1 NOdvPX / id=2 mynews）
sqlite3 查 short_link 表       → 2 行，created_at 已自动填
重启服务后 GET /links          → 仍有 2 条 ✅（阶段 5 这点做不到）
重启后 GET /mynews             → 307 + Location
重复 code                     → 409
uv run python tests/test_api.py → ALL TESTS PASSED ✅（独立测试库）
```

直接用 sqlite 命令行/脚本验数据，是最直观的「真的存进去了」的证明：

```python
import sqlite3
c = sqlite3.connect("shortlink.db")
print([r[0] for r in c.execute("select name from sqlite_master where type='table'")])
```

---

## 7. 作业

1. `uv run fastapi dev` 起来，建 2 条短链，**重启服务**再 `GET /links` —— 确认数据还在（对照阶段 5 会丢）。
2. 用 sqlite 脚本查 `short_link` 表，看 `id / code / url / created_at` 四列，理解「表 = 类」。
3. 故意往 `models.py` 再加一个字段（如 `note: str = ""`），重启服务 —— 观察 `create_all` 会不会给老表加列（答案：不会，这就是迁移要解决的问题）。
4. **对照思考**：阶段 5 判重靠遍历 dict；现在靠 `where` 查询 + `unique` 约束。数据量 100 万条时，两者差别在哪？

> 下一课：**SQL 查询思维** —— 用 `select / where / order_by` 给 `/links` 加搜索与排序，理解 Session 即事务。
