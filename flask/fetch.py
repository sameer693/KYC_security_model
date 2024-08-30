import sqlite3
import json
def get_db_connection():
    #conn = sqlite3.connect("database.db")
    conn = sqlite3.connect("DB.db")
    conn.row_factory = sqlite3.Row
    return conn

con = get_db_connection()
cursor = con.cursor()
cursor.execute('''select first_name,last_name,dob,address,adhar from users''')

rows = cursor.fetchall()
data = []
for row in rows:
    data.append(dict(row))
con.close()
print(json.dumps(data))
filename = "data.json"
with open(filename, "w") as f:
    f.write(json.dumps(data))

