#coding: utf-8

from selenium import webdriver
import re

import urllib2
import sys
from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
from datetime import date
import json
import xlrd

from xlrd import open_workbook
from xlutils.copy import copy
import time

description_id = 1
browser = webdriver.Chrome(executable_path='F:\chromedriver_win32\chromedriver.exe')
def start(url, d, today, vstock):
   # try:
    global description_id
    global browser
    url = url

    try:
	    browser.get(url)
	    t = browser.page_source

	    pn = re.compile(r'(.*)"statuses":(.*?)}]', re.S)
	    match = pn.match(t)
	    if not match:
	       # browser.close()
	       # browser.quit()
	    	return 0
	    result =  match.group(2)
	    result = result + '}]'
	    decode = json.loads(result)
	
	    startDetect = time.time()
	    st = int(time.mktime(datetime.strptime(datetime.strftime(today, "%Y-%m-%d"), "%Y-%m-%d").timetuple()))
	    ed = int(time.mktime(datetime.strptime(datetime.strftime(today + timedelta(days = 1), "%Y-%m-%d"), "%Y-%m-%d").timetuple()))
	    st = str(st) + '000'
	    print(st)
	    ed = str(ed) + '000'
	    print(ed)

	    s_today = datetime.strftime(today, "%Y-%m-%d")
	    for i in range(len(vstock)):

			for item in decode:
				if item['mark'] == 1:
					continue
				#print item['created_at'], st, ed
				#print item['description'].encode('utf-8'), vstock[i]._name
				if str(item['created_at']) > st and str(item['created_at']) < ed:
					if item['text'].encode('utf-8').find(vstock[i]._name) != -1:
						ff = open('corpus/' + s_today + '_' + str(description_id) + '.txt', 'w')
						ff.write(item['text'].encode('utf-8'))
						ff.close()
						description_id += 1
						#print vstock[i]._name, item['description'].encode('utf-8')
						if d.has_key(i):
							d[i] = d[i] + 1
						else:
							d[i] = 1
				elif str(item['created_at']) < st and i == len(vstock) -1:
					#print 1
				#	browser.close()
				#	browser.quit()
					#if i == len(vstock) -1: 
					return 0

			#print array[0], array[1]
			


	   # print decode[0]['description'].encode('utf-8')
	   	
	   # browser.close()
	   # browser.quit()
	    return 1
    except Exception as e:
    	print(e)

       # browser.close()
       # browser.quit()	
        return 0

#获取热门用户列表
def get_id():

	url = 'http://xueqiu.com/people/all'
	
	headers = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6"}
	req = urllib2.Request( url, headers = headers)
	try:
		content = urllib2.urlopen(req).read()
	except:
		return
	soup = BeautifulSoup(content)
	
	name = soup.find('ul',class_='tab_nav')
	h = name.findAll('a')
	f = open('id.txt', 'w')
	people = {}
	for item in h:
		link = item.get('href')
		if link.find('id') != -1:

			url = 'http://xueqiu.com' + link
			print(url)
			headers = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6"}
			req = urllib2.Request( url, headers = headers)
			try:
				content = urllib2.urlopen(req).read()
			except:
				return
			soup = BeautifulSoup(content)
			name = soup.find('ul',class_='people')
			h = name.findAll('li')
			for item in h:
				p = item.findAll('input')
				print(p[0].get('value').encode('utf-8'), p[1].get('value').encode('utf-8'))
				if not people.has_key(p[0].get('value').encode('utf-8')):
					people[p[0].get('value').encode('utf-8')] = 0
					f.write(p[0].get('value').encode('utf-8') + ' ' + p[1].get('value').encode('utf-8') + '\n')
class stock:
	_name = ''
	_industry = ''
	_id = ''


	def __init__(self, id, name, industry):
		self._id = id
		self._name = name
		self._industry = industry

def pawner(day, t2):


	today   = date.today()
	delta = -1


	while 1:
		f = open('id.txt', 'r')
		delta += 1
		if delta >= t2:
			break
		yesterday1 = today - timedelta(days = day - delta)
		yesterday = datetime.strftime(yesterday1, "%Y-%m-%d")
		score_file = 'score' + yesterday + '.txt'
		industry_file = 'industry' + yesterday + '.txt'
		#ff = open('score' + yesterday + '.txt', 'r')
		d = {}
		print(score_file)
		vstock = []
		#ff = open('stock.txt', 'r')


		wb = xlrd.open_workbook('stock.xls')
		sh = wb.sheet_by_name('stock')

		for rownum in range(sh.nrows):
			if rownum < 2:
				continue
			s = stock(str(sh.cell(rownum, 0).value), sh.cell(rownum, 1).value.encode('utf-8'), sh.cell(rownum, 2).value.encode('utf-8'))
			vstock.append(s)


		print(len(vstock))
		print(repr(vstock[0]._name))
		while 1:
			try:
				line = f.readline()
			#	user = str(i)
				if not line:
					break
				array = line[:-1].split(' ')
				user = array[0]
				print(array[0], array[1])
				#user = "1676206424"
				page = 1
				while 1:

					url = "http://xueqiu.com/" + user + "?page=" + str(page)
					ret = start(url, d, yesterday1, vstock)
					if ret == 0:
						#print i
						break
					page = page + 1
				time.sleep(2)
			except Exception as e:
				print(e)
				continue
		f.close()
		ff = open(score_file, 'w')

		industry_p = open(industry_file, 'w')
		rb = open_workbook('stock.xls')
		rs = rb.sheet_by_name('stock')
		wb = copy(rb)
		ws = wb.get_sheet(0)
		ncol = rs.ncols	
		ws.write(1, ncol, yesterday)
		industry_d = {}
		t = sorted(d.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
		for key in t:
			print str(vstock[key[0]]._name) + '%' + str(vstock[key[0]]._industry) + '%'+ str(key[1]) + '\n'
			ff.write(str(vstock[key[0]]._name) + '%' + str(vstock[key[0]]._industry) + '%'+ str(key[1]) + '\n')

			if industry_d.has_key(vstock[key[0]]._industry):
				industry_d[vstock[key[0]]._industry] += 1
			else:
				industry_d[vstock[key[0]]._industry] = 1

			ws.write(key[0] + 2, ncol, key[1])

		t = sorted(industry_d.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
		for key in t:
			print(str(key[0]) + '%' + str(key[1]) + '\n')
			industry_p.write(str(key[0]) + '%' + str(key[1]) + '\n')

		print(industry_d)
		wb.save('stock.xls')

	browser.close()
	browser.quit()

if __name__ == "__main__":

	t = int(sys.argv[1])
	t2 = int(sys.argv[2])
	get_id()
	pawner(t, t2)
