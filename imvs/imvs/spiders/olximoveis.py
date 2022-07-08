from loguru import logger as log
import scraper_helper as helper
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
        # self.anunciante = '//div[@id="miniprofile"]/div/div/div/div[2]/div[2]/span/text()'
        # self.data_publicacao = '((//*[contains(text(), "Publicado em") ])[2]/text())[2]'
        # self.endereco = '//dt[contains(text(), "Logradouro")]/following-sibling::dd/text()'
        # self.bairro = '//dt[contains(text(), "Bairro")]/following-sibling::dd/text()'
        # self.cidade = '//dt[contains(text(), "Município")]/following-sibling::dd/text()'
        # self.quartos = '//dt[contains(text(), "Quartos")]/following-sibling::a/text()'
        # sefl.banheiros = '//dt[contains(text(), "Banheiros")]/following-sibling::dd/text()'
        # self.garagem = '//dt[contains(text(), "Vagas na garagem")]/following-sibling::dd/text()'
        # self.area_privativa = '//dt[contains(text(), "Área útil")]/following-sibling::dd/text()'
        # self.valor_imovel = '(//h2[contains(text(), "R$")])[1]/text()'

        # self.cod_imovel = '(//input[@id="idDoImovel"])[1]/@value'
        #
        # self.creci = '(//input[@id="creciDoAnunciante"])[1]/@value'
        # self.atualizacao = '//*[contains(text(), " Última Atualização:")]/small/text()'
        #
        # self.suites = '//*[contains(text(), "Suítes:")]/small/text()'
        #
        #
        # self.area_total = '//*[contains(text(), "Área Total:")]/small/text()'
        # self.valor_condominio = '(//*[contains(text(), "Condomínio R$:")]/small/text())[1]'
        # self.valor_mt2 = '(//*[contains(text(), "Valor R$ /m²:")]/small/text())[1]'

        # self.no_imvs = '//p[@class="sem-resultado"]'
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

    def handle_error(self, failure):
        if failure.check(HttpError):
            response = failure.value.response
            if response.status == 429:  # Too Many Requests
                # open_in_browser(response)  # for debugging 429
                raise CloseSpider('Banned?')  # Comment out for proxies
