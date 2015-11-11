import mysql.connector

class MysqlHelper(object):
	"""docstring for MysqlHelper"""
	def __init__(self, username, pwd, db):
		super(MysqlHelper, self).__init__()
		self.username = username
		self.pwd = pwd
		try:
			self.conn = mysql.connector.connect(user=username, password=pwd, database=db)
			self.cur = self.conn.cursor()
		except Exception, e:
			print e
	
	def rowcount(self, sql): 
		self.cur.execute(sql)
		self.cur.fetchall()
		return self.cur.rowcount

	def create(self, table, params=None):
		sqlselect = 'show tables like "%s"' %table
		if (self.rowcount(sqlselect) < 1):
			try:
				sqlcreate = 'create table %s %s' %(table,params)
				self.cur.execute(sqlcreate)
			except Exception, e:
				print "Error: can not create table %s" %table
				print e

	def update(self, sql):
		try:
			self.cur.execute(sql)
		except Exception, e:
			raise e

	def insert(self, sql, params):
		try:
			self.cur.execute(sql,params)
			self.conn.commit()
		except mysql.connector.errors.IntegrityError:
			print "Error: it is existed."

	def query(self, sql):
		self.cur.execute(sql)
		return self.cur.fetchall()

	def __del__(self): 
	    try:
	      self._cur.close() 
	      self._conn.close() 
	    except:
	      pass

	def close(self):
		self.__del__()

conn1 = MysqlHelper('root','516cyy','python')
# conn1.create('test','(id int primary key, name varchar(20))')
# conn1.insert('insert into test values (%s,%s)', ['1','curly'])
res = conn1.query('select count(*) from test')
