import rethinkdb as r
from rethinkdb.errors import RqlRuntimeError

def dbSetUp():
    connection=r.connect(host='localhost',port=28015)
    try:
        r.db_create('remember_bot').run(connection)
        r.db('remember_bot').table_create('user').run(connection)
        r.db('remember_bot').table_create('post').run(connection)
        r.db('remember_bot').table_create('reminder').run(connection)
        print("Database setup completed")
    except RqlRuntimeError:
        print("Database running Okay")
    finally:
        connection.close()
