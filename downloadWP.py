# download all wordpress releases in zip format
from lxml import html
import requests
from urlparse import urlparse
import urllib


page = requests.get("https://wordpress.org/download/release-archive/")
tree = html.fromstring(unicode(page.content, "ISO-8859-1"))
cXPath = './/*[@id=\'pagebody\']/div/div[1]/table[1]/tbody/tr/td[2]/a[1]'
companies = tree.xpath(cXPath)

for company in companies:
    parsed = urlparse(company.attrib['href'])
    print parsed.geturl()
    print 'Wordpress' + parsed.path
    urllib.urlretrieve(parsed.geturl(), parsed.path[1:])

print "\n"
