"""Thin per-engine connectors: run SQL, time it, and capture optimizer plans.

Each connector exposes the same small interface so the runner never branches on
engine:

    run(sql)              -> number of rows fetched (all rows are fetched)
    execute(sql)          -> run a statement and discard any result
    estimated_plan(sql)   -> (format, text) without executing the query
    actual_plan(sql)      -> (format, text) after executing it with runtime stats
    version()             -> server version string
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class ConnSettings:
    host: str
    port: int
    user: str
    password: str
    database: str

    @classmethod
    def from_env(cls, engine: str) -> "ConnSettings":
        p = engine.upper()
        defaults = {
            "mysql": ("127.0.0.1", 3306, "root", "tpch_Pass1", "tpch"),
            "mssql": ("127.0.0.1", 1433, "sa", "tpch_Pass1", "tpch"),
        }[engine]
        return cls(
            host=os.environ.get(f"{p}_HOST", defaults[0]),
            port=int(os.environ.get(f"{p}_PORT", defaults[1])),
            user=os.environ.get(f"{p}_USER", defaults[2]),
            password=os.environ.get(f"{p}_PASSWORD", defaults[3]),
            database=os.environ.get(f"{p}_DB", defaults[4]),
        )


class MySQL:
    name = "mysql"

    def __init__(self, s: ConnSettings, database: bool = True):
        import mysql.connector  # imported lazily so tests run without drivers

        self.conn = mysql.connector.connect(
            host=s.host, port=s.port, user=s.user, password=s.password,
            database=s.database if database else None,
            allow_local_infile=True, autocommit=True,
        )
        self._json_v2 = self._try("SET SESSION explain_json_format_version = 2")

    def _try(self, sql: str) -> bool:
        try:
            self.execute(sql)
            return True
        except Exception:
            return False

    def execute(self, sql: str) -> None:
        cur = self.conn.cursor()
        cur.execute(sql)
        if cur.with_rows:
            cur.fetchall()
        cur.close()

    def run(self, sql: str) -> int:
        cur = self.conn.cursor()
        cur.execute(sql)
        n = len(cur.fetchall())
        cur.close()
        return n

    def _scalar(self, sql: str) -> str:
        cur = self.conn.cursor()
        cur.execute(sql)
        row = cur.fetchone()
        cur.fetchall()
        cur.close()
        return row[0]

    def version(self) -> str:
        return self._scalar("SELECT VERSION()")

    def estimated_plan(self, sql: str) -> tuple[str, str]:
        return "json", self._scalar(f"EXPLAIN FORMAT=JSON {sql}")

    def actual_plan(self, sql: str) -> tuple[str, str]:
        # EXPLAIN ANALYZE FORMAT=JSON needs 8.3+ with JSON format version 2;
        # older servers only offer the TREE text form.
        if self._json_v2:
            try:
                return "json", self._scalar(f"EXPLAIN ANALYZE FORMAT=JSON {sql}")
            except Exception:
                pass
        return "tree", self._scalar(f"EXPLAIN ANALYZE {sql}")

    def close(self) -> None:
        self.conn.close()


class MSSQL:
    name = "mssql"

    def __init__(self, s: ConnSettings, database: bool = True):
        import pymssql  # imported lazily so tests run without drivers

        self.conn = pymssql.connect(
            server=s.host, port=s.port, user=s.user, password=s.password,
            database=s.database if database else "master", autocommit=True,
        )

    def execute(self, sql: str) -> None:
        cur = self.conn.cursor()
        cur.execute(sql)
        while True:
            if cur.description:
                cur.fetchall()
            if not cur.nextset():
                break
        cur.close()

    def run(self, sql: str) -> int:
        cur = self.conn.cursor()
        cur.execute(sql)
        n = len(cur.fetchall())
        while cur.nextset():
            if cur.description:
                cur.fetchall()
        cur.close()
        return n

    def version(self) -> str:
        cur = self.conn.cursor()
        cur.execute("SELECT CAST(SERVERPROPERTY('ProductVersion') AS VARCHAR(64)), "
                    "CAST(SERVERPROPERTY('Edition') AS VARCHAR(128))")
        v, ed = cur.fetchone()
        cur.close()
        return f"{v} ({ed})"

    def estimated_plan(self, sql: str) -> tuple[str, str]:
        # SHOWPLAN_XML must be the only statement in its batch. While it is on,
        # the query is compiled but not executed and the plan is the result.
        cur = self.conn.cursor()
        cur.execute("SET SHOWPLAN_XML ON")
        try:
            cur.execute(sql)
            xml = cur.fetchone()[0]
            while cur.nextset():
                pass
        finally:
            cur.execute("SET SHOWPLAN_XML OFF")
            cur.close()
        return "xml", _to_text(xml)

    def actual_plan(self, sql: str) -> tuple[str, str]:
        # STATISTICS XML executes the query; the plan arrives as an extra
        # result set after the query's own rows.
        cur = self.conn.cursor()
        cur.execute("SET STATISTICS XML ON")
        xml = None
        try:
            cur.execute(sql)
            while True:
                if cur.description:
                    rows = cur.fetchall()
                    col = cur.description[0][0] or ""
                    if "Showplan" in col and rows:
                        xml = rows[0][0]
                if not cur.nextset():
                    break
        finally:
            cur.execute("SET STATISTICS XML OFF")
            cur.close()
        if xml is None:
            raise RuntimeError("SQL Server returned no STATISTICS XML plan")
        return "xml", _to_text(xml)

    def close(self) -> None:
        self.conn.close()


def _to_text(v) -> str:
    return v.decode("utf-16" if v[:2] in (b"\xff\xfe", b"\xfe\xff") else "utf-8") if isinstance(v, bytes) else v


def connect(engine: str, database: bool = True):
    s = ConnSettings.from_env(engine)
    return {"mysql": MySQL, "mssql": MSSQL}[engine](s, database=database)
