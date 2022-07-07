from loguru import logger as log
from time import sleep
import json

import scrapy

from ..items import DefaultItem


class VivarealSpider(scrapy.Spider):
    name = 'vivareal'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        log.info(f'Crawler iniciado: {self.name}')

        self.filtro_aplicado = 'venda/distrito-federal/brasilia/apartamento_residencial/'
        log.info(f'Filtro aplicado: {self.filtro_aplicado}')

        self.offset = 0
        self.limit = 36
        self.url_base = 'https://www.vivareal.com.br'
        self.keyword = self.filtro_aplicado.replace('/', '-')

        self.endpoint = "https://glue-api.vivareal.com/v2/listings?" \
                        "addressCity=Bras%C3%ADlia&" \
                        "addressLocationId=BR%3EDistrito%20Federal%3ENULL%3EBrasilia&" \
                        "addressNeighborhood=&" \
                        "addressState=Distrito%20Federal&" \
                        "addressCountry=Brasil&" \
                        "addressPointLat=-15.826691&" \
                        "addressPointLon=-47.92182&" \
                        "business=SALE&" \
                        "facets=amenities&" \
                        "unitTypes=APARTMENT&" \
                        "unitSubTypes=UnitSubType_NONE%2CDUPLEX%2CLOFT%2CSTUDIO%2CTRIPLEX&" \
                        "unitTypesV3=APARTMENT&" \
                        "usageTypes=RESIDENTIAL&" \
                        "listingType=USED&" \
                        "parentId=null&" \
                        "categoryPage=RESULT&" \
                        "includeFields=search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount)%2Cpage%2CseasonalCampaigns%2CfullUriFragments%2Cnearby(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cexpansion(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones%2Cphones)%2Cdevelopments(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))%2Cowners(search(result(listings(listing(displayAddressType%2Camenities%2CusableAreas%2CconstructionStatus%2ClistingType%2Cdescription%2Ctitle%2CunitTypes%2CnonActivationReason%2CpropertyType%2CunitSubTypes%2Cid%2Cportal%2CparkingSpaces%2Caddress%2Csuites%2CpublicationType%2CexternalId%2Cbathrooms%2CusageTypes%2CtotalAreas%2CadvertiserId%2Cbedrooms%2CpricingInfos%2CshowPrice%2Cstatus%2CadvertiserContact%2CvideoTourLink%2CwhatsappNumber%2Cstamps)%2Caccount(id%2Cname%2ClogoUrl%2ClicenseNumber%2CshowAddress%2ClegacyVivarealId%2Cphones)%2Cmedias%2CaccountLink%2Clink))%2CtotalCount))&" \
                        "size=36&" \
                        "from={}&" \
                        "developmentsSize=5&" \
                        "levels=CITY%2CUNIT_TYPE"
        self.headers = {
            'authority': 'glue-api.vivareal.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.vivareal.com.br',
            'pragma': 'no-cache',
            'referer': 'https://www.vivareal.com.br/',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'cross-site',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
            'x-domain': 'www.vivareal.com.br',
            # 'Cookie': '__cfruid=9e1427bc34a59bfcd0f3aa23d581e6f7e321e4e0-1657135142'
        }

    def start_requests(self):
        yield scrapy.Request(url=self.endpoint.format(str(self.offset)), headers=self.headers, callback=self.parse)

    def parse(self, response, **kwargs):
        data = json.loads(response.text)
        page = data['page']['uriPagination']['page']
        log.info(f'Acessando página: {page}')

        for imv in data['search']['result']['listings']:
            item = DefaultItem()
            cod_imovel = imv['listing']['id']
            item['data_publicacao'] = ''
            item['atualizacao'] = ''
            item['cod_imovel'] = cod_imovel
            item['anunciante'] = imv["account"]["name"]
            item['creci'] = imv['account']['licenseNumber']
            item['endereco'] = imv['link']['data']['street']
            item['bairro'] = imv['link']['data']['neighborhood']
            item['cidade'] = imv['link']['data']['city']
            item['quartos'] = imv['listing']['bedrooms'][0]
            item['banheiros'] = imv['listing']['bathrooms'][0]
            item['suites'] = imv['listing']['suites']
            item['garagem'] = imv['listing']['parkingSpaces']
            item['valor_imovel'] = imv['listing']['pricingInfos'][0]['price']
            if 'yearlyIptu' in imv['listing']['pricingInfos'][0]:
                item['valor_iptu'] = imv['listing']['pricingInfos'][0]['yearlyIptu']
            if 'monthlyCondoFee' in imv['listing']['pricingInfos'][0]:
                item['valor_condominio'] = imv['listing']['pricingInfos'][0]['monthlyCondoFee']
            item['area_privativa'] = imv['listing']['usableAreas'][0]
            item['area_total'] = imv['listing']['totalAreas']
            item['valor_mt2'] = ''
            item['url'] = self.url_base + imv['link']['href']

            yield item

        total_imvs = data['page']['uriPagination']['total']
        page_from = self.offset + self.limit
        sleep(2)
        if page_from < total_imvs:
            self.offset = page_from
            log.debug(f'offset: {self.offset}')
            yield scrapy.Request(url=self.endpoint.format(str(self.offset)), headers=self.headers, callback=self.parse)
