# Orbit SQL SQLite

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

## Documentation

The package-specific guides cover [architecture](docs/architecture/overview.md), [operations and security](docs/operations/README.md), and [development](docs/development/README.md), with [security guidance](docs/security/overview.md). The [documentation index](docs/README.md) links to the full package overview and project policies.

