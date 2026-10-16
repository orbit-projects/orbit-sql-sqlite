# Orbit SQL SQLite: operations

`orbit-sql-sqlite` implements `orbit-sql` with Python's standard-library `sqlite3`. It owns one
connection and one dedicated worker thread per `SQLiteDatabase`; the connection opens lazily on the
first operation. It does not own a process pool or provide server-database coordination.

Install the Core runtime, SQL contract, and adapter explicitly:

```bash
python -m pip install orbit-data orbit-sql orbit-sql-sqlite
# Add the Core lifecycle plugin only when the application uses it:
python -m pip install 'orbit-sql-sqlite[core]'
```

## Configure the database resource

`SQLiteConfig` accepts a filesystem path or the exact `:memory:` marker. The path is interpreted
relative to the process working directory when it is relative. Use an absolute path for deployed
applications, create and permission its parent directory before startup, and ensure the service
user can create SQLite journal sidecar files there. This package does not create parent directories.

`timeout` defaults to five seconds and controls how long SQLite waits for a conflicting file lock.
It must be greater than zero and no more than 300 seconds. The wait occurs on the database's single
worker thread; a long timeout can block all operations queued on that instance. Set it based on the
application's write contention and request budget.

```python
from orbit import Application, ApplicationConfig
from orbit_sql_sqlite import SQLiteConfig
from orbit_sql_sqlite.plugin import SQLitePlugin

app = Application(ApplicationConfig(name="notes"))
app.plugins.register(SQLitePlugin(SQLiteConfig(path="/var/lib/notes/notes.sqlite", timeout=5.0)))
```

The plugin registers `SQL_DATABASE_KEY` as a lazy Core-managed resource. Resolve it after startup;
Core closes the resource during shutdown. When using `SQLiteAdapter` directly through the SQL
registry, explicitly call `aclose()` in the application's cleanup path or manage the database with
its async context manager. Concurrent close callers share one cleanup attempt. If a driver or
worker shutdown error makes that attempt fail, call `aclose()` again after addressing the cause;
the failed attempt leaves the resource closed to new queries and retains the worker when it is
needed to retry closing the connection.

## Write and transaction behavior

Standalone writes through `database.execute()` are committed before the call returns. Use
`async with database.transaction()` when several statements must commit or roll back together. A
normal body exit commits. An exception or task cancellation rolls back after submitted synchronous
SQLite work has drained from the worker thread.

Cancellation during commit cannot undo a commit that already succeeded. If the caller observes
cancellation or a connection error at that point, reconcile the write before retrying a
non-idempotent operation. Use an application request ID or other deduplication key where retries
can otherwise create duplicate effects.

The connection runs with foreign-key enforcement enabled. Result reads are bounded: `fetch_all`
raises a provider-neutral error if it finds more rows than its requested limit instead of silently
truncating. Query text and parameter counts also have hard limits; use bound positional parameters
for values and fixed or allowlisted identifiers.

## Choose the deployment boundary

A file-backed database persists across process restarts and can be opened by other local processes,
subject to SQLite locking and filesystem behavior. Each Orbit database object still owns its own
connection; this adapter does not pool or coordinate those connections. Keep the file on reliable
local storage. Use a server database for multi-host writes, high write concurrency, replication, or
centralized access control.

`:memory:` is private to one SQLite connection and disappears when that database resource closes.
It is appropriate for isolated tests and ephemeral local work. SQLite remains useful in embedded
production deployments with modest, local workloads; validate locking, backup, restore, and disk
failure behavior for the actual filesystem before release.

## Release validation

The local suite verifies transaction cleanup, cancellation draining, persistence, parameter
binding, result limits, safe errors, and Core resource shutdown. It does not validate backup/restore,
power-loss behavior, filesystem permissions, multi-process contention, network filesystems, or a
production host. Review those deployment-specific properties separately.
