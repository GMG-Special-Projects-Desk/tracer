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

  def create_tables(self):
    tables = ["""
                CREATE TABLE  IF NOT EXISTS cases(
                id SERIAL PRIMARY KEY,
                party_name TEXT,
                court VARCHAR(255),
                case_id VARCHAR(255),
                case_type TEXT,
                date_filed DATE,
                date_closed DATE,
                disposition TEXT,
                search_query VARCHAR(255))

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

  def get_count(self):
    countSQL = 'select count(*) from {};';
    self.execute(countSQL.format(self.tableName))
    res = self.cur.fetchone()
    return res[0]

  def drop_table(self, tableName):
    dropTblSQL = 'drop table {};'
    self.execute(dropTblSQL.format(tableName))
    self.commit()

  def delete_by_id(self, _id):
    getSQL = 'delete from {} where id = {} ;'
    self.execute(getSQL.format(self.tableName,_id))
    self.commit()

  def get_all(self, reverse=False):
    if reverse:
      getSQL = 'select * from {} order by id desc;'
    else:
      getSQL = 'select * from {};'
    self.execute(getSQL.format(self.tableName))
    return self.cur.fetchall()

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
                              disposition) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
    values = (case_info['party_name'],
              case_info['search_query'],
              case_info['court'],
              case_info['case_id'],
              case_info['case_type'],
              case_info['date_filed'],
              case_info['date_closed'],
              case_info['disposition']
              )
    self.execute(query, values)
    self.commit()
