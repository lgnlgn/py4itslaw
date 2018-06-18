# py4itslaw
A simple python crawler for www.itslaw.com

```
目前在Python2.6 和Python3.5上经过测试可用；可能有一些没遇到的错误。 

在写爬虫期间，发现itslaw也有防机制，会直接封禁IP（猜测是抓了多久就封多久，抓1天封1天，又或者是抓多少条封多少秒），所以只做了单线程并且默认每个请求延迟1秒。

整个网站的文书按 年\裁判类型\文书类型 的组合切分出每次任务，欢迎大家一起使用，合力抓下全部文书。（因为尝试代理，以及没使用requests包，导致里面有很多废代码）
```


### py4itslaw是什么?

一个抓取itslaw 法律文书的简单爬虫

**本repo不再维护, 转到http://www.gitee.com/lgnlgn/py4itslaw**


### py4itslaw如何使用？


* 基本用法

 Usage: main.py [-y <year>][-t <caseType>][-j <judgeType>][-d [dir]][-v]

* Options:
```
  -h, --help            show this help message and exit
  -d DIR, --dir=DIR     data directory for saving [default = .]；Error log will be stored here. 
  -v                    set it to print crawling detail
  -y YEAR, --year=YEAR  set year, e.g. 2015
  -t CASETYPE, --case=CASETYPE
                        set caseType, in [1,2,3,4], 民事、刑事、行政、执行
  -j JUDGETYPE, --judge=JUDGETYPE
                        set judgeType, in [1,2,3,4,5], 判决、裁定、通知、决定、调解
  -i INTERVAL, --interval=INTERVAL
                        set crawling INTERVAL ms , [default = 1000]
  -p, --poweroff        set it to poweroff whether task finished or error occured
```

**可以看run.bat  run2.bat**


* 参数解释

 年份`year`；案由类型`caseType`；文书类型`judgeType`；为**必填**参数。 爬虫脚本每次任务以此三参数为准
 
 爬虫启动之后会在`DIR`下创建 `YEAR/CASETYPE_JUDGETYPE` 目录
 
 之后为year/caseType_judgeType 抓取一个每个法院总数的大列表，之后按法院id升序顺序抓取它的文书，
 
 每个法院的文书全部抓取完成后，更新大列表（如果觉得抓取比例不对，可以重置完成状态功下次重抓）
 
 每抓取一篇文书会停留至多`INTERVAL`毫秒
 
### 改进的方向
1. 代理池