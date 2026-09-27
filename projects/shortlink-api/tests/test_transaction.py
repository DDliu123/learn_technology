"""阶段 6 第 2 课：证明「Session 就是事务」——失败会整体回滚。

跑法：uv run python tests/test_transaction.py
用独立临时库，跑完不留痕迹（*.db 已 gitignore）。
"""
import os
from pathlib import Path

os.environ["SHORTLINK_DB_URL"] = "sqlite:///./test_tx.db"
Path("test_tx.db").unlink(missing_ok=True)

from sqlmodel import Session, select  # noqa: E402

from shortlink_api.database import create_db_and_tables, engine  # noqa: E402
from shortlink_api.models import ShortLink  # noqa: E402

create_db_and_tables()


def codes():
    """从数据库读出当前所有短码（脱离 Session 重新查，确保读的是磁盘真实状态）。"""
    with Session(engine) as session:
        return [link.code for link in session.exec(select(ShortLink)).all()]


def main():
    # ① 两条一起写，但中途炸掉（还没 commit）
    try:
        with Session(engine) as session:
            session.add(ShortLink(code="aaa", url="https://a.com", owner="tester"))
            session.add(ShortLink(code="bbb", url="https://b.com", owner="tester"))
            raise RuntimeError("模拟中途出错")
            session.commit()  # 永远执行不到
    except RuntimeError:
        pass
    # 断言：一条都没进去 → 事务整体回滚了
    assert "aaa" not in codes() and "bbb" not in codes()
    print("① 中途出错 → 全部回滚，库里干干净净 ✅")

    # ② 正常提交
    with Session(engine) as session:
        session.add(ShortLink(code="ccc", url="https://c.com", owner="tester"))
        session.commit()
    assert "ccc" in codes()
    print("② 正常 commit → 落盘 ✅")

    # ③ 先提交再出错：已提交的部分不会回滚（理解 commit 的分界线）
    try:
        with Session(engine) as session:
            session.add(ShortLink(code="ddd", url="https://d.com", owner="tester"))
            session.commit()  # 这一条已经落盘
            session.add(ShortLink(code="eee", url="https://e.com", owner="tester"))
            raise RuntimeError("提交后又炸了")
    except RuntimeError:
        pass
    now = codes()
    assert "ddd" in now and "eee" not in now
    print("③ commit 是分水岭：之前落盘、之后回滚 ✅")

    print(f"最终库里：{now}")
    print("TRANSACTION TESTS PASSED ✅")


if __name__ == "__main__":
    main()
