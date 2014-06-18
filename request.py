import mechanize

browser = mechanize.Browser()
response = browser.open('http://www.huelol.com')
print response.info()
