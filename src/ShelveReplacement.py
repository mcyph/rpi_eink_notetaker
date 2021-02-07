import json
import sqlite3
from os.path import exists


ENABLE_WAL_QUERY = 'PRAGMA journal_mode=WAL;'
CREATE_QUERY = 'CREATE TABLE my_data(key TEXT NOT NULL PRIMARY KEY, value TEXT NOT NULL);'
COUNT_QUERY = 'SELECT COUNT(key) FROM my_data'
ITER_QUERY = 'SELECT key FROM my_data ORDER BY key ASC'
# Note the use of the "?" character to
# prevent SQL injection vulnerabilities!
SETITEM_QUERY = 'REPLACE INTO my_data (key, value) VALUES (?, ?);'
GETITEM_QUERY = 'SELECT value FROM my_data WHERE key = ?;'
DELITEM_QUERY = 'DELETE FROM my_data WHERE key = ?;'


class ShelveReplacement:
    def __init__(self, path):
        # Note "path" can be ":memory" for a fast in-memory storage (which is lost on exit)
        already_exists = exists(path)
        self.con = sqlite3.connect(path)

        # Enable write-ahead logging
        # Please see https://www.sqlite.org/wal.html for more info before using this!
        self.con.execute(ENABLE_WAL_QUERY)

        if not already_exists:
            self.con.execute(CREATE_QUERY)
            self.con.commit()

    def commit(self):
        # Make sure changes are written to disk
        self.con.commit()

    def close(self):
        self.commit()
        self.con.close()

    def __len__(self):
        for len_, in self.con.execute(COUNT_QUERY):
            return len_

    def __iter__(self):
        # Allow "for key in my_shelve_replacement: ..." syntax
        # Note the coercion to list() to allow for __getitem__
        # to be called while iterating through the keys
        for key, in list(self.con.execute(ITER_QUERY)):
            yield key

    def __setitem__(self, key, value):
        self.con.execute(SETITEM_QUERY, (key, json.dumps(value)))

    def __getitem__(self, key):
        for value, in self.con.execute(GETITEM_QUERY, (key,)):
            return json.loads(value)
        raise KeyError(key)  # Not found!

    def __delitem__(self, key):
        self.con.execute(DELITEM_QUERY, (key,))


if __name__ == '__main__':
    db = ShelveReplacement('demo_db.sqlite')
    db['my_key'] = 'my_value'
    print(db['my_key'])
    for my_key in db:
        print(my_key, db['my_key'])
    db.close()

    db = ShelveReplacement('demo_db.sqlite')
    print(db['my_key'])
    db['my_key'] = 'my_new_value'
    print(db['my_key'])
    print(len(db))
    db.close()

