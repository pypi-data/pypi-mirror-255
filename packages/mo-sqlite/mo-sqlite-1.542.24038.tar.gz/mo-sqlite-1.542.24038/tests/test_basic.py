# encoding: utf-8
#
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Contact: Kyle Lahnakoski (kyle@lahnakoski.com)
#
import re
from unittest import TestCase

from mo_sqlite import Sqlite
from mo_sqlite.expressions import Variable, SelectOp
from mo_sqlite.expressions.sql_alias_op import SqlAliasOp
from mo_sqlite.sql_script import SqlStep, SqlTree
from mo_threads import stop_main_thread
from tests.utils import add_error_reporting

whitespace = re.compile(r"\s+", re.MULTILINE)


@add_error_reporting
class TestBasic(TestCase):


    @classmethod
    def tearDownClass(cls):
        stop_main_thread()

    def test_one_nested_query(self):
        # FILL DATABASE WITH TWO TABLES, ONE WITH A FOREIGN KEY TO THE OTHER
        db = Sqlite()
        with db.transaction() as t:
            # create table of some people
            t.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)")
            t.execute("INSERT INTO people (name) VALUES ('kyle')")
            t.execute("INSERT INTO people (name) VALUES ('joe')")
            t.execute("INSERT INTO people (name) VALUES ('jane')")
            # create table of some pets, with foreign key to people
            t.execute("""CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT, _order INTEGER, owner INTEGER)""")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fido', 0, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('spot', 1, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fluffy', 0, 2)")

        people = SqlStep(
            None,
            SelectOp( Variable("people"), Variable("id"), Variable("name")),
            [SqlAliasOp("name", Variable("name"))],
            uids=(Variable("id"),),
            order=(),
        )
        pets = SqlStep(
            people,
            SelectOp(Variable("pets"), Variable("id"), Variable("name"), Variable("_order"), Variable("owner")),
            [SqlAliasOp("pets.$A.name", Variable("name"))],
            uids=(Variable("owner"), Variable("id")),
            order=(Variable("_order"),),
        )

        sql = SqlTree([pets]).to_sql()
        result = db.query(sql)

        expected = {
            "meta": {"format": "table"},
            "header": ["i0_0", "c0_0", "o1_0", "i1_0", "i1_1", "c1_0"],
            "data": [
                (1, "kyle", None, None, None, None),
                (1, None, 0, 1, 1, "fido"),
                (1, None, 1, 1, 2, "spot"),
                (2, "joe", None, None, None, None),
                (2, None, 0, 2, 3, "fluffy"),
                (3, "jane", None, None, None, None),
            ],
        }
        self.assertEqual(result, expected)

    def test_sister_nested_query(self):
        db = Sqlite()
        with db.transaction() as t:
            # create table of peopls
            t.execute("CREATE TABLE people (id INTEGER PRIMARY KEY, name TEXT)")
            t.execute("INSERT INTO people (name) VALUES ('kyle')")
            t.execute("INSERT INTO people (name) VALUES ('joe')")
            t.execute("INSERT INTO people (name) VALUES ('jane')")

            # create table of some pets, with foreign key to people
            t.execute("""CREATE TABLE pets (id INTEGER PRIMARY KEY, name TEXT, _order INTEGER, owner INTEGER)""")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fido', 0, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('spot', 1, 1)")
            t.execute("INSERT INTO pets (name, _order, owner) VALUES ('fluffy', 0, 2)")

            # create table of albums with foreign key to people
            t.execute("CREATE TABLE albums (id INTEGER PRIMARY KEY, cover TEXT, owner INTEGER)")
            t.execute("INSERT INTO albums (cover, owner) VALUES ('dark side of the moon', 3)")
            t.execute("INSERT INTO albums (cover, owner) VALUES ('thriller', 3)")
            t.execute("INSERT INTO albums (cover, owner) VALUES ('huey lewis and the news', 3)")

        people = SqlStep(
            None,
            SelectOp(Variable("people"), Variable("id"), Variable("name")),
            [SqlAliasOp("name", Variable("name"))],
            uids=(Variable("id"),),
            order=(),
        )
        pets = SqlStep(
            people,
            SelectOp(Variable("pets"), Variable("id"), Variable("name"), Variable("_order"), Variable("owner")),
            [SqlAliasOp("pets.$A.name", Variable("name"))],
            uids=(Variable("owner"), Variable("id")),
            order=(Variable("_order"),),
        )
        albums = SqlStep(
            people,
            SelectOp(Variable("albums"), Variable("id"), Variable("cover"), Variable("owner")),
            [SqlAliasOp("albums.$A.cover", Variable("cover"))],
            uids=(Variable("owner"), Variable("id")),
            order=(),
        )

        sql = SqlTree([pets, albums]).to_sql()
        result = db.query(sql)

        expected = {
            "meta": {"format": "table"},
            "header": ["i0_0", "c0_0", "o1_0", "i1_0", "i1_1", "c1_0", "i2_0", "i2_1", "c2_0"],
            "data": [
                (1, "kyle", None, None, None, None, None, None, None),
                (1, None, 0, 1, 1, "fido", None, None, None),
                (1, None, 1, 1, 2, "spot", None, None, None),
                (2, "joe", None, None, None, None, None, None, None),
                (2, None, 0, 2, 3, "fluffy", None, None, None),
                (3, "jane", None, None, None, None, None, None, None),
                (3, None, None, None, None, None, 3, 1, "dark side of the moon"),
                (3, None, None, None, None, None, 3, 2, "thriller"),
                (3, None, None, None, None, None, 3, 3, "huey lewis and the news"),
            ],
        }
        self.assertEqual(result, expected)


