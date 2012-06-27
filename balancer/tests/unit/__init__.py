from sqlalchemy import pool, event


@event.listens_for(pool.Pool, 'connect')
def on_connect(dbapi_con, con_record):
    if type(dbapi_con).__module__.startswith('pysqlite'):
        dbapi_con.cursor().execute('PRAGMA journal_mode=MEMORY')
