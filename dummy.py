import sqlite3
import random

conn = sqlite3.connect("temp.db")
cursor = conn.cursor()

names = [
    "Alice","Bob","Charlie","David","Emma","Frank","Grace","Hannah","Ian","Jack",
    "Kevin","Liam","Mia","Noah","Olivia","Paul","Quinn","Ryan","Sophia","Tom",
    "Uma","Victor","Wendy","Xavier","Yara","Zane"
]

departments = [
    "Engineering",
    "Design",
    "HR",
    "Marketing",
    "Sales",
    "Finance",
    "Support"
]

rows = []

for i in range(120):
    name = random.choice(names) + f"_{i}"
    department = random.choice(departments)
    salary = random.randint(40000, 120000)
    joined_year = random.randint(2018, 2024)

    rows.append((name, department, salary, joined_year))

cursor.executemany(
    """
    INSERT INTO employees (name, department, salary, joined_year)
    VALUES (?, ?, ?, ?)
    """,
    rows
)

conn.commit()
conn.close()

print("Inserted", len(rows), "rows")
