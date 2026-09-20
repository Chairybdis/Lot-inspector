import sqlite3

conn = sqlite3.connect("lots.db")
conn.execute("DELETE FROM lots WHERE lot_number = ?", ("-- New lot --",))
conn.commit()
conn.close()
print("Done.")
