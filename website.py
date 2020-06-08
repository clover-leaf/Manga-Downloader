#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
from multiprocessing.dummy import Pool as ThreadPool
import requests
from lxml import html
import pickle
from jsbeautifier.unpackers import packer

class Website:
	
	INVALID_CHARACTER = list('\/:*?"<>|')
	
	@classmethod
	def loadManga(cls):
		with open('etc/{}.pkl'.format(cls.name), 'rb') as f:
			return pickle.load(f)
		# sql = 'select * from blogtruyen'
		# cur.execute(sql)
		# return cur.fetchall()

	@classmethod
	def saveManga(cls, dictManga):
		with open('etc/{}.pkl'.format(cls.name), 'wb') as f:
			pickle.dump(dictManga, f)

	@classmethod
	def downloadRoot(cls, path, title, image_urls):
		path = cls.createFolder(path, title)
		
		info =  [(path, i, image_urls[i]) for i in range(len(image_urls))]
		# Using ThreadPool to download faster
		pool = ThreadPool(4)
		pool.map(cls.saveImg, info)
		pool.close()
		pool.join()
		return path

	@staticmethod
	def saveImg(info):
		path, c, url = info
		with open(path + '\{0:02}.png'.format(c+1), 'wb') as f:
			f.write(requests.get(url).content)

	@staticmethod
	def filterFolderName(INVALID_CHARACTER, title):
		for char in INVALID_CHARACTER:
			title = title.replace(char, "_")
		return title.strip()

	@classmethod
	def createFolder(cls, path, title):
		title = cls.filterFolderName(cls.INVALID_CHARACTER, title)
		path += '\\' + title
		while os.path.exists(path):
			path += '_new'
		os.makedirs(path)
		return path

class mangak(Website):

	name = 'mangak'
	
	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://mangak.info/page/{}/?s&q'.format(x)

		response = requests.get(url(1))
		tree = html.fromstring(response.content)
		pg = tree.xpath("//div[@class='wp-pagenavi']\
						/span[@class='pages']")[0].text
		last_page = pg.split("/")[1].strip()
		dictManga = {}
		for i in range(int(last_page)):
			page = requests.get(url(str(i + 1)))
			tree = html.fromstring(page.text)
			ls = tree.xpath("//h3[@class='nowrap']/a")
			for x in ls:
				dictManga[x.text_content()] = x.attrib['href']
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@class='vung_doc']/script")[0]\
									.text_content().split('"')
		title = tree.xpath("//h1[@class='name_chapter entry-title']")[0].text
		image_urls = [ls[2*i + 1] for i in range(int(len(ls)/2))]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@class='chapter-list']//a")
		return {c: (i.attrib["title"], i.attrib['href']) \
								for c, i in enumerate(ls)}
		
	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//*[@class='truyen_info_right']/li/h1")[0].text
		return cls.createFolder(path, title)
		
class hentaivn(Website):

	name = 'hentaivn'
	
	@classmethod
	def updateManga(cls):
		url = 'https://hentaivn.net/forum/search-plus.\
					php?name=&dou=&char=&group=0&search=&page='
		a = requests.get(url + '1')
		tree = html.fromstring(a.text)
		ls = tree.xpath("//div//li/a")
		last_page = ls[-1].attrib['href'].split("page=")[-1]
		dictManga = {}
		for i in range(int(last_page)):
			page = requests.get(url + str(i + 1))
			tree = html.fromstring(page.text)
			for x in tree.xpath("//*[@class='search-des']/a"):
				if "the-loai" not in x.attrib["href"]:
					dictManga[x.text_content()] = 'https://hentaivn.net'\
					 + x.attrib['href']
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@id='image']/img")
		title = tree.xpath("//head/title")[0].text
		title = title.split("em Hentai Sex: ")[1]
		image_urls = [x.attrib['src'] for x in ls]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls_title = [i.attrib["title"].split("ruyện hentai ")[1]\
					for i in tree.xpath("//*[@class='chuong_t']")]
		ls_url = [i.attrib["href"] for i in \
						tree.xpath("//td/a[@target='_blank']")]
		return {c: (x[0], 'https://hentaivn.net'\
				+ x[1]) for c, x in enumerate(zip(ls_title, ls_url))}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//head//title")[0].text
		title = title.replace("ruyện Hentai: ", "|").split("|")[1]
		return cls.createFolder(path, title)

