import sqlite3
def get_db_connection():
    #conn = sqlite3.connect("database.db")
    conn = sqlite3.connect("DB.db")
    conn.row_factory = sqlite3.Row
    return conn

con=get_db_connection()
cursor = con.cursor()
cursor.execute('''
CREATE TABLE USERS (
	first_name VARCHAR2(50),
	last_name VARCHAR2(50),
	dob DATE,
	address VARCHAR2(255),
	adhar VARCHAR2(12),
	password VARCHAR2(255),
	user_face_encoding BLOB
)
''')
print(cursor.fetchall())
con.commit()
