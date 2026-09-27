# 阶段 6 · 第 2 课：SQL 查询思维（where / order_by）与「Session 就是事务」

> 项目：`projects/shortlink-api/`
> 本课产出：`/links` 支持 `?search=` 模糊搜索与 `?sort=` 排序；用脚本证明事务回滚
> 新增文件：`tests/test_transaction.py`；改写：`store.py`、`app.py`

---

## 1. SQLModel 的查询是「拼装」出来的

```python
statement = select(ShortLink)                                    # SELECT * FROM short_link
if search:
    pattern = f"%{search}%"
    statement = statement.where(                                 # WHERE code LIKE ? OR url LIKE ?
        or_(ShortLink.code.like(pattern), ShortLink.url.like(pattern))
    )
statement = statement.order_by(ShortLink.created_at.desc())      # ORDER BY created_at DESC
return list(session.exec(statement).all())                       # 到这里才真正执行
```

| 方法 | 对应 SQL | 说明 |
|---|---|---|
| `select(Model)` | `SELECT * FROM 表` | 起点 |
| `.where(条件)` | `WHERE ...` | 过滤；`or_()` / `and_()` 组合多条件 |
| `.order_by(字段)` | `ORDER BY ...` | 排序；`.desc()` 倒序 |
| `.like("%x%")` | `LIKE '%x%'` | 模糊匹配 |
| `session.exec(语句)` | 执行 | **到这一步才发请求给数据库** |

**延迟执行**是关键：前面拼装怎么改都不碰数据库，最后 `exec` 才跑一次 SQL。
所以「按条件动态拼查询」很自然——有 search 才加 where，没有就不加，不用来回写两种查询。

---

## 2. 查询参数：函数参数不是路径参数，就变成 `?xxx=`

```python
@app.get("/links", response_model=list[ShortLink])
def links(search: str | None = None, sort: str = "created_at"):
    return list_links(search=search, sort=sort)
```

FastAPI 规则：路径里没写的参数 → 当作 URL 查询参数。
于是 `GET /links?search=bili&sort=url` 自动把值传进函数，Swagger 里也会列出来、可交互试。

---

## 3. Session 就是事务：失败会整体回滚

`with Session(engine) as session:` 不只是「连接」，它包着一次**事务**：

| 情况 | 结果 |
|---|---|
| 正常走到底 + `commit()` | 写入磁盘 |
| 中途抛异常（没 commit） | **全部撤销**，`with` 退出时自动回滚 |
| 已经 `commit()` 的部分 | 不会回滚——commit 是分水岭 |

`tests/test_transaction.py` 把这三种都跑了一遍并断言：

```
① 两条一起 add、中途抛错 → 一条都没进去        ✅ 整体回滚
② 正常 commit            → 落盘              ✅
③ 先 commit 一条、再炸   → 已提交的留下，后来的回滚 ✅
TRANSACTION TESTS PASSED ✅
```

**这为什么重要**：假设创建短链时要写「短链 + 默认统计记录」两张表，
中间任何一步失败，如果没有事务，就会留下「有短链没统计」的脏数据。

---

## 4. 本机踩坑

| 现象 | 解法 |
|---|---|
| 改了查询逻辑，`?search=` 仍返回全部 | `fastapi dev` 热重载第三次不灵；**杀进程干净重启**（阶段 5 就踩过，本次又踩到） |
| `session.get()` 查不到想要的 | 它只按主键查；按业务字段查用 `select + where` |
| 想看实际执行的 SQL | `create_engine(url, echo=True)`，每条 SQL 打到日志 |

---

## 5. 验证结果

```
GET /links（默认 created_at 倒序）  → apple / zhihu / bilibili / mynews / example
GET /links?search=bili             → 只 1 条 bilibili ✅
GET /links?sort=url                → 按网址升序（apple→bilibili→example→news→zhihu）✅
GET /links?search=mynews           → 按短码匹配命中 ✅
uv run python tests/test_transaction.py → TRANSACTION TESTS PASSED ✅
```

---

## 6. 作业

1. `/docs` 里点开 `GET /links`，填 `search` 和 `sort` 试，看 FastAPI 把你填的值拼成了什么 URL。
2. 给 `?sort=` 加一个新选项（比如按 `id`），体会「加一个 elif 分支」就是加一种排序。
3. 跑 `uv run python tests/test_transaction.py`，把 ① 里的 `raise` 挪到 `session.commit()` 之后，看断言怎么变化。
4. **对照思考**：阶段 3 用 JS 数组做筛选（`.filter()` / `.sort()`）是在**内存里**做；现在 `.where()` / `.order_by()` 是在**数据库里**做。数据量 100 万条时差别是什么？

> 下一课：**访问统计** —— 建 `Visit` 表，每次跳转记一条，加 `GET /{code}/stats` 看点击数；并讲清 `create_all` 与「迁移（Alembic）」的区别。
