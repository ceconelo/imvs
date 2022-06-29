import argparse
import os, sys

from loguru import logger as log

from twisted.internet import reactor, defer

from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging


from config import FILTROS, SPIDERS

PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '{}'))
log.add(PATH.format('app.log'))


@defer.inlineCallbacks
def crawl():
    settings = get_project_settings()
    #configure_logging()
    runner = CrawlerRunner(settings)

    if SPIDERS is None:
        log.error('No arquivo config.py é necessário informar uma lista de spiders.')
        sys.exit(os.EX_IOERR)
    elif FILTROS is None:
        log.error('No arquivo config.py é necessário passar uma lista de filtros.')
        sys.exit(os.EX_IOERR)

    if type(FILTROS) is list:
        for f in FILTROS:

            for spider in SPIDERS:
                yield runner.crawl(spider, filtro=f)
        reactor.stop()


def main():
    crawl()
    reactor.run()


if __name__ == '__main__':
    log.info('Iniciando o sistema.')
    main()