#coding:utf-8
import time
import re
import json 
import os

from bs4 import BeautifulSoup
import requests

COOKIE = {}
BASEURL = 'http://tieba.baidu.com'
MAINURL = 'http://tieba.baidu.com/f?kw=%E5%8E%A6%E9%97%A8%E5%A4%A7%E5%AD%A6&ie=utf-8&pn=0'#厦门大学
DELETEURL = 'http://tieba.baidu.com/f/commit/post/delete'
BATCHDELETEURL = 'http://tieba.baidu.com/f/commit/thread/batchDelete'
BLOCKIDURL = 'http://tieba.baidu.com/pmc/blockid'
FID = '52433'
KW = u'厦门大学'

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  

def getThreadList():
	r = requests.get(MAINURL)
	soup = BeautifulSoup(r.text,"html.parser")
	threadList =[href.get('href') for href in soup.find_all('a', class_ = 'j_th_tit ')]
	return threadList

def getLastPagination(url):
	r = requests.get(url)
	soup = BeautifulSoup(r.text,"html.parser")
	try:
		pageNum = re.search('pn=\d+',str(soup.find_all("a",string = u'\u5c3e\u9875'))).group()
	except Exception,e:
		pageNum = 'pn=0'
	return pageNum

def runDelete(startTime):
	fileHandle = open(str(time.time())+'.txt', 'a')
	while time.time() - startTime < 60 * 60 * 6:#run 6 hours
		threadList = getThreadList()
		for url in threadList:
			pageNum = getLastPagination(BASEURL + url)
			delete_URL = BASEURL + url + '?' + pageNum
			deleteAndBlock(delete_URL,fileHandle)
		time.sleep(3)
	fileHandle.close()

def deleteAndBlock(url, fileHandle = None, sleepTime = 0):

	try:
		r = requests.get(url, cookies = COOKIE, timeout = 15)
	except Exception,e:
		return
		
	soup = BeautifulSoup(r.text,"html.parser")
	try:
		tbs = re.search("tbs.+?\".+?\"", soup.text).group().split("\"")[-2]		
	except Exception,e:
		print 'in %s can not find tbs'%url
		return

	for text_ in soup.find_all('cc'):

		result = deleteJudge(text_)
		if result:
			pid, userName = result
		else:
			continue

		dicDelete = {'commit_fr':'pb', 'ie':'utf-8', 'tbs':tbs, 'kw':KW, 'fid':FID, 'tid':'3988350709', 'is_vipdel':'0', 'pid':pid, 'is_finf':'false'}
		dicBlockid = {'day':'1','fid':FID,'tbs':tbs,'ie':'gbk','user_name[]':userName, 'pid[]':pid,'reason':'测试专用'}
		
		startDeleteAndBlock(dicDelete, dicBlockid, fileHandle)
		time.sleep(sleepTime)

def deleteJudge(content):

	try:
		userName = content.parent.parent.parent
		if userName.a.img:
			userName = userName.a.img.get('username')
		else:
			userName = userName.find_all('a')[1].img.get('username')
	except Exception, e:
		print Exception, e
	pid = filter(str.isdigit, str(content.div.get('id')))

	contentDeleteRule = open('./deleteRule/contentDeleteRule.txt','r').readlines()
	
	for deleteRule in contentDeleteRule:
		if re.match(deleteRule.replace('\t', '').replace(' ', '').replace('\n', ''), content.div.text.replace('\t', '').replace(' ', '').replace('\n', '').encode('utf8')):#回车符一定要去除，否则无法在语音帖中判断
			return pid, userName

	DeleteID = open('./deleteRule/deleteIDList.txt','r').readlines()

	for ID in DeleteID:
		if userName == ID.strip():
			return pid, userName 

def startDeleteAndBlock(dicDelete, dicBlockid = None, fileHandle =None):
	if fileHandle:
		fileHandle.write(dicBlockid[u'user_name[]'] + '\t' + dicDelete[u'tbs'] + '\t' + dicDelete[u'pid'] + '\n')
	r = requests.post(DELETEURL, cookies = COOKIE, data = dicDelete)
	if r.json()['err_code'] == 0:
		print '删帖成功'
	else:
		print '删帖失败，帖子地址:',BASEURL + '/p/' + dicDelete[u'tid'] + '?pid=' + dicDelete[u'pid'] + '&cid=#' + dicDelete[u'pid'] 	
	if dicBlockid:
		r = requests.post(BLOCKIDURL, cookies = COOKIE, data = dicBlockid)
		if r.json()['errno'] == 0:
			print '封禁成功'
		else:
			print '封禁失败，error reson:',r.json()['errmsg']

if __name__ == '__main__':
	while 1:
		runDelete(time.time())







