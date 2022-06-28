import scrapy


class DefaultItem(scrapy.Item):

    cod_imovel = scrapy.Field()
    anunciante = scrapy.Field()
    creci = scrapy.Field()
    atualizacao = scrapy.Field()
    endereco = scrapy.Field()
    bairro = scrapy.Field()
    cidade = scrapy.Field()
    quartos = scrapy.Field()
    suites = scrapy.Field()
    garagem = scrapy.Field()
    dce = scrapy.Field()
    valor_imovel = scrapy.Field()
    area_privativa = scrapy.Field()
    area_total = scrapy.Field()
    valor_condominio = scrapy.Field()
    valor_mt2 = scrapy.Field()
    url = scrapy.Field()
    data_publicacao = scrapy.Field()
