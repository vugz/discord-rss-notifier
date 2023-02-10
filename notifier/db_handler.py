# Author: vugz @ GitHub
# Python 3.10.6

from __future__ import annotations
from typing import TYPE_CHECKING

import os

import aiosqlite
import datetime

if TYPE_CHECKING:
    from subscriber import Log

class DBHandler:
    async def initialize(self, table_name: str):
        self._db = await aiosqlite.connect(os.getenv("NOTIFIER_HOME") + "/resources/logs.db")
        self._cursor = await self._db.cursor()
        await self._cursor.execute(f"CREATE TABLE IF NOT EXISTS {self._sanitize(table_name)} (url TEXT NO NULL PRIMARY KEY, title TEXT, data TEXT, time TEXT)")
        await self._db.commit()
    
    async def is_log_in_db(self, table: str, log: Log):
        """ Check for Log in DB, INDEXED with link """
        await self._cursor.execute(f"SELECT url FROM {table} WHERE url=?;", (log.url,))
        return await self._cursor.fetchall()

    async def save_new_logs(self, table: str, logs: list[Log]):
        for log in logs:
            await self._cursor.execute(f"INSERT INTO {table} VALUES(?, ?, ?, ?)", (log.url, log.title, datetime.date.today(), datetime.datetime.now().strftime("%H:%M:%S")))
        await self._db.commit()
    
    async def close_session(self):
        await self._cursor.close()
        await self._db.close()

    def _sanitize(self, string: str) -> str:
        """ 
        Sanitize the table name
        e.g  '); drop table --' will turn into 'droptable' 
        """
        return "".join([chr for chr in string if chr.isalnum()])
 

