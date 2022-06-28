import os
from loguru import logger as log
from datetime import datetime

from scrapy.exporters import JsonItemExporter

from .utils import create_dirs, slug


class DefaultPipeline(object):
    def __init__(self):
        self.exporter = None
        self.path_output = None
        self.path_base = None
        self.today = datetime.now().strftime("%Y-%m-%d")

    def open_spider(self, spider):
        self.path_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', spider.name))
        self.path_output = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', spider.name, '{}'))

        create_dirs(self.path_base)
        self.fp = open(self.path_output.format(f'{slug(spider.keyword)}-{self.today}.json'), 'wb')  # noqa
        self.exporter = JsonItemExporter(self.fp, ensure_ascii=False, encoding='utf-8')
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        log.info(f'Um novo item foi processado: {item["cod_imovel"]}')
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.fp.close()
        log.info('Crawler finalizado.')
