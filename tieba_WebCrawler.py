# -*- coding: utf-8 -*-
import time
import os
import itertools
import platform
import urllib
from multiprocessing import Pool, freeze_support
import re

import requests
from bs4 import BeautifulSoup 

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')  

__author__ = 'Gods_Dusk'

PAGE_NUM = 50 #50 posts per page
baseURL = 'http://tieba.baidu.com'

def welcomeInterface():

	print u"""欢迎使用贴吧搜(人)索(肉)机,作者:%s\n注:\n\t1.根据提示输入信息,按回车确认\n\t2.代码运行期间可用Ctrl+C强行终止\n\t3.程序使用多线程查询,因此搜索结果并不完全按时间排列"""%__author__
	if platform.system().upper() == 'WINDOWS': #transform to gbk, fuck windows
		tiebaName = urllib.quote(raw_input(unicode('输入贴吧名:','utf-8').encode('gbk')))
		IDName = urllib.unquote(urllib.quote(raw_input(unicode("输入查询ID:",'utf-8').encode('gbk')).decode('gbk').encode('utf-8')))
		pageNumRange = raw_input(unicode("输入查询页数:输入回车将查询所有页面:",'utf-8').encode('gbk'))
		searchMode = raw_input(unicode("输入查询类型:输入'1'只查询主题帖，其他任意键将查询所有发帖内容:",'utf-8').encode('gbk'))
		downloadSuggestion = unicode("输入‘yes’下载所有网页到本地,其他任意键退出:",'utf-8').encode('gbk')
	else:
		tiebaName = raw_input("输入贴吧名:")
		IDName = raw_input("输入查询ID:")
		pageNumRange = raw_input("输入查询页数:输入回车将查询所有页面:")
		searchMode = raw_input("输入查询类型:输入'1'只查询主题帖，其他任意键将查询所有发帖内容:")
		downloadSuggestion = "输入‘yes’下载所有网页到本地,其他任意键退出:"

	return tiebaName, IDName, pageNumRange, searchMode == '1', downloadSuggestion

def getLastPagination(url):

	r = requests.get(url)
	soup = BeautifulSoup(r.text,"html.parser")
	try:
		pageNum = int(filter(str.isdigit,re.search('pn=\d+',str(soup.find_all("a",string = u'\u5c3e\u9875'))).group()))
	except Exception, e:
		pageNum = 0
	return pageNum


def funcConvert(a_b):
	"""Convert `f([1,2])` to `f(1,2)` call."""
	return searchForum(*a_b)

def searchForum(pageNum,imformation):

	fileHead = open(imformation[u'fileName'], 'a')

	url = baseURL + '/f?kw=' + imformation[u'tiebaName'] + '&ie=utf-8&pn=' + str(PAGE_NUM*pageNum) 		
	r = requests.get(url)

	soup = BeautifulSoup(r.text, "html.parser")

	if not imformation[u'mode']:
		contents = soup.find_all('a', class_="j_th_tit ")#get thread lists
		for href in contents:
			searchPost(baseURL + href.get('href'), imformation[u'IDName'], fileHead) 
	else:
		for _text_ in soup.find_all(title = "主题作者: " + imformation[u'IDName'] ):
			fileHead.write('<p>' + str(_text_.parent.parent.find('a')).replace("href=\"","href=\"" + baseURL) + '</p>')

	fileHead.close()

def searchPost(rootURL, IDName, fileHead):
	pageNum = getLastPagination(rootURL)
	isThread = True
	for i in range(pageNum + 1):
		searchURL = rootURL + '?pn=' + str(i + 1)
		r = requests.get(searchURL)
		soup = BeautifulSoup(r.text, 'html.parser')
		if not i:
			title = soup.title.text
			# print title
		contents = soup.find_all('cc')
		for content in contents:
			try:
				userName = content.parent.parent.parent
				if userName.a.img:
					userName = userName.a.img.get('username')
				else:
					userName = userName.find_all('a')[1].img.get('username')
					if isThread and userName == IDName:
						fileHead.write('<p><font color="#FF0000">发表主题帖:</font><a class= \"thread\" href=\"' + rootURL + '\">' + title + '</a></p>\n')
						isThread = False
			except Exception, e:
				print Exception, e
			if userName == IDName:
				pid = filter(str.isdigit, str(content.div.get('id')))
				fileHead.write('<p>在' + title + '中<a class = \"post\" href=\"' + rootURL + '?pid=' + pid + '&cid=#' + pid + '\">' + '回复:' + content.div.text + '</a></p>\n') 


		
def downloadURL(fileName):
	
	starTime = time.time()
	
	fid = open(fileName, 'r')

	soup = BeautifulSoup(fid.read(), "html.parser")

	for link in soup.find_all('a'):
		if platform.system().upper() == 'WINDOWS':
			saveFileName = link.get(u'title').encode('gbk')
		else:
			saveFileName = link.get(u'title')
		fidHtml = open(str(saveFileName)+'.html', 'w')
		url = baseURL + str(link.get('href'))
		fidHtml.write(requests.get(url).text)
		fidHtml.close()
	print u"下载完成,耗时:%f秒"%(time.time()-starTime)


if __name__ == '__main__':

	tiebaName, IDName, pageNumRange, searchMode, downloadSuggestion = welcomeInterface()

	pool = Pool(4)

	starTime = time.time()
	
	fileName = str(starTime) + '.html'
	fileHead = open(fileName, 'w')
	fileHead.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
	fileHead.close()

	if pageNumRange.isdigit():
		pageNum = range(int(pageNumRange))
	else: 
		pageNum = range(getLastPagination(baseURL + '/f?ie=utf-8&kw=' + tiebaName)/PAGE_NUM + 1)


	second_arg = {'tiebaName':tiebaName, 'IDName':IDName, 'fileName':fileName, 'mode':searchMode}
	pool.map(funcConvert, itertools.izip(pageNum, itertools.repeat(second_arg)))

	print u"搜索完成,耗时:%f秒, 搜索结果保存在:%s中"%(time.time()-starTime, os.path.abspath(fileName))
	if searchMode:
		if raw_input(downloadSuggestion) == 'yes':
			downloadURL(fileName)


	
