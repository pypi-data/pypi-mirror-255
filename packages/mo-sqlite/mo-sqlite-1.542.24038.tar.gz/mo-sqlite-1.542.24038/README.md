# More SQLite!

Multithreading for Sqlite, plus expression composition

## Multi-threaded Sqlite

This module wraps the `sqlite3.connection` with thread-safe traffic manager.  Here is typical usage: 

    from mo_sqlite import Sqlite
    db = Sqlite("mydb.sqlite")
    with db.transaction() as t:
        t.command("insert into mytable values (1, 2, 3)")

While you may have each thread own a `sqlite3.connection` to the same file, you will still get exceptions when another thread has the file locked.

## Pull JSON out of database

This module includes a minimum experimental structure that can describe pulling deeply nested JSON documents out of a normalized database.  The tactic is to shape a single query who's resultset can be easily converted to the desired JSON by Python. Read more on [pulling json from a database](docs/JSON%20in%20Database.md)

There are multiple normal forms, including domain key normal form, and columnar form;  these have a multitude one-to-one relations, all represent the same logical schema, but differ in their access patterns to optimize for particular use cases.  This module intends to hide the particular database schema from the caller; exposing just the logical schema. 



This experiment compliments the [mo-columns](https://github.com/klahnakoski/mo-columns) experiment, which is about pushing JSON into a database. 
   