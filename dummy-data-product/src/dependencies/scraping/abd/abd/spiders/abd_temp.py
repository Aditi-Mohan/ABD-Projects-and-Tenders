import scrapy
from scrapy import Request
import logging


class AbdTempSpider(scrapy.Spider):
    name = 'abd_temp'
    allowed_domains = ['www.adb.org']
    start_urls = ['https://www.adb.org/projects?page=0/']
    headers= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'}
    counter = 0
    # allData = []

    def start_requests(self):
        for url in self.start_urls:
            yield Request(url, headers=self.headers)

    def parse(self, response):
        items = response.xpath('//div[@class="list"]/div[@class="item"]')
        for item in items:
            # try:
            meta = {
                "status": item.xpath('.//div[1]/div[1]/span[2]/@class').get(),
                "approvalDate": item.xpath('.//div[1]/div[2]/span[2]/@content').get(),
                "link": 'https://www.adb.org'+item.xpath('.//div[2]/a/@href').get(),
                "title": item.xpath('.//div[2]/a/text()').get(),
                "summary": item.xpath('.//div[3]/text()').get()
            }

            yield response.follow(url=meta['link'], callback=self.parse_info, meta=meta, headers=self.headers)
            # except:
                # logging.debug("error")
        # logging.info(len(self.allData))
        # logging.info(self.allData)
    
    def getDesc(self, res):
        desc = ""
        desct = res.xpath('.//tr[11]/td[2]/text()').get()
        if desct is None:
            descs = res.xpath('.//tr[11]/td[2]/p')
            for each in descs:
                desc += each.xpath('.//text()').get()
        else:
            desc = desct
        return desc

    def getBudget(self, res):
        amt = 0
        innerTable = res.xpath('.//tr[6]/td[2]/table/tr')
        for each in innerTable:
            amtText = each.xpath('.//td[2]/text()').get()
            if(amtText is not None):
                amtText = amtText[4:]
                if("million" in amtText):
                    amtText = amtText[:amtText.index("million")].strip().replace(",", "")
                    amt += float(amtText)*1000000
                else:
                    amtText = amtText.strip().replace(",", "")
                    amt += float(amtText)
        # logging.debug(amt)
        # logging.debug(innerTable)
        # num = res.xpath('/tr/td[2]')
        # logging.debug(len(num))
        return amt
    
    def getSectorsAndSubsectors(self, res):
        list = res.xpath('.//tr[9]/td[2]/p')
        sec = []
        subsec = []
        for each in list:
            str = each.get()
            str = str.replace('<p><strong class="sector">', "")
            str = str.replace('</strong>', "")
            str = str.replace('</p>', "")
            str = str.replace('\n', "")
            sec.append(str[:str.index("/")].strip())
            subsec.append(str[str.index("/")+1:].strip())
            # sec.append(each.xpath('.//strong/text()').get())
            # subsec.append(each.xpath('.//text()').get()[3:])
        return sec, subsec
    
    def getDocUrls(self, res):
        urls = []
        catOfDoc = res.xpath('//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][3]/div')
        for each in catOfDoc:
            docs = each.xpath('.//div/div/table/tbody/tr')
            if(docs.get() is not None):
                for i in docs:
                    urls.append('https://www.adb.org'+i.xpath('.//td[1]/a/@href').get())
        return urls

    def getDates(self, res):
        timetable = res.xpath('//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][2]/div/div/div/div/table[./tbody/tr[1]/th/text() = "Timetable"]').get()
        logging.debug(timetable is None)
        return 0
    
    def parse_info(self, response):
        # numberOfDetails = len(response.xpath('//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][1]/div/div[2]/div/div[2]/ul/li'))
        # sectorsRes = response.xpath(f'//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][1]/div/div[2]/div/div[2]/ul/li[{numberOfDetails}]/span/ul/li')
        # sectors = []
        # for each in sectorsRes:
        #     sectors.append(each.xpath('.//text()').get())

        # # logging.debug(numberOfDetails)

        # projectDetails = {
        #     "status": response.request.meta['status'],
        #     "approvalDate": response.request.meta['approvalDate'],
        #     "link": response.request.meta['link'],
        #     "title": response.request.meta['title'],
        #     "summary": response.request.meta['summary'],
        #     "projectOfficer": response.xpath('//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][1]/div/div[2]/div/div[2]/ul/li[1]/span/strong[2]/text()').get(),
        #     "country": response.xpath(f'//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][1]/div/div[2]/div/div[2]/ul/li[{numberOfDetails-1}]/span/text()[2]') .get(),
        #     "sectors": sectors,
        # }

        # tabs
        table1 = response.xpath('//div[@id="tabs-0"]/div[contains(@class, "tabs-panel")][2]/div/div/div/table')

        sec, subsec = self.getSectorsAndSubsectors(table1)
        docUrls = self.getDocUrls(response)
        # logging.debug(table1)

        projectDetails = {
            # "aug_id": ,
            "original_id": table1.xpath('.//tr[2]/td[2]/text()').get(),
            "project_or_tender": "P",
            "name": response.request.meta['title'],
            "description": self.getDesc(table1),
            "source": "ABD",
            "status": response.request.meta['status'],
            # "stage": ,
            "budget": self.getBudget(table1),
            "url": response.request.meta['link'],
            "document_urls": docUrls,
            "sectors": sec,
            "subsectors": subsec,
            "country_name": response.xpath('.//tr[3]/td[2]/text()').get(),
            # "country_code": ,
            # "reigon_name": ,
            # "region_code": ,
            # "state": ,
            # "county": ,
            # "city": ,
            # "locality": ,
            # "nieghbourhood": ,
            # "location": ,
            # "map_coordinates": ,
            "timestamps": self.getDates(response),
            # "timestamp_range": {"min": , "max": },
        }

        yield projectDetails

