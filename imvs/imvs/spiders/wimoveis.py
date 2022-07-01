import scrapy


class WimoveisSpider(scrapy.Spider):
    name = 'wimoveis'
    allowed_domains = ['x']
    start_urls = ['http://x/']

    def parse(self, response):
        pass
