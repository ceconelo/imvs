import time
from time import sleep

from uc_browser.browser_v2 import BrowserV2
from selenium.webdriver.support.ui import WebDriverWait
#import cfscrape
import cloudscraper

from urllib.parse import urlparse
from http import HTTPStatus
from loguru import logger as log

import json

from scrapy.exceptions import CloseSpider
import scrapy

from ..items import DefaultItem


class WimoveisSpider(scrapy.Spider):
    name = 'wimoveis'

    start_urls = ['http://httpbin.org/ip']

    def __init__(self, filtro=None, **kwargs):
        global bairro, id

        super().__init__(**kwargs)
        log.info(f'Crawler iniciado: {self.name}')

        self.id_bairros = {
            'asa-norte': '42704',  # apartamentos-venda-asa-norte-brasilia.html
            'asa-sul': '42705',  # apartamentos-venda-asa-sul-brasilia.html
            'noroeste': '42748',  # apartamentos-venda-noroeste-brasilia.html
            'sudoeste': '42750',  # apartamentos-venda-sudoeste-brasilia.html
            'octogonal': '42703',  # apartamentos-venda-octogonal-brasilia.html
            'lago-norte': '42709',  # apartamentos-venda-lago-norte-brasilia.html
            'park-sul': '42711',  # apartamentos-venda-park-sul-brasilia.html
            'guara': '80222',  # apartamentos-venda-guara-brasilia.html
            'aguas-claras': '80218',  # apartamentos-venda-aguas-claras-brasilia.html
            'cruzeiro': '80252',  # apartamentos-venda-cruzeiro-brasilia.html
        }

        self.page = 1
        self.filtro_aplicado = 'apartamentos-venda-brasilia-df.html'

        if filtro:
            for key, value in self.id_bairros.items():
                if key in filtro:
                    bairro = key
                    id = value
            log.debug(f'Bairro: {bairro}')
            log.debug(f'Id Bairro: {id}')

            self.filtro_aplicado = f'apartamentos-venda-{bairro}-brasilia-pagina-'

        log.info(f'Filtro aplicado: {self.filtro_aplicado}')
        self.keyword = self.filtro_aplicado.replace('/', '-')  # usado como nome do arquivo de saida

        self.url_base = f'https://www.wimoveis.com.br/{self.filtro_aplicado}-{self.page}.html'
        self.endpoint = 'https://www.wimoveis.com.br/rplis-api/postings'

        self.scraper = cloudscraper.create_scraper(delay=10, browser={'custom': 'Imvs'})
        log.info('Abrindo navegador...')
        self.web = BrowserV2()

        self.headers = {
            'content-type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
         }

        self.payload = json.dumps({
            'q': None,
            'direccion': None,
            'moneda': None,
            'preciomin': None,
            'preciomax': None,
            'services': '',
            'general': '',
            'searchbykeyword': '',
            'amenidades': '',
            'caracteristicasprop': None,
            'comodidades': '',
            'disposicion': None,
            'roomType': '',
            'outside': '',
            'areaPrivativa': '',
            'areaComun': '',
            'multipleRets': '',
            'tipoDePropiedad': '2',
            'subtipoDePropiedad': None,
            'tipoDeOperacion': '1',
            'garages': None,
            'antiguedad': None,
            'expensasminimo': None,
            'expensasmaximo': None,
            'habitacionesminimo': 0,
            'habitacionesmaximo': 0,
            'ambientesminimo': 0,
            'ambientesmaximo': 0,
            'banos': None,
            'superficieCubierta': 1,
            'idunidaddemedida': 1,
            'metroscuadradomin': None,
            'metroscuadradomax': None,
            'tipoAnunciante': 'ALL',
            'grupoTipoDeMultimedia': '',
            'publicacion': None,
            'sort': 'relevance',
            'etapaDeDesarrollo': '',
            'auctions': None,
            'polygonApplied': None,
            'idInmobiliaria': None,
            'banks': None,
            f'pagina': self.page,
            'city': None,
            'province': None,
            'zone': None,
            f'valueZone': id,
            'subZone': None,
            'coordenates': None, })

        self.web.navigate(url=self.url_base)
        log.info(f'Navegando na página: {self.url_base}')

        WebDriverWait(self.web.driver, 15).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete")
        log.info('Pagina carregada com sucesso!')

        self.response = self.scraper.post(self.endpoint, cookies=self.web.get_cookies(), headers=self.headers,
                                          data=self.payload)
        if self.response.status_code == HTTPStatus.OK:
            log.info('Requisição realizada com sucesso!')
            self.data = json.loads(self.response.text)
        else:
            log.error(f'Erro ao realizar requisição! Codigo: {self.response.status_code}')
            self.web.close_driver()
            CloseSpider('Erro ao realizar requisição!')

    def parse(self, response, **kwargs):
        global cod_imovel, url_imv

        total_paginas = self.data["paging"]["totalPages"]
        log.info(f'Total de paginas: {total_paginas}')

        parsed_uri = urlparse(self.url_base)
        url_base = '{uri.scheme}://{uri.netloc}'.format(uri=parsed_uri)

        while self.page <= total_paginas:
            log.info('Pagina atual: {}'.format(self.data['paging']['currentPage']))
            log.info('Parsing...')

            for imv in self.data['listPostings']:
                try:
                    item = DefaultItem()
                    cod_imovel = imv['postingId']
                    url_imv = url_base + imv['url']

                    item['data_publicacao'] = ''
                    item['atualizacao'] = imv['modified_date'].split('T')[0]
                    item['cod_imovel'] = cod_imovel

                    if imv['publisher'] is not None:
                        if 'name' in imv['publisher']:
                            item['anunciante'] = imv['publisher']['name']
                        if 'license' in imv['publisher']:
                            item['creci'] = imv['publisher']['license']

                    if imv['postingLocation'] is not None:
                        if 'address' in imv['postingLocation']:
                            if imv['postingLocation']['address'] is not None:
                                if 'name' in imv['postingLocation']['address']:
                                    item['endereco'] = imv['postingLocation']['address']['name']

                    item['bairro'] = imv['postingLocation']['location']['name']
                    item['cidade'] = imv['postingLocation']['location']['parent']['name']

                    if imv['mainFeatures'] is not None:
                        if 'CFT100' in imv['mainFeatures']:
                            item['area_total'] = imv['mainFeatures']['CFT100']['value']
                        if 'CFT101' in imv['mainFeatures']:
                            item['area_privativa'] = imv['mainFeatures']['CFT101']['value']
                        if 'CFT2' in imv['mainFeatures']:
                            item['quartos'] = imv['mainFeatures']['CFT2']['value']
                        if 'CFT3' in imv['mainFeatures']:
                            item['banheiros'] = imv['mainFeatures']['CFT3']['value']
                        if 'CFT4' in imv['mainFeatures']:
                            item['suites'] = imv['mainFeatures']['CFT4']['value']
                        if 'CFT7' in imv['mainFeatures']:
                            item['garagem'] = imv['mainFeatures']['CFT7']['value']
                        if 'CFT5' in imv['mainFeatures']:
                            item['idade_imovel'] = imv['mainFeatures']['CFT5']['value']

                    item['valor_imovel'] = imv['priceOperationTypes'][0]['prices'][0]['formattedAmount']

                    if imv['expenses'] is not None:
                        item['valor_condominio'] = imv['expenses']['amount']
                    item['valor_mt2'] = ''
                    item['url'] = url_imv

                    yield item
                except BaseException as err:
                    log.error(f'Erro ao parsear o imv: {cod_imovel}')
                    log.error(f'Url do imv: {url_imv}')
                    log.error(f'Erro: {err}', exc_info=True)

            self.page += 1
            url = f'https://www.wimoveis.com.br/{self.filtro_aplicado}{self.page}.html'
            self.web.navigate(url=url)
            log.info(f'Navegando na página: {url}')

            WebDriverWait(self.web.driver, 15).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete")
            log.info('Pagina carregada com sucesso!')

            # mudando a pagina no header
            payload = json.loads(self.payload)
            payload['pagina'] = self.page
            payload = json.dumps(payload)

            self.response = self.scraper.post(self.endpoint, cookies=self.web.get_cookies(), headers=self.headers,
                                              data=payload)
            if self.response.status_code == HTTPStatus.OK:
                log.info('Requisição realizada com sucesso!')
                self.data = json.loads(self.response.text)
            else:
                log.error(f'Erro ao realizar requisição! Codigo: {self.response.status_code}')
                CloseSpider('Erro ao realizar requisição!')
            sleep(1.5)

    def close(self, reason):
        self.web.close_driver()
