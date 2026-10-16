# Copyright 2026-present Orbit Contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Optional Core plugin wiring the standalone SQLite provider resource."""

from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from orbit import Application
from orbit.plugins import ControlAction, ControlResult, Plugin, PluginMetadata
from orbit_sql import SQL_DATABASE_KEY

from orbit_sql_sqlite.config import SQLiteConfig
from orbit_sql_sqlite.database import SQLiteDatabase


class SQLitePlugin(Plugin):
    """Register a lazy SQLite resource managed by Core's container lifecycle."""

    metadata = PluginMetadata(
        name="orbit-sql-sqlite",
        version="0.1.0a1",
        capabilities=frozenset({"database.sql.sqlite"}),
    )

    def __init__(self, config: SQLiteConfig) -> None:
        """Capture validated settings without opening a worker or connection."""
        if not isinstance(config, SQLiteConfig):
            raise TypeError("SQLitePlugin requires SQLiteConfig.")
        self._config = config
        self.control_actions = (
            ControlAction(
                id="check-connection",
                title="Check SQLite database",
                description="Run a read-only SELECT 1 and close the temporary database resource.",
                handler=self._check_connection,
            ),
        )

    def setup(self, application: Application) -> None:
        """Register a managed resource factory during plugin setup."""
        if not isinstance(application, Application):
            raise TypeError("SQLitePlugin requires an Orbit Application.")
        application.container.register_resource(SQL_DATABASE_KEY, lambda _: self._database())

    @asynccontextmanager
    async def _database(self) -> AsyncIterator[SQLiteDatabase]:
        """Create the local resource only when requested and close it at shutdown."""
        database = SQLiteDatabase(
            self._config.database_path,
            timeout=self._config.timeout,
        )
        try:
            yield database
        finally:
            await database.aclose()

    async def _check_connection(self, _: Mapping[str, object]) -> ControlResult:
        """Run a bounded, read-only local database check and release its worker."""
        database_path = self._config.database_path
        if database_path != ":memory:" and not Path(database_path).is_file():
            return ControlResult("SQLite database file does not exist.", succeeded=False)
        async with self._database() as database:
            await database.execute("PRAGMA query_only = ON")
            await database.fetch_one("SELECT 1")
        return ControlResult("SQLite database is reachable.")


__all__ = ["SQLitePlugin"]
