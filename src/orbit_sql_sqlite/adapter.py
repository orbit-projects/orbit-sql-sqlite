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
"""SQLite implementation of Orbit's SQL adapter contract."""

from orbit_sql import SQLAdapter
from pydantic import BaseModel

from orbit_sql_sqlite.config import SQLiteConfig
from orbit_sql_sqlite.database import SQLiteDatabase


class SQLiteAdapter:
    """Open a local SQLite database through explicit Orbit SQL adapter selection."""

    @property
    def name(self) -> str:
        """Return the stable SQL registry key."""
        return "sqlite"

    @property
    def configuration_model(self) -> type[BaseModel]:
        """Return the typed local database settings."""
        return SQLiteConfig

    async def connect(self, configuration: BaseModel) -> SQLiteDatabase:
        """Create a lazy SQLite resource from the explicit configuration."""
        if not isinstance(configuration, SQLiteConfig):
            raise TypeError("SQLiteAdapter requires SQLiteConfig.")
        return SQLiteDatabase(configuration.database_path, timeout=configuration.timeout)


assert isinstance(SQLiteAdapter(), SQLAdapter)

__all__ = ["SQLiteAdapter"]
