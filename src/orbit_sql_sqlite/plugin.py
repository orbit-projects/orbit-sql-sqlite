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

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from orbit import Application
from orbit.plugins import Plugin, PluginMetadata
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


__all__ = ["SQLitePlugin"]
