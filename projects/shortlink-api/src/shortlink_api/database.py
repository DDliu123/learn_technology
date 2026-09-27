"""阶段 6 第 1 课：数据库引擎与建表。

engine 是 SQLAlchemy 的「数据库连接池入口」。所有 Session 都从它创建。
为什么用文件型 SQLite（sqlite:///./shortlink.db）而不是内存：文件落盘，服务重启数据还在——
这正是阶段 5 内存 dict 最大的短板（一重启全没）。
"""
import os

from sqlmodel import SQLModel, create_engine

# 数据库地址。默认用项目根目录的 shortlink.db。
# 测试时通过环境变量换成临时库（见 tests/test_api.py），保证每次测试从空库开始。
DATABASE_URL = os.getenv("SHORTLINK_DB_URL", "sqlite:///./shortlink.db")

# SQLite 不需要账号密码，create_engine 即可。echo=True 会把每条 SQL 打到日志，调试期很方便。
engine = create_engine(DATABASE_URL, echo=False)


def create_db_and_tables() -> None:
    """按所有 table=True 的 SQLModel 建表。

    幂等：表已存在就跳过，不会重建。
    但它**不会改表结构**——比如以后给模型加字段，老表不会自动加列。
    生产环境用 Alembic 做「迁移」来解决这个问题（阶段 6 末会点一下）。
    """
    SQLModel.metadata.create_all(engine)
