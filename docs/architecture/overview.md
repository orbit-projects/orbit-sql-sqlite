# Orbit SQL SQLite: architecture and boundaries

## Responsibility

`orbit-sql-sqlite` is the local SQLite provider for the `orbit-sql` capability. It uses Python's
standard-library `sqlite3` on a dedicated worker thread, so application calls do not block the
event loop. Core owns only the generic application lifecycle and resource container; SQLite and SQL
contracts are installed from this package chain.

```bash
pip install orbit-core orbit-data orbit-sql orbit-sql-sqlite
```

`SQLitePlugin` registers a lazy resource at `orbit_sql.SQL_DATABASE_KEY`. It opens the connection
on first operation and Core closes it during application shutdown. Each database object is bound to
one event loop, serializes access on its worker, bounds result sizes and waits for submitted worker
operations before releasing transaction locks after cancellation. Use file-backed SQLite for
multi-connection applications; `:memory:` is scoped to one connection and one process. SQLite is
for development, local and embedded deployments; it is not a server database or shared distributed
store.

```python
from orbit import Application, ApplicationConfig
from orbit_sql_sqlite import SQLiteConfig, SQLitePlugin

app = Application(ApplicationConfig(name="notes"))
app.plugins.register(SQLitePlugin(SQLiteConfig(path="var/notes.sqlite")))
```

This package is pre-alpha. Live deployment behavior depends on the host filesystem and SQLite
build. It supports Python 3.11 through 3.14.

Licensed under Apache-2.0.

## Declared dependencies

The following dependency declarations come from the checked-in manifests. Optional groups and development dependencies are called out separately.

### `pyproject.toml`
- `orbit-core>=0.1.0a1,<0.2`
- `orbit-sql>=0.1.0a1,<0.2`
- Optional `dev` group: `pytest>=8,<10`, `pytest-asyncio>=0.24,<2`, `ruff>=0.8,<1`, `mypy>=1.13,<2`.

Declared dependencies do not mean that optional providers or services are bundled with this package.

## Implementation layout

Representative implementation files in this checkout:

- `src/orbit_sql_sqlite/__init__.py`
- `src/orbit_sql_sqlite/adapter.py`
- `src/orbit_sql_sqlite/config.py`
- `src/orbit_sql_sqlite/database.py`
- `src/orbit_sql_sqlite/plugin.py`

## Public contract and scope

The README does not contain a separately headed architecture section. Its responsibility statement above and the public source files define the implemented scope; this guide adds no behavior beyond that description.

## Boundary rules

Keep provider SDKs, credentials, transports, and provider-specific error translation in provider adapters. Keep reusable capability contracts in the matching capability package and lifecycle orchestration in Core. Apply the relevant layer for this repository and preserve the dependency direction shown above.
