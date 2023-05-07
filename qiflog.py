import logging

def init_log():
    global log

    logging.basicConfig(
        level=logging.WARN,
        format='%(levelname)s %(message)s'
    )
    return logging.getLogger()