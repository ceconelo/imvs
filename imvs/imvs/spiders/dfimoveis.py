from loguru import logger as log
from urllib.parse import urlparse

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.exceptions import CloseSpider

from scrapy.shell import inspect_response

from ..items import DefaultItem


class DfimoveisSpider(CrawlSpider):
    name = 'dfimoveis'
    log.info(f'Crawler iniciado: {name}')

    page = 1
    keyword = 'kitnet'
    #allowed_domains = ['https://www.dfimoveis.com.br/']
    url = f'https://www.dfimoveis.com.br/venda/df/todos/{keyword}?pagina={page}'

    cards_imoveis = '//div[@class="property js-propriedade"]'
    cod_imovel = '(//input[@id="idDoImovel"])[1]/@value'
    data_publicacao = ''
    anunciante = '(//img[@id="LogoDoAnunciante"])[1]/@alt'
    creci = '(//input[@id="creciDoAnunciante"])[1]/@value'
    atualizacao = '//*[contains(text(), " Última Atualização:")]/small/text()'
    endereco = '(//input[@id="enderecoDoImovel"])[1]/@value'
    bairro = '//*[contains(text(), "Bairro:")]/small/text()'
    cidade = '//*[contains(text(), "Cidade:")]/small/text()'
    quartos = '//*[contains(text(), "Quartos:")]/small/text()'
    suites = '//*[contains(text(), "Suítes:")]/small/text()'
    garagem = '//*[contains(text(), "Garagens:")]/small/text()'
    valor_imovel = '//*[contains(text(), "R$:")]/small/text()'
    area_privativa = '(//*[contains(text(), "Área Útil:")]/small/text())[1]'
    area_total = '//*[contains(text(), "Área Total:")]/small/text()'
    valor_condominio = '(//*[contains(text(), "Condomínio R$:")]/small/text())[1]'
    valor_mt2 = '(//*[contains(text(), "Valor R$ /m²:")]/small/text())[1]'
    url_imv = './@data-url'
    no_imvs = '//p[contains(text(), "Neste momento não temos imóveis com essa segmentação")]'

    def start_requests(self):
        log.info(f'Acessando: {self.url}')
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        no_page = response.xpath(self.url_imv).get()
        if no_page:
            log.info('Não existem mais imóveis.')
            raise CloseSpider('Todas as paginas foram raspadas.')

        parsed_uri = urlparse(response.url)
        url_base = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

        cards_imoveis = response.xpath(self.cards_imoveis)
        for card in cards_imoveis:
            url_imv = url_base + card.xpath(self.url_imv).get()

            yield scrapy.Request(url=url_imv, callback=self.parse_item)

        self.page = self.page + 1
        url = f'https://www.dfimoveis.com.br/venda/df/todos/{self.keyword}?pagina={self.page}'
        log.info(f'Acessando: {url}')
        yield scrapy.Request(url=url, callback=self.parse)

    def parse_item(self, response):
        try:
            item = DefaultItem()
            cod_imovel = response.xpath(self.cod_imovel).get()
            item['data_publicacao'] = ''
            item['atualizacao'] = response.xpath(self.atualizacao).get()
            item['cod_imovel'] = cod_imovel
            item['anunciante'] = response.xpath(self.anunciante).get()
            item['creci'] = response.xpath(self.creci).get()
            item['endereco'] = response.xpath(self.endereco).get()
            item['bairro'] = response.xpath(self.bairro).get()
            item['cidade'] = response.xpath(self.cidade).get()
            item['quartos'] = response.xpath(self.quartos).get()
            item['suites'] = response.xpath(self.suites).get()
            item['garagem'] = response.xpath(self.garagem).get()
            item['valor_imovel'] = response.xpath(self.valor_imovel).get()
            item['area_privativa'] = response.xpath(self.area_privativa).get()
            item['area_total'] = response.xpath(self.area_total).get()
            item['valor_condominio'] = response.xpath(self.valor_condominio).get()
            item['valor_mt2'] = response.xpath(self.valor_mt2).get()
            item['url'] = response.url

            yield item
        except BaseException as err:
            log.error('Error ao processar item.')
            log.error(err)
