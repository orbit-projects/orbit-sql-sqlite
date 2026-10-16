# Orbit SQL SQLite

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
on first operation and Core closes it during application shutdown. Each database object owns one
connection, is bound to one event loop, serializes access on its worker, bounds result sizes, and
waits for submitted worker operations before releasing transaction locks after cancellation.
Standalone writes commit before `execute()` returns; use `transaction()` for atomic multi-statement
work. Use a file-backed database when data must survive process shutdown; `:memory:` is scoped to
one connection and one process. SQLite suits local and embedded deployments, but is not a server
database or shared distributed store.

When registered as a Core plugin, Orbit CLI exposes a read-only **Check SQLite database**
operation. It opens a short-lived managed database, runs `SELECT 1`, and closes its worker
before reporting success. It does not create or mutate application tables.

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

## Documentation

The package-specific guides cover [architecture](docs/architecture/overview.md), [operations and security](docs/operations/README.md), and [development](docs/development/README.md), with [security guidance](docs/security/overview.md). The [documentation index](docs/README.md) links to the full package overview and project policies.

