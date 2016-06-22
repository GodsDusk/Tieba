#coding:utf-8
import re
import json
import  requests
from bs4 import BeautifulSoup

import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  

COOKIE = {}
BLOCKIDURL = 'http://tieba.baidu.com/pmc/blockid'


if __name__ == '__main__':
	
	URL = 'http://tieba.baidu.com/p/4109398533?pid=77872777981&cid=#77872777981'
	pid = '77872777981'
	ID = u'心不在医'	
	r = requests.get(URL, cookies = COOKIE)
	soup = BeautifulSoup(r.text, 'html.parser')
	tbs = re.search("tbs.+?\".+?\"", soup.text).group().split("\"")[-2]


	dic = {'tbs': tbs, 'day': '1', 'reason': '\xe5\xb9\xbf\xe5\x91\x8a', 'fid': '52433', 'user_name[]': ID, 'ie': 'gbk', 'pid[]': pid}

	r = requests.post(BLOCKIDURL, cookies = COOKIE, data = dic)

	print r.json()['errmsg']
	if r.json()[u'errno'] == 0:
		print tbs