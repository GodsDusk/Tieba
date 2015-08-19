# -*- coding: utf-8 -*-
import time
import os
import itertools
import platform
import urllib
from multiprocessing import Pool, freeze_support

import requests
from bs4 import BeautifulSoup 

import sys  

reload(sys)  
sys.setdefaultencoding('utf8')  

__author__ = 'Gods_Dusk'

PAGE_NUM = 50

def welcomeInterface():
	print u"""欢迎使用贴吧搜(人)索(肉)机,作者:%s\n注:\n\t1.代码执行期间可用Ctrl+C强行终止\n\t2.程序使用多线程查询,因此搜索结果并不完全按时间排列"""%__author__
	if platform.system().upper() == 'WINDOWS': '''fuck windows'''
	'''transform to gbk'''
			tiebaName = urllib.quote(raw_input(unicode('输入贴吧名:','utf-8').encode('gbk')))
			IDName = urllib.unquote(urllib.quote(raw_input(unicode("输入查询ID:",'utf-8').encode('gbk')).decode('gbk').encode('utf-8')))
			pageNum = range(int(raw_input(unicode("输入查询页数:",'utf-8').encode('gbk'))))
			downloadPrompt = unicode("输入‘yes’下载所有网页到本地,其他任意键退出:",'utf-8').encode('gbk')
	else:
 			tiebaName = raw_input("输入贴吧名:")
			IDName = raw_input("输入查询ID:")
			pageNum = range(int(raw_input("输入查询页数:")))
			downloadPrompt = "输入‘yes’下载所有网页到本地,其他任意键退出:"
	return tiebaName, IDName, pageNum, downloadPrompt


def funcConvert(a_b):
	"""Convert `f([1,2])` to `f(1,2)` call."""
	return tiebaWebCrawler(*a_b)

def tiebaWebCrawler(pageNum,imformation):

	fid = open(imformation[u'fileName'], 'a')

	url = 'http://tieba.baidu.com/f?kw=' + imformation[u'tiebaName'] + '&ie=utf-8&pn=' + str(PAGE_NUM*pageNum)		
	r = requests.get(url)

	soup = BeautifulSoup(r.text, "html.parser")

	for _text_ in soup.find_all(title = "主题作者: " + imformation[u'IDName'] ):
		fid.write(str(_text_.parent.parent.find('a')) + '\n')

	fid.close()
		
def downloadURL(fileName):
	
	starTime = time.time()
	url = 'http://tieba.baidu.com'
	fid = open(fileName, 'r')

	soup = BeautifulSoup(fid.read(), "html.parser")

	for link in soup.find_all('a'):
		if platform.system().upper() == 'WINDOWS':
			saveFileName = link.get(u'title').encode('gbk')
		else:
			saveFileName = link.get(u'title')
		fidHtml = open(str(saveFileName)+'.html', 'w')
		url = 'http://tieba.baidu.com' + str(link.get('href'))
		fidHtml.write(requests.get(url).text)
		fidHtml.close()
	print u"下载完成,耗时:%f秒"%(time.time()-starTime)


if __name__ == '__main__':

	tiebaName, IDName, pageNum, downloadPrompt = welcomeInterface()

	pool = Pool(4)

	starTime = time.time()
	fileName = str(starTime) + '.txt'

	second_arg = {'tiebaName':tiebaName, 'IDName':IDName, 'fileName':fileName}
	pool.map(funcConvert, itertools.izip(pageNum, itertools.repeat(second_arg)))

	print u"搜索完成,耗时:%f秒, 搜索结果保存在:%s中"%(time.time()-starTime, os.path.abspath(fileName))

	if raw_input(downloadPrompt) == 'yes':
		downloadURL(fileName)



	
