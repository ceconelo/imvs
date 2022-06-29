from imvs.spiders.dfimoveis import DfimoveisSpider

SPIDERS = [
    DfimoveisSpider,
    ]

'''
Informe abaixo todos os filtos que vai utilizar:
Basta fazer o filtro no site, copiar o filtro e colar baixo
'''
FILTROS = [
    'venda/go/aparecida-de-goiania/cardoso/apartamento/2-quartos',
    'venda/df/alphaville/alphaville-brasilia/apartamento/3-quartos',
    'venda/df/aguas-claras/ade/kitnet?valorinicial=72000&valorfinal=108000'
    # 'venda/df/todos/apartamento',
    # 'venda/df/todos/kitnet'
]

