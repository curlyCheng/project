#! /usr/bin/python2
# -*- coding: utf-8 -*-
import re, os, urllib2, Queue, shutil, urllib, time, StringIO, gzip, httplib
from bloomfilter_test01 import BloomFilter

page_count = 0
img_count = 0
file_count = 0
headers = {
	'Accept-encoding':'gzip',
    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
}
seen = BloomFilter(500000, 10000)

def cbk(a,b,c):
	global img_count
	per = a * b * 100.0 / c
	if per > 100:
		per = 100
	print "%0.2f%%" % per

class Spider:
	def __init__(self, site, url, headers):
		self.site = site
		self.url = url
		self.headers = headers
		self.dir = ""
		self.current_page = ""
		self.now_site = site

	def getPage(self):
		result = None
		url = self.url
		req = urllib2.Request(url = url, headers = self.headers)
		try: response = urllib2.urlopen(req) #use default opener get response
		except  urllib2.HTTPError, e: #catch URLError and HttpError
			if hasattr(e, 'code'):
				print e.code
				print self.url
			elif hasattr(e, 'reason'):
				print e.reason
		except httplib.HTTPException, e:
			print e
			print self.url
		else: result = response
		return result

	def storeImage(self):
		global img_count
		imgReg = re.compile(r"""<img\s.*?\s?src\s*=\s*['|"]?(/[^\s'"]+).*?>""",re.I)
		imgRegRes = imgReg.findall(self.current_page)
		result = self.url_handler(imgRegRes)
		for img in result:
			url = img
			img = urllib.unquote(img).replace(self.now_site,'')
			index = img.rfind('/')
			file_dir = self.dir + (img[0:index])
			file_path = self.dir + img
			if os.path.exists(file_path):
				continue
			if not os.path.exists(file_dir):
				os.makedirs(file_dir)
			urllib.urlretrieve(url, file_path, cbk)
			img_count = img_count + 1
			print "downloaded %s images." %(img_count)
			
	def storePage(self):
		global page_count, file_count
		print self.url
		response = self.getPage()
		if not response:
			return
		app_prefix = (".doc",".docx",".zip",".rar",".txt",".xls",".xlsx")
		# isApp = response.headers['Content-Type'].find('application') + 1
		isApp = self.url.endswith(app_prefix)
		predata = response.read()
		pdata = StringIO.StringIO(predata)
		gzipper = gzip.GzipFile(fileobj=pdata)
		try:
			data = gzipper.read()
		except:
			data = predata
		self.current_page = data
		url = urllib.unquote(self.url).replace('http://','')
		if self.url == self.now_site:
			url = url + '/'
		prefix = url.endswith(('.html','.htm','.aspx','.php','.jsp'))
		if isApp or prefix:
			file_path = self.dir + url
			file_dir = self.dir + url[0:url.rfind('/')]
		else:
			if url.endswith('/'):
				file_dir = self.dir + url
				url = url + 'index.html'
				file_path = self.dir + url
			else:
				file_dir = self.dir + url[0:url.rfind('/')]
				url = url + '.html'
				file_path = self.dir + url
		if not os.path.exists(file_dir):
			os.makedirs(file_dir)	
		with open(file_path, "w+") as f:
			f.write(self.current_page)
			if not isApp:
				page_count = page_count + 1
				print "download", page_count, "pages."
				self.storeImage()
			else:
				file_count = file_count + 1
				print "download", file_count, "files."

	def extract_urls(self):
		findUrlRex = re.compile(r"""<a.*?href\s*=\s*['|"]{1}([^><"'#]+?)['|"]{1}.*?>.*?</a>""", re.I)
		result = findUrlRex.findall(self.current_page)
		return self.url_handler(result)
		
	def url_handler(self,urls):
		res = []
		for url in urls:
			if (url.startswith('http://') and len(url)>7):
				if (url.find(self.site[7:].replace('www.','')) > -1):
					res.append(url)
				continue
			elif (url.find("(") > -1):
				continue
			else:
				if url.startswith(('/','./')):
					url = url.replace('./','/')
				else:
					url = '/'+url
			if (url.count('../') > 0):
				steps = url.count('../')
				path = self.url.replace(self.now_site,'').split('/')[-1-steps:-1]
				arr = url.split('/')
				for i in path:
					arr[arr.index('..')] = i
				url = '/'.join(arr)
			res.append(self.now_site+url)
		return res

	def initDir(self,root):
		if not root:
			parent_dir = os.path.abspath('.')
		else:
			parent_dir = root
		dir_name = self.site.replace('http://','')
		file_dir = os.path.join(parent_dir, dir_name)
		if not os.path.exists(file_dir):
			os.mkdir(file_dir)	
		else:
			shutil.rmtree(file_dir, True)
		self.dir = file_dir+os.sep

	def main(self, root=None):
		global page_count
		wait_queue = Queue.Queue()
		wait_queue.put(self.url)
		seen.add(self.url)
		self.initDir(root)
		while not wait_queue.empty():
			self.url = wait_queue.get()
			if len(self.url) <= 7:
				continue
			if not self.url.startswith(self.now_site):
				self.now_site = 'http://'+self.url[7:].split('/')[0]
			self.storePage()
			for next_url in self.extract_urls():
				if not seen.in_bf(next_url):
					wait_queue.put(next_url)
					seen.add(next_url)
		print "total:", page_count, "page."

if __name__ == '__main__':
	start = time.time()
	print "input site:"
	input_site = raw_input()
	print "input start url:"
	input_url = raw_input()
	spider = Spider(site=input_site,url=input_url,headers=headers)
	spider.main(root="/home/curly/trash")
	print "use time: %0.2f sectonds" %(time.time() - start)