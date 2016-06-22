# -*- coding: utf-8 -*-
import time
import os
import itertools
import platform
import urllib
import re

import requests
from bs4 import BeautifulSoup 

import sys  

reload(sys)  
sys.setdefaultencoding('utf8') 

class save:
	def __init__(self, url):
		
		self.url = url
		folder = url.split('/')[-1]
		self.savePath = os.getcwd() + '/'+ folder + '/'
		self.filePath = self.savePath + 'files/'
		if os.path.exists(self.savePath):
			if os.path.exists(self.filePath):
				pass
			else:
				os.mkdir(self.filePath)
		else:	
			os.mkdir(self.savePath)
			os.mkdir(self.filePath)
		self.COOKIE = []


	def runSave(self):
		pageNum, title = self.getPageInfo()

		fidSave = open(self.savePath + title + '.html', 'w')

		for num in xrange(1, pageNum + 1):

			soup = self.getText(self.url + '?pn=' + str(num))
			soup = self.downloads(soup)
			soup = self.getComment(soup)
			# return
			text = soup.prettify()
			fidSave.write(text + '\n')
			# return
		fidSave.close()

	def getComment(self, soup):
		
		post = soup.find_all('div', class_ = 'core_reply j_lzl_wrapper')
		for p in post:
			if p.div.a.text == '回复':
				continue

			dataField = p.find('div', class_ = "common_complient_container")
			if dataField:
				dataField =	eval(dataField.get('data-field'))
			else: 
				continue
			commentURL = 'http://tieba.baidu.com/p/comment?tid=' + str(dataField['thread_id']) + '&pid=' + str(dataField['post_id']) + '&pn=1&t=' + str(int(time.time()))
			r = self.requestGet(commentURL)
			addSoup = BeautifulSoup(r.text,"html.parser")
			p.find('div', class_ = "j_lzl_container core_reply_wrapper hideLzl").decompose()
			p.append(addSoup)
			# break
		return soup

	def downloads(self, soup):

		css = soup.find_all('link', rel = "stylesheet")
		for c in css:
			href = c.get('href')
			fileName = self.filePath + href.split('/')[-1]
			c['href'] = fileName 
			
			if os.path.isfile(fileName):
				continue
				# pass
			r = self.requestGet(href)
			tempSoup = BeautifulSoup(r.text,"html.parser")
			fid = open(fileName, 'w')
			fid.write(str(tempSoup))
			fid.close()

		content = soup.find_all('div', class_ = 'd_post_content j_d_post_content ')
		for c in content:
			img = c.img
			if img:
				imageURL = img.get('src')
				imageName = imageURL.split('/')[-1].replace('?t=20140803', '')#电脑端发表情时url中会有这个后缀
				imagePath = self.filePath + imageName
				img['src'] = imagePath

				if os.path.isfile(imagePath):
					continue
					#pass
				fidImage = open(imagePath, 'w')
				r = self.requestGet(imageURL)
				for chunk in r.iter_content():
					fidImage.write(chunk)
				fidImage.close()

		return soup

	def getPageInfo(self):
	
		r = self.requestGet(self.url)

		soup = BeautifulSoup(r.text,"html.parser")
		pageNum = re.search('pn=\d+',str(soup.find_all("a",string = u'\u5c3e\u9875')))

		title = soup.find('title').text
		return int(filter(str.isdigit, pageNum.group())) if pageNum else 1, title
	

	def requestGet(self, url):
		
		for t in xrange(3):
			try:
				r = requests.get(url, cookies = self.COOKIE, timeout = 3)
				return r
			except Exception, e:
				if t == 2:
					print url, 'time out!'


	def getText(self, url):

		r = self.requestGet(url)
		soup = BeautifulSoup(r.text,"html.parser")

		tempSoup = soup.find('div', class_ = 'tb_rich_poster_container')#去除发表回复栏
		tempSoup.decompose()		

		if url[-1] == '1':
			pass
		else:
			soup = soup.find('div', class_ = "content clearfix").extract()#只保留回复贴

		return soup



if __name__ == '__main__':
	saveRun = save(raw_input("输入贴子URL:\"(格式：'http://tieba.baidu.com/p/xxxxxxx'):\n"))
	saveRun.runSave()
