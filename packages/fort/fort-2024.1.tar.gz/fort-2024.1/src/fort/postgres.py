import logging
import psycopg2
import psycopg2.extras
import psycopg2.pool
import textwrap

from typing import Any, Dict, List, Optional


class PostgresDatabase:
    def __init__(self, dsn, minconn=1, maxconn=1):
        self.log = logging.getLogger(__name__)
        self.p = psycopg2.pool.ThreadedConnectionPool(minconn, maxconn, dsn, cursor_factory=psycopg2.extras.DictCursor)
        psycopg2.extras.register_uuid()

    def b(self, sql: str, records: List[Dict]):
        """Batch execute a query"""
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as cur:
                    self.log.debug(f'Batch query with {len(records)} parameter sets')
                    self.log.debug(textwrap.dedent(sql))
                    psycopg2.extras.execute_batch(cur, sql, records)
        finally:
            self.p.putconn(cnx)

    def q(self, sql: str, params: Dict = None) -> List[Dict]:
        """Execute a query and return all rows"""
        if params is None:
            params = {}
        result = []
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as c:
                    self.log.debug(textwrap.dedent(c.mogrify(sql, params).decode()))
                    c.execute(sql, params)
                    result = c.fetchall()
        finally:
            self.p.putconn(cnx)
            return result

    def q_one(self, sql: str, params: Dict = None) -> Optional[Dict]:
        """Execute a query and return the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r
        return None

    def q_val(self, sql: str, params: Dict = None) -> Any:
        """Execute a query and return the value in the first column of the first row, or None if there are no rows"""
        for r in self.q(sql, params):
            return r[0]
        return None

    def u(self, sql: str, params: Dict = None) -> int:
        """Execute a statement and return the number of rows affected"""
        if params is None:
            params = {}
        result = 0
        cnx = self.p.getconn()
        try:
            with cnx:
                with cnx.cursor() as c:
                    self.log.debug(textwrap.dedent(c.mogrify(sql, params).decode()))
                    c.execute(sql, params)
                    result = c.rowcount
        finally:
            self.p.putconn(cnx)
            return result
