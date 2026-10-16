# Orbit SQL SQLite: security

SQLite stores application data in a local file. This adapter provides parameter binding,
bounded reads, sanitized driver errors, and one worker-owned connection; it does not encrypt the
database, authenticate operating-system users, or provide network transport security.

## Protect the database files

Run the application under a dedicated operating-system identity. Place the database in a
pre-provisioned directory with restrictive ownership and permissions, and ensure untrusted users
cannot replace the database path or its parent directory. SQLite may create journal sidecar files
beside the database while writes are in progress; treat the database and its directory contents as
one sensitive data boundary. Backups, snapshots, and exported copies need the same access controls.

SQLite does not encrypt data at rest by default. Use an appropriately encrypted filesystem or a
separately reviewed encryption extension when the threat model requires encryption. Protect
backups and removable media independently; file deletion is not a reliable secure-erasure method
on copy-on-write, journaled, or flash storage.

## Query and result handling

Bind values through `parameters` rather than interpolating them into SQL. Keep table and column
identifiers fixed or validate them against an allowlist; SQL placeholders bind values, not
identifiers. The adapter limits SQL text to 1 MB, positional parameters to 10,000, and fetched rows
to the requested limit (at most 10,000). It raises an explicit error when a result exceeds its
limit rather than silently truncating it.

Driver failures are translated to provider-neutral errors without SQL text or raw SQLite details.
Do not log parameter values or query results that contain sensitive information. A sanitized
exception does not prevent application code from logging the original statement or bound values.

## Deployment boundaries

The connection is process-local and serialized through a dedicated worker thread. A file-backed
database can be reopened by other processes, but this adapter does not coordinate application
instances, provide a connection pool, or guarantee safe behavior on network filesystems. Keep the
database on storage with reliable local locking and backup semantics. Use a server database for
multi-host writes, high write concurrency, replication, or centralized access control.

The `:memory:` database is private to this adapter's single connection and disappears at shutdown.
It is useful for isolated development and tests, not persistence. No credentials are stored by the
SQLite adapter itself; operating-system file access controls determine who can read the database.

For vulnerability reporting, follow the repository [security policy](../../SECURITY.md). Do not
publish exploitable details in public issues.
