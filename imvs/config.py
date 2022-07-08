from imvs.spiders.dfimoveis import DfimoveisSpider
from imvs.spiders.wimoveis import WimoveisSpider
from imvs.spiders.vivareal import VivarealSpider
from imvs.spiders.olximoveis import OlximoveisSpider

SPIDERS = [
    WimoveisSpider,
    DfimoveisSpider,
    VivarealSpider,
    OlximoveisSpider
]

'''
Informe abaixo todos os filtos que vai utilizar:
Basta fazer o filtro no site, copiar o filtro e colar baixo
'''
FILTRO_DFIMOVEIS = [
    'venda/df/todos/asa-norte/apartamento',
    #'venda/df/aguas-claras/apartamento',
    # 'venda/df/todos/apartamento',
    # 'venda/df/todos/kitnet'
]
FILTRO_WIMOVEIS = [
    # 'apartamentos-venda-asa-norte-brasilia.html',
    # 'apartamentos-venda-asa-sul-brasilia.html',
    # 'apartamentos-venda-noroeste-brasilia.html',
    # 'apartamentos-venda-sudoeste-brasilia.html',
    # 'apartamentos-venda-octogonal-brasilia.html',
    # 'apartamentos-venda-lago-norte-brasilia.html',
    # 'apartamentos-venda-park-sul-brasilia.html',
    # 'apartamentos-venda-guara-brasilia.html',
    'apartamentos-venda-aguas-claras-brasilia.html',
    # 'apartamentos-venda-cruzeiro-brasilia.html',
]
FILTRO_VIVAREAL = [
    'venda/distrito-federal/brasilia/apartamento_residencial/', # Somente esse filtro funciona
]
FILTRO_OLX = [
    #'imoveis/venda/apartamentos',
    #'distrito-federal-e-regiao/brasilia/imoveis/venda/apartamentos',
    'distrito-federal-e-regiao/outras-cidades/imoveis/venda/apartamentos'
]


