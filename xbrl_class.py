import urllib2, re, csv, sys, httplib
import lxml.etree as etree
from io import StringIO
from bs4 import BeautifulSoup
from datetime import datetime
from collections import defaultdict

class filer(object):
	def __init__(self, cik):
		self.cik = cik
		self.secUrl = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=' + self.cik + '&type=10&count=40'
		self.instances = []

        def __str__(self):
            return str(self.cik) + ' has ' + str(len(self.instances)) + ' filings'

	def addInstances(self, number = 1):
		"""
		given an integer number, this will populate a list with the instance details of the last n filings.
		"""
		loop = self.filingGenerator()
		for n in xrange(number):
			self.instances.append(loop.next())

	def getInstance(self):
		return self.instances[:]

	def parseXBRL(self):
		concepts = []
		

	def filingGenerator(self):
		"""
		Generator function
		With a CIK, navigate to instance file on the sec.
		Yield lxml etree iterable
		"""
		try:
			u = urllib2.urlopen(self.secUrl)
			html = u.read()
		except:
			read_error_counter += 1
			print "sec main page error"
		else:

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
		
				# find links to filing documents
				split_links = html.split("\" id=\"documentsbutton\"");
			
				for s in split_links:
					split_xbrl = s.split("<a href=\"")

					#then check to see if we have an href to follow
					if 'Archives' in split_xbrl[len(split_xbrl) - 1]:
						# then follow the link to filings
						url = 'http://www.sec.gov' + split_xbrl[len(split_xbrl) - 1]
						u = urllib2.urlopen(url)
	
						try:
							html = u.read()
						except:
							read_error_counter += 1
							print "sec main page error"
						else:
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
									except:
										read_error_counter += 1
										print "sec main page error"
									else:
										u.close
										html = html.split("-->")
										xml = ""
										for element in html:
											sub = element.split("<!--")
											xml = xml + sub[0] 
										try:
											p = etree.XMLParser(huge_tree=True, recover=True)
											xmldoc = etree.fromstring(xml, p)
										except:
											read_error_counter += 1
											print "sec main page error"
										else:
											if len(xmldoc) > 10:
												yield [split_date, list(xmldoc)]
