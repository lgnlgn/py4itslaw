import http.cookiejar
import gzip
import urllib.request as ul
# 设置保存cookie的文件，同级目录下的cookie.txt
user_agent = r'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36'
headers = {'User-Agent': user_agent, 'Connection': 'keep-alive',
           'Referer':'http://www.ip111.cn/',
           'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Encoding':'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
           'Cache-Control': 'no-cache',
           'Host': '45.32.164.128',
           'Pragma': 'no-cache',
           }
filename = 'cookie.txt'
# 声明一个MozillaCookieJar对象实例来保存cookie，之后写入文件
cjar = http.cookiejar.CookieJar()
# 利用urllib2库的HTTPCookieProcessor对象来创建cookie处理器
cookie_handler = ul.HTTPCookieProcessor(cjar)

proxy_handler = ul.ProxyHandler({"http":"180.110.249.210:8118"})

# 通过handler来构建opener
opener = ul.build_opener(cookie_handler, proxy_handler)
# 创建一个请求，原理同urllib2的urlopen

req = ul.Request("http://45.32.164.128/ip.php", headers= headers)

ul.install_opener(opener)
resp = ul.urlopen(req, timeout=30)

resphead = resp.info()
print(resphead)
data = resp.read()
print(data)
if 'gzip' in resphead['Content-Encoding']:
    data = gzip.decompress(data)
    print(data)
else:
    print(str(data, encoding='utf-8'))
print(cjar)


