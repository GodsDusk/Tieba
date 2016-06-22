#coding:utf-8
import time
import re
import json 
import urllib
import sys  
import os

from bs4 import BeautifulSoup
import requests

class adder:
	def __init__(self, kw):

		self.COOKIE = {}#自行添加cookie
		self.kw = kw
		KW = urllib.quote(kw)
		self.addBlackURL = 'http://tieba.baidu.com/bawu2/platform/addBlack'
		self.listMemberURL = 'http://tieba.baidu.com/bawu2/platform/listMember?ie=utf-8&word=' + KW + '&stype=uname&svalue='
		self.memberBlackURL = 'http://tieba.baidu.com/bawu2/platform/listBlackUser?ie=utf-8&word=' + KW + '&stype=uname&svalue='

	def beginAdd(self, ID):

		memberURL = self.listMemberURL + urllib.quote(ID)
		r = self.getURL(memberURL)
		soup = BeautifulSoup(r.text, 'html.parser')

		info = re.search("badge bg_lv1.+", str(soup))
		if info:
			info = info.group()
		else:
			black = self.isBlack(ID)
			if black:
				print ID + ' is in black list'
			else:
				print ID + ' is not the member of ' + self.kw
				return 'save'
			return 

		tbs = re.search('tbs\":\".+?\"', str(soup)).group()
		tbs = tbs.split('\"')[-2]
		userID = re.search('id=\".+?\"', info).group()
		userID = filter(str.isdigit, userID)
		
		addInfo = {'user_id':userID, 'tbs':tbs, 'word':self.kw, 'ie':'utf-8'}
		r = self.postURL(self.addBlackURL,addInfo)
		print r.json()[u'errmsg']
		if r.json()[u'errmsg'] != 'success':
			return 'save'

	def isBlack(self, ID):

		memberBlackURL = self.memberBlackURL + urllib.quote(ID)
		r = self.getURL(memberBlackURL)
		soup = BeautifulSoup(r.text, 'html.parser')	
		if re.search(ID, str(soup)):
			return True

	def postURL(self, url, data):
		for tryTime in xrange(4):
			try:
				r = requests.post(url, cookies = self.COOKIE, timeout = 3, data = data)
			except Exception, e:
				pass
		return r

	def getURL(self, url):
		for tryTime in xrange(4):
			try:
				r = requests.get(url, cookies = self.COOKIE, timeout = 3)
			except Exception, e:
				pass
		return r

def readTxt():
	path = '/Volumes/未命名/Tieba/blockList/'
	fidSave = open('save.txt', 'a')
	aer = adder('厦门大学')
	content = ''
	for filename in os.listdir(path):
		if filename == '.DS_Store' or filename == '1.txt':
			continue
		fileHandle = open(path + '/' + filename, 'r')
		blocklist = fileHandle.readlines()
		for content in blocklist:
			try:
				[userName, tbs, pid] = content.strip().split('\t')
			except Exception, e:
				userName = content.strip()

			save = aer.beginAdd(userName)
			if save == 'save':
				content = content + userName + '\t' + tbs + '\t' + pid + '\n'
			else:
				content = content + userName + '\n'
			time.sleep(3)
		fidSave.write(content)
		content = ''
		fileHandle.close()
		os.remove(path + filename)
	fidSave.close()

if __name__ == '__main__':
	readTxt()


