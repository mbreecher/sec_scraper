import urllib2, re, csv, sys
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

pstart = datetime.now()
dest = open('C:/ipy/sec_scraper/2015-05/subsidiaries.csv', 'w')
writer = csv.writer(dest)
#error file
error = open('C:/ipy/sec_scraper/2015-05/errors_21.csv', 'w')
error_write = csv.writer(error)

with open('C:/ipy/sec_scraper/2015-05/ciks.csv', 'rb') as f:
	reader = csv.reader(f)
	for i, line in enumerate(reader):
		# for each cik, read html page on sec
		testcik = str(line[0])
		print "cik" + " " + testcik
		url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + testcik + '&type=10-K&dateb=&owner=exclude&count=40'
		u = urllib2.urlopen(url)
		try:
			html = u.read()
			
			if 'No matching CIK' in html:
				print line[0] + ' is an invalid CIK'
				error_result = [line[0], 'invalid CIK']
				error_write.writerow(error_result)
			else:
				split_name = html.split("<span class=\"companyName\">")
				if len(split_name) > 1:
					split_name = split_name[1].split("<")
					split_name = split_name[0].strip()
				else:
					split_name = "name not found"
				print split_name
				# find latest document link button
				split_links = html.split("\" id=\"documentsbutton\"");
				result = 0
				split_xbrl = split_links[0].split("<a href=\"")
				
				#then check to see if we have an href to follow
				if 'Archives' in split_xbrl[len(split_xbrl) - 1]:
					# then follow the link to filings
					url = 'http://www.sec.gov' + split_xbrl[len(split_xbrl) - 1]
					u = urllib2.urlopen(url)
					
					try:
						html = u.read()
						u.close
						instance_split = html.split("EX-21")
						if len(instance_split) >= 2:
							split_page = instance_split[len(instance_split)-2].split(".htm</a>");
							split_xbrl = split_page[len(split_page)-2].split("<a href=\"")
							split_xml = split_xbrl[len(split_xbrl)-1].split("\">")
							
							url = 'http://www.sec.gov' + split_xml[0]
							u = urllib2.urlopen(url)
							html = u.read()
							soup = BeautifulSoup(html)
							
							result = []
							allrows = soup.findAll('tr')
							for row in allrows:
								result.append([])
								allcols = row.findAll('td')
								for col in allcols:
									thestrings = [s.encode('ascii', 'ignore') for s in col.findAll(text=True)]
									thetext = ''.join(thestrings).strip()
									if len(thetext) > 0:
										result[-1].append(thetext)
							for i in result:
								if len(i) > 0:
									loop = i.pop(0)
									if len(loop) > 4:
										output = [testcik, split_name, loop]
										writer.writerow(output)
										print split_name + loop

					finally:
						u.close
		finally:
			pass

dest.close()
pend = datetime.now()
pdiff = pend - pstart
print pdiff
