import argparse
import os, sys

from loguru import logger as log

from twisted.internet import reactor, defer

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging

from config import FILTRO_WIMOVEIS, FILTRO_DFIMOVEIS, FILTRO_VIVAREAL, FILTRO_OLX, SPIDERS

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '{}'))
log.add(PATH.format('app.log'))


@defer.inlineCallbacks
def crawl():
    global filtro
    settings = get_project_settings()
    #configure_logging()
    runner = CrawlerRunner(settings)

    if SPIDERS is None:
        log.error('No arquivo config.py é necessário informar uma lista de spiders.')
        sys.exit(os.EX_IOERR)
    elif FILTRO_WIMOVEIS is None:
        log.error('No arquivo config.py é necessário passar uma lista de filtros.')
        sys.exit(os.EX_IOERR)
    elif FILTRO_DFIMOVEIS is None:
        log.error('No arquivo config.py é necessário passar uma lista de filtros.')
        sys.exit(os.EX_IOERR)
    elif FILTRO_VIVAREAL is None:
        log.error('No arquivo config.py é necessário passar uma lista de filtros.')
        sys.exit(os.EX_IOERR)
    elif FILTRO_OLX is None:
        log.error('No arquivo config.py é necessário passar uma lista de filtros.')
        sys.exit(os.EX_IOERR)

    for spider in SPIDERS:
        if spider.__name__ == 'DfimoveisSpider':
            filtro = FILTRO_DFIMOVEIS
        elif spider.__name__ == 'WimoveisSpider':
            filtro = FILTRO_WIMOVEIS
        elif spider.__name__ == 'VivarealSpider':
            filtro = FILTRO_VIVAREAL
        elif spider.__name__ == 'OlximoveisSpider':
            filtro = FILTRO_OLX

        for f in filtro:
            #log.debug(f'Crawling {spider.__name__} - {f}')
            yield runner.crawl(spider, filtro=f)
    reactor.stop()


def main():
    crawl()
    reactor.run()


if __name__ == '__main__':
    log.info('Iniciando o sistema.')
    main()
