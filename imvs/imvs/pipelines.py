import os
from loguru import logger as log
from datetime import datetime

from scrapy.exporters import JsonItemExporter
from scrapy.exporters import CsvItemExporter

from .utils import create_dirs, slug


class DefaultPipeline(object):
    def __init__(self):
        self.exporter_json = None
        self.exporter_csv = None
        self.path_output = None
        self.path_base = None
        self.today = datetime.now().strftime("%Y-%m-%d")

    def open_spider(self, spider):
        self.path_base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', spider.name))
        self.path_output = os.path.abspath(os.path.join(os.path.dirname(__file__), 'output', spider.name, '{}'))

        create_dirs(self.path_base)
        self.fp_json = open(self.path_output.format(f'{slug(spider.keyword)}-{self.today}.json'), 'wb')  # noqa
        self.fp_csv = open(self.path_output.format(f'{slug(spider.keyword)}-{self.today}.csv'), 'wb')  # noqa
        self.exporter_json = JsonItemExporter(self.fp_json, ensure_ascii=False, encoding='utf-8')
        self.exporter_csv = CsvItemExporter(self.fp_csv, encoding='utf-8')
        self.exporter_json.start_exporting()
        self.exporter_csv.start_exporting()

    def process_item(self, item, spider):
        try:
            log.info(f'Um novo item foi processado: Cod. Imóvel - {item["cod_imovel"]}')
            self.exporter_json.export_item(item)
            self.exporter_csv.export_item(item)
            return item
        except BaseException as err:
            log.error(f'Erro ao processar o item: Cod. Imóvel - {item["cod_imovel"]}')
            log.error(f'Erro ao processar o item: {err}')

    def close_spider(self, spider):
        self.exporter_json.finish_exporting()
        self.exporter_csv.finish_exporting()
        self.fp_json.close()
        self.fp_csv.close()
        log.info('Crawler finalizado.')
