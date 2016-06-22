#coding:utf-8
import time
import re
import json 
import urllib
import sys  

from bs4 import BeautifulSoup
import requests

BASEURL = 'http://tieba.baidu.com'

MAINURL = BASEURL + '/f?kw=%E5%8E%A6%E9%97%A8%E5%A4%A7%E5%AD%A6&ie=utf-8&pn=0'#厦门大学

DELETEURL = 'http://tieba.baidu.com/f/commit/post/delete'
BLOCKIDURL = 'http://tieba.baidu.com/pmc/blockid'

FID = '52433'
KW = u'厦门大学'
COOKIE = {}#自行添加cookie





reload(sys)  
sys.setdefaultencoding('utf8')  

class fucker:
	def __init__(self, levelLimit, timeLimit):
		self.levelLimit = levelLimit
		self.timeLimit = int(filter(str.isdigit, str(timeLimit)))

	def requestURL(self, url):
		for t in xrange(3):
			try:
				r = requests.get(url, cookies = COOKIE, timeout = 3)
				return r
			except Exception, e:
				if t == 2:
					print url, 'time out!'

	def getTBS(self, url):
		r =self.requestURL(url)

		soup = BeautifulSoup(r.text, 'html.parser')
		return re.search("tbs.+?\".+?\"", soup.text).group().split("\"")[-2]

	def getThreadList(self):
		
		r = self.requestURL(MAINURL)

		soup = BeautifulSoup(r.text, "html.parser")
		threadList =[href.get('href') for href in soup.find_all('a', class_ = 'j_th_tit ')]
		return threadList


	def getLastPagination(self, url):
	
		r = self.requestURL(url)
				
		soup = BeautifulSoup(r.text,"html.parser")
		try:
			pageNum = re.search('pn=\d+',str(soup.find_all("a",string = u'\u5c3e\u9875'))).group()
		except Exception,e:
			pageNum = 'pn=0'
		return pageNum	


	def runFucker(self):
		threadList = self.getThreadList()
		for listURL in threadList:
			threadURL = BASEURL + listURL
			threadURL = threadURL + '?' + self.getLastPagination(threadURL)
			replyerList = self.getReplyerList(threadURL)

			for replyer in replyerList:
				motherFucker = self.fuckerJudge(replyer)
				if motherFucker:
					ID, pid = motherFucker
					tid = int(filter(str.isdigit, str(listURL)))
					tbs = self.getTBS(threadURL)
					print ID, tid, pid, tbs
					dicDelete = {'commit_fr':'pb', 'ie':'utf-8', 'tbs':tbs, 'kw':KW, 'fid':FID, 'tid':tid, 'is_vipdel':'0', 'pid':pid, 'is_finf':'false'}
					dicBlockid = {'day':'1','fid':FID,'tbs':tbs,'ie':'gbk','user_name[]':ID, 'pid[]':pid,'reason':'看置顶'}
					self.startDeleteAndBlock(threadURL, dicDelete, dicBlockid)
					# return
				# break
			# break

	def startDeleteAndBlock(self, href, dicDelete, dicBlockid = None):
		r = requests.post(DELETEURL, cookies = COOKIE, data = dicDelete)
		if r.json()['err_code'] == 0:
			print '删帖成功'
		else:
			print '删帖失败，帖子地址:',href	
		if dicBlockid:
			r = requests.post(BLOCKIDURL, cookies = COOKIE, data = dicBlockid)
			if r.json()['errno'] == 0:
				print '封禁成功'
			else:
				print '封禁失败，error reson:',r.json()['errmsg']

	def getReplyerList(self, threadURL):
		r = self.requestURL(threadURL)			
		soup = BeautifulSoup(r.text, "html.parser")
		# replyerList = soup.find_all('ul', class_ = 'p_author')
		replyerList = soup.find_all('div', class_ = 'l_post j_l_post l_post_bright  ')
		return replyerList


	def fuckerJudge(self, replyer):

		dataField = replyer.get('data-field')
	 	replyTime = re.search("date\":\".+?\"", dataField).group()
	 	
	 	if int(filter(str.isdigit, str(replyTime))) < self.timeLimit:#发帖时间检查
	 		return


		info = replyer.find('ul', class_ = 'p_author')

		info = info.text.strip().split('\n')
		ID = info[0]
		level = int(filter(lambda x:x.isdigit(),info[-1]))
		# if 
		if replyer.find('div', class_ = 'louzhubiaoshi j_louzhubiaoshi'): #排除回复自己的主题帖
			return
		# print ID, level
		if level < levelLimit:
			pid = re.search('post_id\":.+?,', dataField).group()
			pid = int(filter(str.isdigit, str(pid)))
			return ID, pid
		# print replyer.find('a', class_ = 'user_badge d_badge_bright d_badge_icon3_1')

if __name__ == '__main__':

	levelLimit = 4
	timeLimit = '2016-06-22 08:00'#注意个位数补0
	fuckerNo1 = fucker(levelLimit, timeLimit)
	while 1:
		fuckerNo1.runFucker()
		break

	



