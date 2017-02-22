import psycopg2
from urllib.parse import urlparse

class DbServer:
    def __init__(self, uri):
        # urlparse.uses_netloc.append('postgres')
        self.uri = uri
        self.uriObj = urlparse(self.uri)
        self.conn = psycopg2.connect(
        database=self.uriObj.path[1:],
        user=self.uriObj.username,
        password=self.uriObj.password,
        host=self.uriObj.hostname,
        port=self.uriObj.port
        )
        self.cur = self.conn.cursor()
        self.create_tables()
        self.table_name = 'cases'
        # """Util queries"""
    def create_tables(self):
        tables = ["""
            CREATE TABLE IF NOT EXISTS parties(
            p_id SERIAL PRIMARY KEY,
            name TEXT
            )
            """,
            """
            CREATE TABLE  IF NOT EXISTS cases(
            c_id SERIAL PRIMARY KEY,
            party_name TEXT,
            court VARCHAR(255),
            case_id VARCHAR(255),
            case_type TEXT,
            date_filed DATE,
            date_closed DATE,
            disposition TEXT,
            search_query VARCHAR(255),
            p_id INTEGER,
            FOREIGN KEY (p_id) REFERENCES parties(p_id))
          """]

        for tSql in tables:
            self.execute(tSql)
            self.commit()

    def commit(self):
        self.conn.commit()

    def execute(self, sql, values=None):
        if values:
            self.cur.execute(sql, values)
        else:
            self.cur.execute(sql)

    def create_table(self, tableName, schema):
        createTblSQL = 'create table {} {};';
        self.execute(createTblSQL.format(tableName, schema))
        self.commit()

    def drop_table(self,):
        dropTblSQL = 'drop table parties cascade; drop table cases;'
        self.execute(dropTblSQL)
        self.commit()

    def delete_by_id(self, _id):
        getSQL = 'delete from {} where id = {} ;'
        self.execute(getSQL.format(self.table_name,_id))
        self.commit()

    # """These are useful queries for tracer"""
    def add_party(self, party):
        query = 'INSERT INTO parties(name) VALUES (\'{}\')'
        self.execute(query.format(party))
        self.commit()

    def add_cases(self, cases):
        [self.add_case(c) for c in cases]

    def add_case(self, case_info):
        query = """
        INSERT INTO cases(party_name,
                          search_query,
                          court,
                          case_id,
                          case_type,
                          date_filed,
                          date_closed,
                          disposition,
                          p_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (case_info['party_name'],
          case_info['search_query'],
          case_info['court'],
          case_info['case_id'],
          case_info['case_type'],
          case_info['date_filed'],
          case_info['date_closed'],
          case_info['disposition'],
          case_info['p_id']
          )
        self.execute(query, values)
        self.commit()

    # """These are useful queries for slacker"""
    def get_parties(self):
        self.execute('SELECT * FROM parties;')
        return self.cur.fetchall()
    def get_counts(self):
        countSQL = 'SELECT count(*), search_query FROM cases GROUP BY search_query';
        self.execute(countSQL)
        return self.cur.fetchall()

    def check_case_exists(self, case_id):
        countSQL = 'SELECT count(*) FROM cases WHERE case_id=\'{}\';'.format(case_id)
        self.execute(countSQL)
        count = self.cur.fetchone()
        return count[0]

    def get_all(self, reverse=False):
        if reverse:
            getSQL = 'select * from {} order by id desc;'
        else:
            getSQL = 'select * from {};'
            self.execute(getSQL.format(self.table_name))
            return self.cur.fetchall()