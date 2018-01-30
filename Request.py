#coding=utf-8
import gzip
import  sys
import json
import time
v = sys.version_info[0]
if v == 3:
    import  urllib.request as ul
else:
    from StringIO import StringIO
    import urllib2 as ul

conditions = {'trialYear':'%2B$0%2B7%2B$0', 'caseType':'%2B$1%2B10%2Bxxxxxx', 'searchView':'text', 'court':'%2B$5%2B52C'}


class ItslawRequester:
    head = '''
    Accept:application/json, text/plain, */*
    Accept-Encoding:gzip, deflate, sdch, br
    Accept-Language:zh-CN,zh;q=0.8
    Cache-Control:no-cache
    Connection:keep-alive
    Cookie:gr_user_id=722f9c7e-37a3-44a4-a627-ed96592bd193; _t=33e8daef-9033-4684-aa13-e2abcd8f514e; showSubSiteTip=false; Hm_lvt_e496ad63f9a0581b5e13ab0975484c5c=1516844137,1516933430; Hm_lpvt_e496ad63f9a0581b5e13ab0975484c5c=1516952494; sessionId=e0d58c4a-7548-403b-9b47-73075b26f736; subSiteCode=bj; gr_session_id_8d9004219d790ea8=9fe24cef-53ae-49d0-bce3-fed3334a9af2
    Host:www.itslaw.com
    If-Modified-Since:Mon, 26 Jul 1997 05:00:00 GMT
    Pragma:no-cache
    Referer:https://www.itslaw.com/detail?judgementId=2cb05a0a-c661-4844-b4fc-448fd62e8048&area=1&index=2&count=1351&sortType=1&conditions=trialYear%2B2015%2B7&conditions=caseType%2B2%2B10&conditions=court%2B48%2B5
    User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3226.400 QQBrowser/9.6.11681.400
    '''

    # same id same condition court%2B7%2B5%2CcaseType%2B2%2B10%2CtrialYear%2B2014%2B7
    detail_url_tpl = 'https://www.itslaw.com/api/v1/detail?timestamp=1505136306015&judgementId=$0&area=1&sortType=1&conditions=court%2B$5%2B5%2CcaseType%2B$4%2B10%2CtrialYear%2B$3%2B7'
    detail_ref_tpl = 'https://www.itslaw.com/detail?judgementId=$0&area=1&index=$1&count=$2&sortType=1&conditions=trialYear%2B$3%2B7&conditions=caseType%2B$4%2B10&conditions=court%2B$5%2B5'

    # only needs
    case_url_tpl = 'https://www.itslaw.com/api/v1/caseFiles?startIndex=0&countPerPage=2&sortType=1&conditions=trialYear%2B$0%2B7%2B$0&conditions=caseType%2B$1%2B10%2Bxxxxxx'
    case_ref_tpl = 'https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B$0%2B7%2B$0&conditions=caseType%2B$1%2B10%2Bxxxxxx'

    list_url_tpl = case_url_tpl + "&conditions=court%2B$2%2B5%2Bxxxxxxxxx"
    list_ref_tpl = case_ref_tpl + "&conditions=court%2B$2%2B5%2Bxxxxxxxxx&searchView=text"

    case_type = '2'
    year = '2014'

    send_headers = dict([head.strip().split(":", 1) for head in head.strip().split('\n')])

    def __init__(self, case_type, year):
        self.case_type = str(case_type)
        self.year = str(year)

    def get_detail(self, index, count, doc_id, court_id):
        index, count, doc_id, court_id = map(str, (index, count, doc_id, court_id))
        assert all([x.isdigit() for x in [index, count,court_id]])
        timestamp = str(time.time() - 5).replace('.','')
        # detail_url = self.detail_url_tpl % (doc_id, self.year, self.case_type, court_id)
        detail_url = self.detail_url_tpl.replace('$0', doc_id).replace('$3', self.year).replace('$4', self.case_type).replace('$5', court_id).replace("1505136306015", timestamp)

        # detail_ref = self.detail_ref_tpl % (doc_id, index, count, self.year, self.case_type, court_id)
        detail_ref = self.detail_ref_tpl.replace('$0', doc_id).replace('$1', index).replace('$2', count).replace('$3', self.year).replace('$4', self.case_type).replace('$5', court_id)

        print(detail_ref)
        print(detail_url)
        return self.__req(detail_url, detail_ref)

    def get_case(self):
        case_url = self.case_url_tpl.replace('$0', self.year).replace('$1', self.case_type)
        case_ref = self.case_ref_tpl.replace('$0', self.year).replace('$1', self.case_type)
        print(case_url)
        print(case_ref)
        return self.__req(case_url, case_ref)

    def get_list(self, court_id):
        list_url = self.list_url_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', court_id)
        list_ref = self.list_ref_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', court_id)
        print(list_url)
        print(list_ref)
        return self.__req(list_url, list_ref)

    def __decompress(self, response):
        data = response.read() #reads
        if response.info().get('Content-Encoding') == 'gzip':
            if v == 2:
                buf = StringIO(data)
                f = gzip.GzipFile(fileobj=buf)
                data = f.read()
            else :
                data = gzip.decompress(data)
        return data

    def __req(self, url, ref):
        heade = dict(self.send_headers)
        heade['Referer'] = ref
        print(heade)
        req = ul.Request(url, headers= heade)
        resp = ul.urlopen(req)
        html = self.__decompress(resp)
##        doc = resp.read()
##        print doc
##        html = gzip.decompress(doc).decode("utf-8")
        return html