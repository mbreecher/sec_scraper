import urllib2, re, csv, sys
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

pstart = datetime.now()
dest = open('C:/cygwin64/home/Mike.Breecher/sec-scraper/test/fact_counts.csv', 'w')
writer = csv.writer(dest)
#error file
error = open('C:/cygwin64/home/Mike.Breecher/sec-scraper/test/errors.csv', 'w')
error_write = csv.writer(error)

with open('C:/cygwin64/home/Mike.Breecher/sec-scraper/test/ciks.csv', 'rb') as f:
	reader = csv.reader(f)
	for i, line in enumerate(reader):
		# for each cik, read html page on sec
		testcik = str(line[0])
		print "cik" + " " + testcik
		url = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + testcik + '&type=10&dateb=&owner=exclude&count=40'
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
				
				split_links = html.split("\" id=\"documentsbutton\"");
				s = 0
				result = 0
				while True:
					# check that we still have documents links and haven't gotten our 4 filings
					if s >= len(split_links) or result >= 4:
						break
					else:
						split_xbrl = split_links[s].split("<a href=\"")
						s = s + 1
						
						#then check to see if we have an href to follow
						if 'Archives' in split_xbrl[len(split_xbrl) - 1]:
							# then follow the link to filings
							url = 'http://www.sec.gov' + split_xbrl[len(split_xbrl) - 1]
							u = urllib2.urlopen(url)
							
							try:
								html = u.read()
								u.close
								instance_split = html.split("EX-101.INS")
								if len(instance_split) >= 2:
									split_page = instance_split[len(instance_split)-2].split(".xml</a>",1);
									split_xbrl = split_page[len(split_page)-2].split("<a href=\"")
									split_xml = split_xbrl[len(split_xbrl)-1].split("\">")
									
									#grab the filing date
									split_date = html.split("<div class=\"infoHead\">Filing Date</div>")
									split_date = split_date[1].split("<div class=\"infoHead\">Accepted</div>")
									split_date = split_date[0].replace("<div class=\"info\">","")
									split_date = split_date.replace("</div>","")
									split_date = split_date.strip()

									doctype = ""
									if "10-K" in html:
										doctype = "10-K"
									elif "10-Q" in html:
										doctype = "10-Q"

									# then follow the link to the instance file
									url = 'http://www.sec.gov' + split_xml[0]
									u = urllib2.urlopen(url)

									if not "10-Q/A" in html and not "10-K/A" in html: 
										try:
											html = u.read()
											html = html.split("-->")
											xml = ""
											for element in html:
												sub = element.split("<!--")
												xml = xml + sub[0] 

											try:
												p = etree.XMLParser(huge_tree=True)
												xmldoc = etree.fromstring(xml, p)
												if len(xmldoc) > 10:
													std_list = []
													ext_list = []
													ignored = []
													for node in list(xmldoc):
														if node.prefix is None or len(node.prefix) == 0:  
															ignored.append(node.tag)
														elif 'dei' in node.prefix or 'us-gaap' in node.prefix:
															std_list.append(node.tag)
														elif not 'xbrli' in node.prefix and not 'link' in node.prefix:
															ext_list.append(node.tag)
														else:
															ignored.append(node.tag)
												if len(std_list) > 0:
													fact_count = len(std_list) + len(ext_list)
													print testcik + "," + split_name + "," + doctype+ "," + split_date + "," + str(fact_count) + ',' + str(len(set(std_list))) + "," + str(len(set(ext_list))) 
													output = [testcik, doctype, split_date, fact_count, len(set(std_list)), len(set(ext_list))]
													writer.writerow(output)
													set(ignored)
													result = result + 1
											finally:
												pass
										finally:
											u.close
							finally:
								u.close
		finally:
			pass

dest.close()
pend = datetime.now()
pdiff = pend - pstart
print pdiff