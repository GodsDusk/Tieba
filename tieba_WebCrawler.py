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
	print u"""欢迎使用贴吧搜(人)索(肉)机,作者:%s\n注:\n\t1.代码执行期间可用Ctrl+C强行终止\n\t2.程序使用多线程查询,因此搜索结果并不完全按时间排列"""%__author__
	if platform.system().upper() == 'WINDOWS': #transform to gbk, fuck windows
		tiebaName = urllib.quote(raw_input(unicode('输入贴吧名:','utf-8').encode('gbk')))
		IDName = urllib.unquote(urllib.quote(raw_input(unicode("输入查询ID:",'utf-8').encode('gbk')).decode('gbk').encode('utf-8')))
		pageNumRange = raw_input(unicode("输入查询页数;输入回车将查询所有页面:",'utf-8').encode('gbk'))
		downloadPrompt = unicode("输入‘yes’下载所有网页到本地,其他任意键退出:",'utf-8').encode('gbk')
	else:
		tiebaName = raw_input("输入贴吧名:")
		IDName = raw_input("输入查询ID:")
		pageNumRange = raw_input("输入查询页数;输入回车将查询所有页面:")
		downloadPrompt = "输入‘yes’下载所有网页到本地,其他任意键退出:"

	return tiebaName, IDName, pageNumRange, downloadPrompt

def getLastPagination(url):

	r = requests.get(url)
	soup = BeautifulSoup(r.text,"html.parser")

	return re.search('pn=\d+',str(soup.find_all("a",string = u'\u5c3e\u9875'))).group()


def funcConvert(a_b):
	"""Convert `f([1,2])` to `f(1,2)` call."""
	return tiebaWebCrawler(*a_b)

def tiebaWebCrawler(pageNum,imformation):

	fid = open(imformation[u'fileName'], 'a')

	url = baseURL + '/f?kw=' + imformation[u'tiebaName'] + '&ie=utf-8&pn=' + str(PAGE_NUM*pageNum) 		
	r = requests.get(url)

	soup = BeautifulSoup(r.text, "html.parser")

	for _text_ in soup.find_all(title = "主题作者: " + imformation[u'IDName'] ):
		fid.write('<p>' + str(_text_.parent.parent.find('a')).replace("href=\"","href=\"" + baseURL) + '</p>' + '\n')

	fid.close()
		
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

	tiebaName, IDName, pageNumRange, downloadPrompt = welcomeInterface()

	pool = Pool(4)

	starTime = time.time()
	
	fileName = str(starTime) + '.html'
	fileHead = open(fileName, 'w')
	fileHead.write('<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />')
	fileHead.close()

	if pageNumRange.isdigit():
		pageNum = range(int(pageNumRange))
	else: 
		number = filter(str.isdigit, getLastPagination(baseURL + '/f?ie=utf-8&kw=' + tiebaName))
		pageNum = range(int(number)/PAGE_NUM + 1)


	second_arg = {'tiebaName':tiebaName, 'IDName':IDName, 'fileName':fileName}
	pool.map(funcConvert, itertools.izip(pageNum, itertools.repeat(second_arg)))

	print u"搜索完成,耗时:%f秒, 搜索结果保存在:%s中"%(time.time()-starTime, os.path.abspath(fileName))

	if raw_input(downloadPrompt) == 'yes':
		downloadURL(fileName)


	
