# 阶段 7 · 第 2 课：登录校验与 JWT 签发

> 项目：`projects/shortlink-api/`
> 本课产出：`POST /token` 校验密码并签发 JWT，客户端拿它访问受保护接口
> 文件：`auth.py`（`create_access_token` / `decode_token`）

---

## 1. 登录在做什么

1. 收到用户名 + 密码
2. 按用户名查出用户（查不到 → 失败）
3. 把提交的明文和库里的哈希 `checkpw` 比对（不一致 → 失败）
4. 都通过 → **签发一个 token**，之后客户端靠它证明身份

```python
user = get_user_by_credentials(username, password)
if user is None:
    raise HTTPException(401, "用户名或密码错误")
return {"access_token": create_access_token(user.username), "token_type": "bearer"}
```

**提示语故意不区分**「用户不存在」和「密码错」——统一返回同一句，
否则别人能用错误信息探测「哪些用户名已注册」。

---

## 2. 为什么用 JWT，而不是 session

| 方案 | 服务端要存什么 | 多台服务器时 |
|---|---|---|
| session | 每台机器记一份「session id → 用户」 | 要共享存储（Redis），否则换台机器就掉线 |
| **JWT** | **什么都不存** | 任意机器都能独立校验 ✅ |

JWT 把身份信息放进 token 本身，用**签名**保证改不了：

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9 . eyJzdWIiOiJhbGljZSIsImV4cCI6MTc2OTU... . 5rZ0f...
└─ header（算法）                      └─ payload（数据：sub/exp）              └─ signature（签名）
```

| 字段 | 含义 |
|---|---|
| `sub` | 这是谁（用户名） |
| `exp` | 过期时间，到点自动作废 |
| signature | 用密钥对前两段签名；**没有密钥改 payload 会导致验签失败** |

```python
def create_access_token(username: str, expires_delta=None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=60))
    return jwt.encode({"sub": username, "exp": expire}, SECRET_KEY, algorithm="HS256")

def decode_token(token: str) -> str | None:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"]).get("sub")
    except jwt.PyJWTError:
        return None        # 过期 / 签名不对 / 被篡改 → 一律 None
```

**签名不对 = 一律失败，不告诉对方具体原因**（避免泄露信息）。

---

## 3. 登录接口用表单，不是 JSON

```python
from fastapi.security import OAuth2PasswordRequestForm

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    ...
```

用 `application/x-www-form-urlencoded`（表单）是 **OAuth2 密码流的约定**。
好处：Swagger 右上角会出现 **锁图标**，填用户名密码登录后，
后续所有带锁的接口会自动带上 `Authorization: Bearer <token>` —— 不用手动复制 token。

```
curl -X POST http://127.0.0.1:8000/token -d "username=alice&password=secret123"
→ {"access_token":"eyJhbGci...","token_type":"bearer"}
```

---

## 4. 密钥管理（安全红线）

```python
SECRET_KEY = os.getenv("SHORTLINK_SECRET", "dev-only-secret-please-replace-...")
```

| 规则 | 原因 |
|---|---|
| 从**环境变量**读，不写死在代码里 | 代码会进 Git，密钥泄露 = 任何人都能伪造 token |
| 长度 ≥ 32 字节 | HS256 的建议下限；太短 PyJWT 会 `InsecureKeyLengthWarning`（本项目第一版就踩到，已加长默认值） |
| 生产环境必须换成随机值 | 例如 `openssl rand -hex 32` 生成 |

JWT **只是签名不是加密**：token 内容 base64 解码就能看到（别往 payload 里放密码、手机号）。
所以它必须走 HTTPS。

---

## 5. 验证结果

```
POST /token 密码错             → 401 用户名或密码错误
POST /token 正确               → 200 {"access_token":"eyJhbGci...","token_type":"bearer"}
POST /shorten 不带 token       → 401 Not authenticated
POST /shorten 带 token         → 201，owner 自动记为 alice
伪造 token                     → 401
```

---

## 6. 本机踩坑

| 现象 | 解法 |
|---|---|
| `InsecureKeyLengthWarning: HMAC key is 25 bytes` | 密钥太短；换 ≥32 字节（HS256 要求） |
| `/docs` 里没有锁图标 | 登录接口必须用 `OAuth2PasswordRequestForm`，且 `OAuth2PasswordBearer(tokenUrl="token")` 的 tokenUrl 要对上 |
| token 解码报 `AttributeError` | 把 `jwt.encode` 结果当 dict 用了；`encode` 返回字符串，`decode` 才返回 dict |

---

## 7. 作业

1. 打开 `/docs`，点右上角锁图标，用 alice 登录后，再点 `/links` 的 Try it out —— 观察请求头里自动带了 `Authorization`。
2. 把 token 粘到 <https://jwt.io> 看三段内容，确认 `sub` 和 `exp`（**不要在生产 token 上做这件事**）。
3. 等 token 过期（或把 `ACCESS_TOKEN_EXPIRE_MINUTES` 改成 1 分钟后重启），再请求 → 确认变 401。
4. **对照思考**：JWT 签发后**无法主动作废**（只能等过期）。如果要做「强制下线/改密后踢掉所有设备」，你会怎么设计？

> 下一课：**鉴权依赖与归属隔离** —— 用 `Depends(get_current_user)` 把「当前是谁」注入路由，让每个用户只能操作自己的短链。
