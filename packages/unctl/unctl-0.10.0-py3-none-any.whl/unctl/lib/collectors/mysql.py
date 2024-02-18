import aiomysql
import contextlib
from unctl.lib.collectors.base import DataCollector
from unctl.constants import CheckProviders


class MySQLData:
    def __init__(self, default_config_file):
        self._connection = None
        self.default_config_file = default_config_file

    async def get_dbname(self):
        # should be considered as a check namespace
        return (await self._get_connection())._db  # noqa

    async def get_max_connections(self):
        target = "max_connections"
        async with self._get_cursor() as cursor:
            await cursor.execute(f"SHOW VARIABLES LIKE '{target}';")
            result = await cursor.fetchone()
        return int(result[-1])

    async def get_connections_used(self):
        target = "Max_used_connections"
        async with self._get_cursor() as cursor:
            await cursor.execute(f"SHOW STATUS LIKE '{target}';")
            result = await cursor.fetchone()
        return int(result[-1])

    async def _get_connection(self):
        if self._connection is None:
            self._connection = await aiomysql.connect(
                read_default_file=self.default_config_file
            )
        return self._connection

    @contextlib.asynccontextmanager
    async def _get_cursor(self):
        conn = await self._get_connection()
        async with conn.cursor() as cursor:
            yield cursor


class MySQLDataCollector(DataCollector, name=CheckProviders.MySQL):
    DEFAULT_CONFIG_FILE = "~/.my.cnf"

    async def fetch_data(self):
        return MySQLData(self.DEFAULT_CONFIG_FILE)
