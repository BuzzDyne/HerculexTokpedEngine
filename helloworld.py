import mysql.connector
from _cred import Credentials

mydb = mysql.connector.connect(
    host=Credentials["host"],
    user=Credentials["user"],
    password=Credentials["password"],
    database=Credentials["database"],
)

myCursor = mydb.cursor()


# region CREATE TABLE
# myCursor.execute("""DROP TABLE customers""")

# myCursor.execute("""
#     CREATE TABLE customers (
#         id INT AUTO_INCREMENT PRIMARY KEY,
#         name VARCHAR(255),
#         address VARCHAR(255)
#     )""")

# myCursor.execute("SHOW TABLES")
# for x in c:
#   print(x)
# endregion

# region INSERT INTO
sql = "INSERT INTO customers (name, address) VALUES (%s, %s)"
val = [
    ("Peter", "Lowstreet 4"),
    ("Amy", "Apple st 652"),
    ("Hannah", "Mountain 21"),
    ("Michael", "Valley 345"),
    ("Sandy", "Ocean blvd 2"),
    ("Betty", "Green Grass 1"),
    ("Richard", "Sky st 331"),
    ("Susan", "One way 98"),
    ("Vicky", "Yellow Garden 2"),
    ("Ben", "Park Lane 38"),
    ("William", "Central st 954"),
    ("Chuck", "Main Road 989"),
    ("Viola", "Sideway 1633"),
]

myCursor.executemany(sql, val)
mydb.commit()
print(myCursor.rowcount, "was inserted.")
# endregion

myCursor.execute("SELECT * FROM customers")

myresult = myCursor.fetchall()

for x in myresult:
    print(x)
