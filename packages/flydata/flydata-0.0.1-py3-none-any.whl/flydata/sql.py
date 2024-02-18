"""
Manipulate SQL databases.
"""
# from __future__ import annotations
import sqlite3 as _sql

def create(filename: str):
    """
    Wrapper for initializing a Database.
    """
    return Database(filename)

class EntryType:
    NULL = "NULL"
    NONE = NULL
    REAL = "REAL"
    FLOATINGPOINT = REAL
    TEXT = "TEXT"
    STRING = TEXT
    BLOB = "BLOB"
    FILE = BLOB

class Entry:
    _type: EntryType = EntryType.NULL
    _name: str = None
    def __init__(self, type: EntryType, name: str) -> None:
        """
        A table entry.
        """
        self._type = type
        self._name = name

class Database:
    """
    An SQLite database. To initialize in memory, use the :memory: string as a filename.
    """
    _connection: _sql.Connection = None
    _cursor: _sql.Cursor
    def __init__(self, filename: str) -> None:
        self._connection = _sql.connect(filename)
        self._cursor = self._connection.cursor()
    def execute(self, *commands):
        """
        Run SQL commands.
        """
        for c in commands:
            self._cursor.execute(c)
    def createTable(self, name: str, *entries: Entry):
        """
        Creates a table.
        """
        rawEntryData = "("
        i = 0
        for e in entries:
            i += 1
            rawEntryData += f"{e._name} {e._type}"
            if i != len(entries):
                rawEntryData += ","
        rawEntryData += ")"
        self.execute(f"CREATE TABLE {name} {rawEntryData}")
    def createRow(self, tableName: str, *values):
        rawEntryData = "("
        i = 0
        for e in values:
            i += 1
            rawEntryData += f"{e if type(e) != str else f'{e}'}"
            if i != len(values):
                rawEntryData += ","
        rawEntryData += ")"
        self.execute(f"INSERT INTO {tableName} VALUES {rawEntryData}")
    