class nettruyen(Website):

	name = 'nettruyen'
	
	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://mangak.info/page/{}/?s&q'.format(x)

		response = requests.get(url(1))
		tree = html.fromstring(response.content)
		pg = tree.xpath("//div[@class='wp-pagenavi']\
						/span[@class='pages']")[0].text
		last_page = pg.split("/")[1].strip()
		dictManga = {}
		for i in range(int(last_page)):
			page = requests.get(url(str(i + 1)))
			tree = html.fromstring(page.text)
			ls = tree.xpath("//h3[@class='nowrap']/a")
			for x in ls:
				dictManga[x.text_content()] = x.attrib['href']
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@class='vung_doc']/script")[0]\
									.text_content().split('"')
		title = tree.xpath("//h1[@class='name_chapter entry-title']")[0].text
		image_urls = [ls[2*i + 1] for i in range(int(len(ls)/2))]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@class='chapter-list']//a")
		return {c: (i.attrib["title"], i.attrib['href']) \
								for c, i in enumerate(ls)}
		
	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//*[@class='truyen_info_right']/li/h1")[0].text
		return cls.createFolder(path, title)

class blogtruyen(Website):
	
	name = 'blogtruyen'

	@classmethod
	def updateManga(cls):
		url = 'http://blogtruyen.com/timkiem/nangcao/1/0/-1/-1?p='
		a = requests.get(url + '1')
		tree = html.fromstring(a.text)
		idk = tree.xpath("//*[@title='Trang cuối']")
		last_page = idk[0].attrib['href'].split('=')[1]
		dictManga = {}
		for i in range(int(last_page)):
			page = requests.get(url + str(i + 1))
			tree = html.fromstring(page.text)
			for x in tree.xpath("//*[@class='fs-12 ellipsis tiptip']/a"):
				dictManga[x.text] = x.attrib['href']
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.text)
		ls = tree.xpath("//*[@id='content']/img")
		title = tree.xpath("//header/h1")[0].text
		image_urls = [x.attrib['src'] for x in ls]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//*[@id='list-chapters']//span[@class='title']/a")
		return {c: (x.attrib['title'], 'http://blogtruyen.com' + \
			x.attrib['href']) for c, x in enumerate(ls)}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.text)
		title = tree.xpath("//head//title")[0].text
		title = title.split(" |")[0]
		return cls.createFolder(path, title)

class vnsharing(Website):

	name = 'vnsharing'
	
	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://truyen.vnsharing.site/index/KhamPha/newest/{}'\
					.format(x)
		dictManga = {}
		for x in range(1, 40):
			response = requests.get(url(x))
			tree = html.fromstring(response.content)
			ls = tree.xpath(\
				"//li[@class='browse_result_item']/a[@class='title']")
			for i in ls:
				dictManga[i.text_content()] = i.attrib['href']
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='br_frame']//img")
		name = tree.xpath("//a[@class='read_header_title']")[0]
		chap = tree.xpath("//div[@class='read_header_chapter']")[0]
		title = name.text_content() + ' ' + chap.text
		image_urls = [x.attrib['src'] for x in ls]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//li[@class='browse_result_item']/a[@class='title']")
		return {c: (i.attrib["title"], i.attrib['href']) \
			for c, i in enumerate(ls)}
		
	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//head/title")[0].text.split("::")[0]
		return cls.createFolder(path, title)

class hocvientt(Website):
	
	name = 'hocvientt'

	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://hocvientruyentranh.net/searchs?keyword=&type=\
		-1&author=-1&status=-1&submit=T%C3%ACm+ki%E1%BA%BFm&page={}'.format(x)
		response = requests.get(url(1))
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='box-footer']//ul/li/a")
		last_page = ls[-2].text_content()
		dictManga = {}
		for i in range(int(last_page)):
			response = requests.get(url(i+1))
			tree = html.fromstring(response.content)
			ls = tree.xpath("//table[@class='table table-hover']//tr/td/a")
			l = len(ls)
			for i in range(l//3):
				dictManga[ls[3*i].attrib["title"]] = ls[3*i].attrib["href"]
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='manga-container']/img")
		title = tree.xpath("//head/title")[0].text
		title = title.split(" |")[0]
		image_urls = [x.attrib["src"] for x in ls]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='table-scroll']//td/a")
		title = tree.xpath("//head/title")[0].text
		title = title.split(" |")[0]
		return {c: (title + " " + x.attrib['title'], x.attrib['href'])\
					for c, x in enumerate(ls)}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//head/title")[0].text
		title = title.split(" |")[0]
		return cls.createFolder(path, title)

