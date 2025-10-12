import mysql.connector as sql
from sqlalchemy import create_engine
import pymysql

# Creating a database
def create_database(mycon):
    cursor = mycon.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS vehiclemanagement")
    mycon.close()

def sql_connect():
    # try:
    #     print("Trying initial connection...")
    #     mycon = sql.connect(host="localhost", user="root", password="123456")
    #     print("Initial connection successful.")
    #     create_database(mycon)
    # except sql.Error as e:
    #     print(f"🔥 SQL Error during initial connection: {e}")
    #     raise

    print("Connecting to DB vehiclemanagement...")
    mycon = sql.connect(host="localhost", user="root", password="123456", database="vehiclemanagement")
    print("DB connection established.")
    cursor = mycon.cursor()
    mycon.autocommit = False  # You must commit/rollback manually
    mycon.start_transaction(isolation_level='READ COMMITTED')  # Prevents dirty reads

    engine = create_engine(
        "mysql+pymysql://root:123456@localhost/vehiclemanagement",
        isolation_level="AUTOCOMMIT",  # Needed for to_sql commits
        # echo=True  # Uncomment for debug logging SQL queries
    )
    engcon = engine.connect()
    return mycon, cursor, engine, engcon

# Remove this call from global scope and call in your main script instead:
# mycon, cursor, engine, engcon = sql_connect()
try:
    mycon, cursor, engine, engcon = sql_connect()
except Exception as e:
    print(f"Failed to connect to database: {e}")
    exit(1)