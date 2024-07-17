import logging


def setup_logging():
    logging.basicConfig(
        level=logging.WARNING,
        filename='tg_gpt_bot.log',
        format='%(asctime)s, %(levelname)s, %(message)s, %(funcName)s',
        encoding='utf-8'
    )
    return logging.getLogger(__name__)
