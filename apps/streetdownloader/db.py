import sqlite3
database="db.sqlite3"
conn=sqlite3.connect(database)
conn.execute("create tabl e input()")
