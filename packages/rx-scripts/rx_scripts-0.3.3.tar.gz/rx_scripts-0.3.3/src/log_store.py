import logzero

from logzero import logger as log
#------------------------------------------------------------
class log_store:
    d_logger = {}
    d_levels = {}
    @staticmethod
    def add_logger(name=None):
        if name is None:
            log.error(f'Logger name missing')
            raise
        elif name in log_store.d_logger:
            log.error(f'Logger name {name} already found')
            raise

        level          = logzero.INFO if name not in log_store.d_levels else log_store.d_levels[name] 
        logger         = logzero.setup_logger(name=name, level=level)
        log_store.d_logger[name] = logger

        return logger

    @staticmethod
    def set_level(name, value):
        log_store.d_levels[name] = value

    @staticmethod
    def show_loggers():
        log.info(f'{"Name":<20}{"Level":<20}')
        for name, logger in log_store.d_logger.items():
            log.info(f'{name:<20}{logger.level:<20}')
#------------------------------------------------------------
