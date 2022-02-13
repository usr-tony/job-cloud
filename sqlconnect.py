import mysql.connector
# add a file named dbpw.py in the current directory with the login credentials as follows
# or it might be a good idea to use environment variables instead
from dbpw import endpoint, port, dbuser, dbpass, dbname

# rds database information


def connect_to_db():
    return create_sql_db()


def create_sql_db():
    con = mysql.connector.connect(host=endpoint, user=dbuser, passwd=dbpass, port=port, database=dbname)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS jobs
        (id INT, title TEXT, company TEXT, nation TEXT, state TEXT, city TEXT, area TEXT, suburb TEXT, 
        sector_id INT, sector TEXT, industry_id INT, industry TEXT, work_type TEXT, details TEXT, time TEXT)''')

    return (con, cur)

