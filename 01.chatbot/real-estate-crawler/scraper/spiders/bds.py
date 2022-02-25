import scrapy
import math

class Mogi(scrapy.Spider):
    name = "bds"
    PREFIX = 'https://batdongsan.com.vn'
    CURRENT_DOMAIN = 'HCM-ban-can-ho-chung-cu'
    CURRENT_URL = ''
    BASE_URLS = dict()
    CURRENT_BASE_URL = ''

    # BASE_URLS['HCM-ban-can-ho-chung-cu'] = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-tp-hcm/'
    # BASE_URLS['HCM-ban-nha-dat'] = 'https://batdongsan.com.vn/ban-nha-dat-tp-hcm/'
    BASE_URLS['HCM-ban-dat-dat-nen'] = 'https://batdongsan.com.vn/ban-dat-dat-nen-tp-hcm'
    # BASE_URLS['HCM-ban-kho-nha-xuong'] = 'https://batdongsan.com.vn/ban-kho-nha-xuong-tp-hcm/'
    # BASE_URLS['HCM-ban-loai-bat-dong-san-khac'] = 'https://batdongsan.com.vn/ban-loai-bat-dong-san-khac-tp-hcm/'

    # BASE_URLS['HCM-cho-thue-can-ho-chung-cu'] = 'https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-tp-hcm/'
    # BASE_URLS['HCM-cho-thue-nha-rieng'] = 'https://batdongsan.com.vn/cho-thue-nha-rieng-tp-hcm/'
    # BASE_URLS['HCM-cho-thue-nha-mat-pho'] = 'https://batdongsan.com.vn/cho-thue-nha-mat-pho-tp-hcm/'
    # BASE_URLS['HCM-cho-thue-nha-tro-phong-tro'] = 'https://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-tp-hcm/'
    # BASE_URLS['HCM-cho-thue-van-phong'] = 'https://batdongsan.com.vn/cho-thue-van-phong-tp-hcm/'
    # BASE_URLS['HCM-cho-thue-cua-hang-ki-ot'] = 'https://batdongsan.com.vn/cho-thue-cua-hang-ki-ot-tp-hcm'
    # BASE_URLS['HCM-cho-thue-kho-nha-xuong-dat'] = 'https://batdongsan.com.vn/cho-thue-kho-nha-xuong-dat-tp-hcm'

    # BASE_URLS['HN-ban-can-ho-chung-cu'] = 'https://batdongsan.com.vn/ban-can-ho-chung-cu-ha-noi/'
    # BASE_URLS['HN-ban-nha-dat'] = 'https://batdongsan.com.vn/ban-nha-dat-ha-noi/'
    # BASE_URLS['HN-ban-dat-dat-nen'] = 'https://batdongsan.com.vn/ban-dat-dat-nen-ha-noi'
    # BASE_URLS['HN-ban-kho-nha-xuong'] = 'https://batdongsan.com.vn/ban-kho-nha-xuong-ha-noi/'
    # BASE_URLS['HN-ban-loai-bat-dong-san-khac'] = 'https://batdongsan.com.vn/ban-loai-bat-dong-san-khac-ha-noi/'

    # BASE_URLS['HN-cho-thue-can-ho-chung-cu'] = 'https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-ha-noi/'
    # BASE_URLS['HN-cho-thue-nha-rieng'] = 'https://batdongsan.com.vn/cho-thue-nha-rieng-ha-noi/'
    # BASE_URLS['HN-cho-thue-nha-mat-pho'] = 'https://batdongsan.com.vn/cho-thue-nha-mat-pho-ha-noi/'
    # BASE_URLS['HN-cho-thue-nha-tro-phong-tro'] = 'https://batdongsan.com.vn/cho-thue-nha-tro-phong-tro-ha-noi/'
    # BASE_URLS['HN-cho-thue-van-phong'] = 'https://batdongsan.com.vn/cho-thue-van-phong-ha-noi/'
    # BASE_URLS['HN-cho-thue-cua-hang-ki-ot'] = 'https://batdongsan.com.vn/cho-thue-cua-hang-ki-ot-ha-noi'
    # BASE_URLS['HN-cho-thue-kho-nha-xuong-dat'] = 'https://batdongsan.com.vn/cho-thue-kho-nha-xuong-dat-ha-noi'


    def start_requests(self):
        for domain, base_url in self.BASE_URLS.items():
            self.CURRENT_DOMAIN = domain
            self.CURRENT_BASE_URL = base_url
            print("CRAWL DATA IN DOMAIN: ", domain.upper(), '\n')
            yield scrapy.Request(url = base_url, callback = self.parse_url)


    def parse_url(self, response):
        article_urls = response.css('.Main .search-productItem .p-title a::attr(href)').extract()
        for url in article_urls:
            self.CURRENT_URL = self.PREFIX + url
            yield scrapy.Request(url = self.CURRENT_URL, callback=self.parse_article)
        
        next_page_url = response.xpath('//*[@id="form1"]/div[4]/div[6]/div[3]/div/div[3]/div/a[contains(., "...")]/@href').extract()[-1]
        if next_page_url is not None:
            yield scrapy.Request(self.PREFIX + next_page_url, callback=self.parse_url)


    def parse_article(self, response):
        article = dict()
        article['domain'] = self.CURRENT_DOMAIN
        article['url'] = self.CURRENT_URL
        article['tittle']           = response.xpath('//*[@id="product-detail"]/div[1]/h1/text()').extract()[0].strip()      
        article['address']          = response.xpath('//*[@id="product-detail"]/div[2]/span[1]/text()').extract()[0].strip()
        article['price']            = response.xpath('//*[@id="product-detail"]/div[2]/span[2]/span[1]/strong/text()').extract()[0].strip()
        article['usable_area']      = response.xpath('//*[@id="product-detail"]/div[2]/span[2]/span[2]/strong/text()').extract()[0].strip()
        # article['area']             = response.xpath('//*[@id="property-info"]/div[1]/ul[1]/li[3]/text()').extract()[0].strip()
        # article['publish_date']     = response.xpath('//*[@id="property-info"]/div[1]/ul[1]/li[4]/text()').extract()[0].strip()
        # article['real_estate_id']   = response.xpath('//*[@id="property-info"]/div[1]/ul[1]/li[5]/text()').extract()[0].strip()
        # article['bedroom']          = response.xpath('//*[@id="app"]/div[2]/main/article/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[4]/div/span/text()[3]').extract()[0].strip()
        # article['bathroom']         = response.xpath('//*[@id="app"]/div[2]/main/article/div[1]/div[2]/div[1]/div[2]/div[2]/div/div[5]/div/span/text()[3]').extract()[0].strip()
        # article['legal_papers']     = response.xpath('//*[@id="property-info"]/div[1]/ul[2]/li[3]/text()').extract()[0].strip()
        # article['direction']        = response.xpath('//*[@id="property-info"]/div[1]/ul[2]/li[4]/text()').extract()[0].strip()
        article['description']      = "\n".join(response.xpath('//*[@id="product-detail"]/div[5]/div[1]/text()').extract()).strip()
        # for key, text in article.items():
        #     print("{key}: {text}".format(key = key.upper(), text = text))

        return article

