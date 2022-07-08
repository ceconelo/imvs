from loguru import logger as log
import json

import scrapy

from ..items import DefaultItem


class OlximoveisSpider(scrapy.Spider):
    name = 'olximoveis'

    def __init__(self, filtro=None, **kwargs):
        super().__init__(**kwargs)

        log.info(f'Crawler iniciado: {self.name}')

        self.filtro = filtro
        self.filtro_aplicado = 'imoveis/venda/apartamentos'

        if filtro:
            self.filtro_aplicado = self.filtro
        log.info(f'Filtro aplicado: {self.filtro_aplicado}')
        self.keyword = self.filtro_aplicado.replace('/', '-')  # usado como nome do arquivo de saida

        self.page = 1
        self.url_base = 'https://df.olx.com.br/'
        self.url = f'{self.url_base}{self.filtro_aplicado}?o={self.page}'

        self.show_result = 0
        self.cards_imoveis = '//ul[@id="ad-list"]/li//a[@data-lurker-detail="list_id"]'
        self.url_imv = './@href'
        self.resultado_pesquisa = '//span[contains(text(), "resultados")]/text()'

    def start_requests(self):
        log.info(f'Acessando: {self.url}')
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        log.info(f'{response.xpath(self.resultado_pesquisa).get()}')
        total_pages = response.xpath('//p[contains(text(), "Página")]/text()[2]').get().split(' ')[2]

        cards_imoveis = response.xpath(self.cards_imoveis)
        for card in cards_imoveis:
            url_imv = card.xpath(self.url_imv).get()
            yield scrapy.Request(url=url_imv, callback=self.parse_item)

        if self.page < int(total_pages):
            self.page += 1
            url = f'{self.url_base}{self.filtro_aplicado}?o={self.page}'
            log.info(f'Acessando: {url}')
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_item(self, response):
        data = json.loads(response.xpath('//script[@id="initial-data"]/@data-json').get())
        imv = data['ad']

        item = DefaultItem()
        cod_imovel = imv['listId']
        item['data_publicacao'] = imv['listTime'].split('T')[0]
        item['atualizacao'] = ''
        item['cod_imovel'] = cod_imovel
        item['anunciante'] = imv["user"]["name"]
        item['creci'] = ''

        for i in imv['properties']:
            if i['name'] == 'condominio':
                item['valor_condominio'] = i['value']
            if i['name'] == 'iptu':
                item['valor_iptu'] = i['value']
            if i['name'] == 'size':
                item['area_privativa'] = i['value']
            if i['name'] == 'rooms':
                item['quartos'] = i['value']
            if i['name'] == 'bathrooms':
                item['banheiros'] = i['value']
            if i['name'] == 'garage_spaces':
                item['garagem'] = i['value']

        item['suites'] = ''

        item['endereco'] = imv['location']['address']
        item['bairro'] = imv['location']['neighbourhood']
        item['cidade'] = imv['location']['municipality']
        item['valor_imovel'] = imv['priceValue']

        item['area_total'] = ''
        item['valor_mt2'] = ''
        item['url'] = imv['friendlyUrl']

        yield item

