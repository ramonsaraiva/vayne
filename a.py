import json
import urllib2

nr = 4
np = 50
url = 'https://ajax.googleapis.com/ajax/services/search/web?v=1.0&q=inurl:product.php?id=&start={0}'.format(nr*(np-1))
r = urllib2.urlopen(url)
j = json.loads(r.read())
try:
	for i in j['responseData']['results'][:4]:
		print urllib2.unquote(i['url'])
except Exception, e:
	print e
