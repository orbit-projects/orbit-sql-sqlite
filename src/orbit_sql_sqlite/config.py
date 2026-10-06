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
"""Validated local SQLite settings."""

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, StrictStr


class SQLiteConfig(BaseModel):
    """File-backed or in-memory SQLite settings; no connection opens during validation."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: StrictStr = Field(min_length=1, max_length=4_096)
    timeout: float = Field(default=5.0, gt=0, le=300, allow_inf_nan=False, strict=True)

    @property
    def database_path(self) -> str | Path:
        """Return the literal memory marker or a normalized filesystem path."""
        if self.path == ":memory:":
            return self.path
        return Path(self.path)


__all__ = ["SQLiteConfig"]
