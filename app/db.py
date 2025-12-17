#import os
#import mysql.connector

#def get_db_connection():
#    return mysql.connector.connect(
#        host=os.environ.get("MYSQL_HOST", "mysql"),
#        user=os.environ.get("MYSQL_USER", "root"),
#        password=os.environ.get("MYSQL_PASSWORD", "root"),
#        database=os.environ.get("MYSQL_DB", "cloudapp")
#    )


# app/db.py
import os
import mysql.connector

def get_db_connection():
    host = os.environ["MYSQL_HOST"]
    user = os.environ["MYSQL_USER"]
    password = os.environ["MYSQL_PASSWORD"]
    db = os.environ["MYSQL_DB"]

    return mysql.connector.connect(
        host=host,
        user=user,
        password=password,
        database=db
    )
