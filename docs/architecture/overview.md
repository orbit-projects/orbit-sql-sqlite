# Orbit SQL SQLite: architecture and boundaries

## Responsibility

`orbit-sql-sqlite` is the local SQLite provider for the `orbit-sql` capability. It uses Python's
standard-library `sqlite3` on a dedicated worker thread, so application calls do not block the
event loop. Core owns only the generic application lifecycle and resource container; SQLite and SQL
contracts are installed from this package chain.
`SQLiteDatabase` and `SQLiteAdapter` work without Core; `SQLitePlugin` is an optional lifecycle
integration imported from `orbit_sql_sqlite.plugin` and installed with the `[core]` extra.

```bash
pip install orbit-data orbit-sql orbit-sql-sqlite
# Add the Core lifecycle plugin only when the application uses it:
pip install 'orbit-sql-sqlite[core]'
```

`SQLitePlugin` registers a lazy resource at `orbit_sql.SQL_DATABASE_KEY`. It opens the connection
on first operation and Core closes it during application shutdown. Each database object is bound to
one event loop, serializes access on its worker, bounds result sizes and waits for submitted worker
operations before releasing transaction locks after cancellation. Use file-backed SQLite for
multi-connection applications; `:memory:` is scoped to one connection and one process. SQLite is
for development, local and embedded deployments; it is not a server database or shared distributed
store.

Standalone writes autocommit before `execute()` returns. `transaction()` opens an explicit SQLite
transaction and commits only after the body completes normally; errors and cancellation roll it
back after any already-submitted worker operation drains. A cancelled or failed commit may have an
unknown final outcome, so applications should reconcile before repeating non-idempotent writes.

```python
from orbit import Application, ApplicationConfig
from orbit_sql_sqlite import SQLiteConfig
from orbit_sql_sqlite.plugin import SQLitePlugin

app = Application(ApplicationConfig(name="notes"))
app.plugins.register(SQLitePlugin(SQLiteConfig(path="var/notes.sqlite")))
```

This package is alpha. Live deployment behavior depends on the host filesystem and SQLite
build. It supports Python 3.11 through 3.14.

Licensed under Apache-2.0.

## Declared dependencies

The following dependency declarations come from the checked-in manifests. Optional groups and development dependencies are called out separately.

### `pyproject.toml`
- `orbit-sql>=0.1.0a1,<0.2`
- Optional `core` extra: `orbit-core>=0.1.0a1,<0.2` for `SQLitePlugin`.
- Development dependencies: Core for plugin tests, plus pytest, pytest-asyncio, Ruff, and mypy.

Declared dependencies do not mean that optional providers or services are bundled with this package.

## Implementation layout

Representative implementation files in this checkout:

- `src/orbit_sql_sqlite/__init__.py`
- `src/orbit_sql_sqlite/adapter.py`
- `src/orbit_sql_sqlite/config.py`
- `src/orbit_sql_sqlite/database.py`
- `src/orbit_sql_sqlite/plugin.py`

## Public contract and scope

Each database instance owns one lazily opened `sqlite3.Connection` and one single-thread
`ThreadPoolExecutor`. The connection stays on its worker thread to satisfy SQLite thread affinity;
the async lock serializes every public operation and protects transaction scope. One instance is
bound to the first event loop that uses it and must be closed before that loop exits.

Statements outside `transaction()` use SQLite autocommit. A transaction acquires the instance lock,
issues an explicit `BEGIN`, and yields a facade restricted to the owning task. That facade avoids
reacquiring the lock while preventing another task from using the same connection inside the
transaction. Success commits; errors and cancellation roll back after any worker call already
submitted has completed. `aclose()` rejects later work, waits for the current operation, closes the
connection on its worker, and then shuts down the worker. Concurrent close calls share that cleanup;
after a failed close, a later call retries cleanup while keeping the resource unavailable to queries.

The adapter returns detached `SQLRow` values rather than exposing thread-affine cursors. It binds
Orbit's numbered `$1` parameters by name, converts dates/times/decimal/UUID values to portable text
representations, and does not parse or rewrite SQL. The SQL statement and parameter bounds are
resource controls, not a substitute for safe query construction: bind values and keep identifiers
fixed or allowlisted.

## Boundary rules

SQLite file permissions, directory ownership, backups, and filesystem reliability belong to the
deployment. This adapter does not provide encryption at rest, connection pooling, cross-process
coordination, replication, migration execution, or network access. Core owns the application
container lifecycle; the plugin registers this adapter as a managed `SQLDatabase` resource.
