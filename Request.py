#coding=utf-8
from proxy_tool import *


class ItslawRequester(object):
    head = '''
    Accept:application/json, text/plain, */*
    Accept-Encoding:gzip, deflate, sdch, br
    Accept-Language:zh-CN,zh;q=0.8
    Cache-Control:no-cache
    Connection:keep-alive
    Cookie:Hm_lvt_603ab75906557bfe372ca494468e3e1b=1500890396; gr_user_id=73f97a63-9f9e-4895-abcb-7d8ec53950fc
    Host:www.itslaw.com
    If-Modified-Since:Mon, 26 Jul 1997 05:00:00 GMT
    Pragma:no-cache
    Referer:https://www.itslaw.com/detail?judgementId=2cb05a0a-c661-4844-b4fc-448fd62e8048&area=1&index=2&count=1351&sortType=1&conditions=trialYear%2B2015%2B7&conditions=caseType%2B2%2B10&conditions=court%2B48%2B5
    User-Agent:Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3226.400 QQBrowser/9.6.11681.400
    '''

    # same id same condition court%2B7%2B5%2CcaseType%2B2%2B10%2CtrialYear%2B2014%2B7
    detail_url_tpl = 'https://www.itslaw.com/api/v1/detail?timestamp=1505136306015&judgementId=$0&area=$6&sortType=1&conditions=court%2B$5%2B5%2CcaseType%2B$4%2B10%2CtrialYear%2B$3%2B7%2CjudgementType%2B$7%2B9'
    detail_ref_tpl = 'https://www.itslaw.com/detail?judgementId=$0&area=$6&index=$1&count=$2&sortType=1&conditions=trialYear%2B$3%2B7&conditions=caseType%2B$4%2B10&conditions=court%2B$5%2B5%2CjudgementType%2B$7%2B9'

    # only needs
    case_url_tpl = 'https://www.itslaw.com/api/v1/caseFiles?startIndex=0&countPerPage=2&sortType=1&conditions=trialYear%2B$0%2B7%2B$0&conditions=caseType%2B$1%2B10%2Bxxxxxx&conditions=judgementType%2B$2%2B9%2Bzzzzzzz'
    case_ref_tpl = 'https://www.itslaw.com/search?searchMode=judgements&sortType=1&conditions=trialYear%2B$0%2B7%2B$0&conditions=caseType%2B$1%2B10%2Bxxxxxx&conditions=judgementType%2B$2%2B9%2Bzzzzzzz'

    list_url_tpl = case_url_tpl + "&conditions=court%2B$3%2B5%2Bxxxxxxxxx"
    list_ref_tpl = case_ref_tpl + "&conditions=court%2B$3%2B5%2Bxxxxxxxxx&searchView=text"

    case_type = '2'
    year = '2014'
    judge_type = '1'

    send_headers = dict()

    proxy_pool = None

    def __init__(self, year, case_type, judge_type, proxy_enable= False):
        self.case_type = str(case_type)
        self.year = str(year)
        self.judge_type = str(judge_type)
        if proxy_enable:
            self.proxy_pool = ProxyPool()
            print("proxy enable!")

        self.send_headers = load_header()

    def get_detail(self, index, count, court_id, area, doc_id):
        index, count, doc_id, court_id, area = map(str, (index, count, doc_id, court_id, area))
        assert all([x.isdigit() for x in [index, count, court_id, area]])
        timestamp = str(time.time() - 5).replace('.','')
        # detail_url = self.detail_url_tpl % (doc_id, self.year, self.case_type, court_id)
        detail_url = self.detail_url_tpl.replace('$0', doc_id).replace('$3', self.year).replace('$4', self.case_type)\
            .replace('$5', court_id).replace("1505136306015", timestamp).replace('$6', area).replace('$7', self.judge_type)

        # detail_ref = self.detail_ref_tpl % (doc_id, index, count, self.year, self.case_type, court_id)
        detail_ref = self.detail_ref_tpl.replace('$0', doc_id).replace('$1', index).replace('$2', count).replace('$3', self.year)\
            .replace('$4', self.case_type).replace('$5', court_id).replace('$6', area).replace('$7', self.judge_type)

        #print(detail_ref)
        #print(detail_url)
        return self.__req(detail_url, detail_ref)

    def get_case(self):
        """no use"""
        case_url = self.case_url_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', self.judge_type)
        case_ref = self.case_ref_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', self.judge_type)
        print(case_url)
        print(case_ref)
        return self.__req(case_url, case_ref)

    def get_list(self, court_id):
        court_id = str(court_id)
        list_url = self.list_url_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', self.judge_type).replace('$3', court_id)
        list_ref = self.list_ref_tpl.replace('$0', self.year).replace('$1', self.case_type).replace('$2', self.judge_type).replace('$3', court_id)
        # print(list_url)
        # print(list_ref)
        return self.__req(list_url, list_ref)

    # def __decompress(self, response):
    #     data = response.read() # reads
    #     if response.info().get('Content-Encoding') == 'gzip':
    #         if v == 2:
    #             buf = StringIO(data)
    #             f = gzip.GzipFile(fileobj=buf)
    #             data = f.read()
    #         else:
    #             data = gzip.decompress(data).decode("utf-8")
    #         return data
    #     elif type(data) == bytes:
    #         if v == 2:
    #             return str(data)
    #         else:
    #             return str(data, encoding='utf-8')
    #     return data

    def __req(self, url, ref):
        heade = dict(self.send_headers)
        heade['Referer'] = ref
        if self.proxy_pool :
            proxy = self.proxy_pool.get_random()
            while proxy:
                try:
                    result = request_with_proxy(url, heade, {'https': proxy})
                    self.proxy_pool.confirm_success(proxy)
                    sys.stdout.write(proxy + "\t")
                    return result
                except :
                    self.proxy_pool.confirm_fail(proxy)
                time.sleep(2)
                proxy = self.proxy_pool.get_random()

        else:
            return request_with_proxy(url, heade) #raise exception out

