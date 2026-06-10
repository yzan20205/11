import sqlite3

db = sqlite3.connect("database.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phone TEXT,
    product TEXT,
    email TEXT,
    password TEXT,
    expire TEXT
)
""")

cur.execute("""
INSERT INTO accounts
(phone, product, email, password, expire)
VALUES
('0551234567',
'Game Pass Ultimate',
'test@rtstore.com',
'RT123456',
'2027-06-10')
""")

db.commit()
db.close()

print("Database Created Successfully")