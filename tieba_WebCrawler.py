# -*- coding: utf-8 -*-
import requests
import sys
import re  

__author__ = 'Gods_Dusk'

reload(sys)

sys.setdefaultencoding('utf8')
page_num = 50

def tieba_WebCrawler_run(tieba_name,ID_name,pageNum):

	ID_name = "<a href=\"/p/[^主]*title=\"主题作者: " + ID_name + "\""
	
	IDName=unicode(ID_name.encode('utf8'),'utf8')

	for index in range(int(pageNum)):
		url = 'http://tieba.baidu.com/f?kw=' + tieba_name + '&ie=utf-8&pn=' + str(page_num*index)
		#print url
		
		r = requests.get(url)

		unistr=unicode(r.text.encode('utf8'),'utf8')

		p = re.compile(IDName)  
		for m in p.finditer(unistr):  
		    print m.group()
		    fid.write(m.group())

		


if __name__ == '__main__':
	fid = open('re.txt','w')
	tieba_name = raw_input("输入贴吧名：")
	ID_name = raw_input("输入查询ID：")
	pageNum = raw_input("输入查询页数:")
	tieba_WebCrawler_run(tieba_name,ID_name,pageNum)
	fid.close()
