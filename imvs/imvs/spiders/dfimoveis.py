from loguru import logger as log
from urllib.parse import urlparse

import scrapy

from scrapy.exceptions import CloseSpider

from scrapy.shell import inspect_response

from ..items import DefaultItem


class DfimoveisSpider(scrapy.Spider):
    name = 'dfimoveis'

    def __init__(self, filtro=None, **kwargs):
        super().__init__(**kwargs)

        log.info(f'Crawler iniciado: {self.name}')

        self.filtro = filtro
        self.filtro_aplicado = 'venda/df/todos/apartamento'

        if filtro:
            self.filtro_aplicado = self.filtro
        log.info(f'Filtro aplicado: {self.filtro_aplicado}')
        self.keyword = self.filtro_aplicado.replace('/', '-')  # usado como nome do arquivo de saida

        self.page = 1
        self.url = f'https://www.dfimoveis.com.br/{self.filtro_aplicado}?pagina={self.page}'

        self.show_result = 0
        self.cards_imoveis = '//div[@class="property js-propriedade"]'
        self.cod_imovel = '(//input[@id="idDoImovel"])[1]/@value'
        self.data_publicacao = ''
        self.anunciante = '(//img[@id="LogoDoAnunciante"])[1]/@alt'
        self.creci = '(//input[@id="creciDoAnunciante"])[1]/@value'
        self.atualizacao = '//*[contains(text(), " Última Atualização:")]/small/text()'
        self.endereco = '(//input[@id="enderecoDoImovel"])[1]/@value'
        self.bairro = '//*[contains(text(), "Bairro:")]/small/text()'
        self.cidade = '//*[contains(text(), "Cidade:")]/small/text()'
        self.quartos = '//*[contains(text(), "Quartos:")]/small/text()'
        self.suites = '//*[contains(text(), "Suítes:")]/small/text()'
        self.garagem = '//*[contains(text(), "Garagens:")]/small/text()'
        self.valor_imovel = '//*[contains(text(), "R$:")]/small/text()'
        self.area_privativa = '(//*[contains(text(), "Área Útil:")]/small/text())[1]'
        self.area_total = '//*[contains(text(), "Área Total:")]/small/text()'
        self.valor_condominio = '(//*[contains(text(), "Condomínio R$:")]/small/text())[1]'
        self.valor_mt2 = '(//*[contains(text(), "Valor R$ /m²:")]/small/text())[1]'
        self.url_imv = './@data-url'
        self.no_imvs = '//p[@class="sem-resultado"]'
        self.resultado_pesquisa = '//h1[@itemprop="name"]/text()'

    def start_requests(self):
        log.info(f'Acessando: {self.url}')
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response, **kwargs):
        if self.show_result == 0:
            log.info(f'Resultado da Pesquisa: {response.xpath(self.resultado_pesquisa).get()}')
            self.show_result = 1

        no_page = response.xpath(self.no_imvs).get()
        if no_page:
            log.info('Não existem mais imóveis.')
            raise CloseSpider('Todas as paginas foram raspadas.')

        parsed_uri = urlparse(response.url)
        url_base = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

        cards_imoveis = response.xpath(self.cards_imoveis)
        # log.debug(cards_imoveis)
        for card in cards_imoveis:
            url_imv = url_base + card.xpath(self.url_imv).get()
            yield scrapy.Request(url=url_imv, callback=self.parse_item)

        self.page += 1
        url = f'https://www.dfimoveis.com.br/{self.filtro_aplicado}?pagina={self.page}'
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
            log.error('Error ao pesquisar item.')
            log.error(err)
