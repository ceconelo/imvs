from loguru import logger as log
import re
import os
import unicodedata


def slug(value, allow_unicode=False):
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')


def create_dirs(dirs):
    try:
        if not os.path.exists(dirs):
            os.makedirs(dirs)
            log.info(f'Diretório criado: {dirs}')
    except BaseException as err:
        log.error(f'Erro ao tentar criar diretório. {err}')
        raise CloseSpider('Ocorreu um erro ao tentar criar uma pasta no diretório OUTPUT')