class tttuan(Website):
	
	name = 'tttuan'

	@classmethod
	def updateManga(cls):
		url = 'http://truyentranhtuan.com/danh-sach-truyen/'
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='manga-focus']/span[@class='manga']/a")
		dictManga = {}
		for c, i in enumerate(ls):
			dictManga[i.text_content()] = i.attrib["href"]
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		var = re.findall(r'var slides_page_[^\n]+', response.text)
		urls = re.findall(r'https?://[^"]+', ''.join(var))
		image_urls = list(map(lambda x: x.replace("amp;", ""), urls))
		image_urls = sorted(image_urls, key=cls.natural_key)

		tree = html.fromstring(response.content)
		title = tree.xpath("//head/title")[0].text
		title = title.split("-")[0].strip()
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def natural_key(string_):
		return [int(s) if s.isdigit() else s for s in re.findall(\
			r'(\d{1,3})(?:(?=.jpg)|(?=.png)|(?=.bmp)|(?=.JPG)|(?=.PNG)|(?=.BMP))',\
			string_)]

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//span[@class='chapter-name']/a")
		return {c: (x.text_content(), x.attrib['href']) \
				for c, x in enumerate(ls)}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//head/title")[0].text
		title = title.split("- Truyện tranh online - ")[0]
		return cls.createFolder(path, title)

class tt8(Website):
	
	name = 'tt8'

	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://truyentranhtam.com/search.php?&page={}\
				&view=list&act=timnangcao'.format(x)
		response = requests.get(url(1))
		tree = html.fromstring(response.content)
		last_page = tree.xpath("//p[@class='page']//a")[-1].attrib['data-page']
		dictManga = {}
		for i in range(int(last_page)):
			print(i)
			response = requests.get(url(i+1))
			tree = html.fromstring(response.content)
			ls = tree.xpath("//a[@class='tipsy']")
			for i in ls:
				dictManga[i.text_content()] = i.attrib["href"]
		cls.saveManga(dictManga)

	@staticmethod
	def natural_key(string_):
		return [int(s) if s.isdigit() else s for s in re.findall(\
			r'(\d{1,3})(?:(?=.jpg)|(?=.png)|(?=.bmp)|(?=.JPG)|(?=.PNG)|(?=.BMP))',\
			string_)]
		
	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		data = re.findall(r"eval[^\n]*", response.text)[0]
		unpack = packer.unpack(data)
		regex = r"""(?:(?<=lstImages\[\d\]=")|(?<=lstImages\[\d\d\]=")|
			(?<=lstImages\[\d\d\d\]="))https?://[^'|^"]+"""
		ls = [i for i in re.findall(regex, unpack) if "haybaoloi" not in i]
		image_urls = sorted(ls, key=cls.natural_key)
		
		tree = html.fromstring(response.content)
		title = tree.xpath("//div/h1")[0].text.split(":")[0]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//ul[@id='ChapList']//a")
		return {c: (x.attrib['title'].split('ruyện tranh')[1],\
		 	x.attrib['href']) for c, x in enumerate(ls)}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		title = tree.xpath("//body//h1")[0].text
		title = title.split('ruyện Tranh')[1]
		return cls.createFolder(path, title)

class uptruyen(Website):
	
	name = 'uptruyen'

	@classmethod
	def updateManga(cls):
		url = lambda x: 'http://uptruyen.com/manga/tat-ca-the-loai?&page={}&order_by=name&order_type=DESC'.format(x)
		response = requests.get(url(1))
		tree = html.fromstring(response.content)
		last_page = tree.xpath('//ul[@class="m_pagination"]//a')[-2].text_content()
		dictManga = {}
		for i in range(int(last_page)):
			print(i)
			response = requests.get(url(i+1))
			tree = html.fromstring(response.text)
			ls = tree.xpath('//li[@class="wrapper-top-view-shounen wrapper-top-view-common"]/p//a')
			for i in ls:
				dictManga[i.attrib['title']] = 'http://uptruyen.com'+i.attrib["href"]
		cls.saveManga(dictManga)

	@classmethod
	def download(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.content)
		ls = tree.xpath("//div[@class='container']//img")
		title = tree.xpath("/html/head/title")[0].text
		title = title.split("|")[0]
		image_urls = [x.attrib["src"] for x in ls if 
				'.gif' not in x.attrib["src"]]
		return cls.downloadRoot(path, title, image_urls)

	@staticmethod
	def updateChapter(url):
		response = requests.get(url)
		tree = html.fromstring(response.text)
		ls = tree.xpath('//div[@id="chapter_table"]//a')
		return {c: (x.text_content(), 'http://uptruyen.com'\
			+ x.attrib['href']) for c, x in enumerate(ls)}

	@classmethod
	def prepareFolder(cls, path, url):
		response = requests.get(url)
		tree = html.fromstring(response.text)
		title = tree.xpath('/html/head/title')[0].text
		return cls.createFolder(path, title)


DICT = {"Blogtruyen": blogtruyen,
		# "Vagabond": vagabond, 
		"Hentaivn": hentaivn,
		"Mangak": mangak,
		"Vnsharing": vnsharing,
		"Hocvientruyentranh": hocvientt,
		"TruyenTranhTuan": tttuan,
		"TruyenTranh8": tt8,
		"Uptruyen": uptruyen}
