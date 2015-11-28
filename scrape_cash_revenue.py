import urllib2, re, csv, sys, httplib
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict
from httplib import IncompleteRead

pstart = datetime.now()
execfile('./xbrl_class.py')
dest = open('./xbrl_data.csv', 'wb')
writer = csv.writer(dest)
#error file
error = open('./errors.csv', 'wb')
error_write = csv.writer(error)
read_error_counter = 0
header = ["CIK", "date", "cash", "revenue"]
writer.writerow(header)
cash = -1
revenue = -1
revenue_tag = ""
with open('./ciks.csv', 'rb') as f:
	reader = csv.reader(f)
	for i, line in enumerate(reader):
		# for each cik, read html page on sec
		testcik = str(line[0])
		print "cik" + " " + testcik
		loop = filer(testcik)
		try:		
			loop.addInstances()
		except:
			print 'no filings'
			latest = ''
			date = ''
		else:
			latest = loop.getInstance()[0][1]
			date = loop.getInstance()[0][0]
		cash = []
		revenue = []
		cash_out = ''
		revenue_out = ''
		for node in latest:
			if 'CashAndCashEquivalentsAtCarryingValue' in node.tag:
				cash.append(node.text)
			if 'Revenues' == node.tag.split('}')[1]:
				revenue.append(node.text)
		if len(cash)>0: 
			cash_out = max(cash)
		if len(revenue)>0: 
			revenue_out = max(revenue)
		print date
		print ' cash: ',
		print cash_out,
		print ' revenue: ',
		print revenue_out
		output = [testcik, date, cash_out, revenue_out]
		writer.writerow(output)

dest.close()
