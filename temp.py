import sqlite3

connection = sqlite3.connect('temp.db')

cursor = connection.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS student (
               id INT PRIMARY KEY,
               name TEXT NOT NULL,
               grade INT,
               section TEXT)""")

cursor.execute("""CREATE TABLE IF NOT EXISTS teacher (
               id INT PRIMARY KEY,
               name TEXT NOT NULL,
               salary INT)""")

connection.commit()

cursor.execute("SELECT type, name, tbl_name FROM sqlite_master WHERE type='table' AND Name NOT LIKE 'sqlite_%'")

results = cursor.fetchall()

for result in results:
    print(result)

cursor.execute("PRAGMA table_info(student)")

cols = cursor.fetchall()

for col in cols:
    print(col)