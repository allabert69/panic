import sqlite3

db_file = "panic.db"

# # Create database
# conn = sqlite3.connect(db_file)
# conn.close()

# Drop table
with sqlite3.connect(db_file) as conn:
    cur = conn.cursor()
    # noinspection SqlNoDataSourceInspection
    cur.execute(
        """DROP TABLE IF EXISTS articles"""
    )

# create table
with sqlite3.connect(db_file) as conn:
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY
            ,created_at TIMESTAMP
            ,published_at TIMESTAMP
            ,kind VARCHAR(20)
            ,domain VARCHAR(100)
            ,title VARCHAR(300)
            ,slug VARCHAR(300)
            ,currencies VARCHAR(10)
            ,url VARCHAR(300)
            ,link VARCHAR(300)
            ,sent_0 DECIMAL(6, 5)
            ,sent_1 DECIMAL(6, 5)
        )"""
    )