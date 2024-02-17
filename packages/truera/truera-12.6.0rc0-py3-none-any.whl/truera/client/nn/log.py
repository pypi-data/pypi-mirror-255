import logging

logger = logging.getLogger(name="truera-nn")

debug = logger.debug
info = logger.info
warning = logger.warning
error = logger.error
critical = logger.critical


def configure(level=1, root_level=logging.WARNING):
    global logger
    logging.basicConfig(
        format=
        '%(levelname)s:%(name)s:%(filename)s:%(lineno)s(%(funcName)s): %(message)s',
        level=root_level
    )
    logger.setLevel(level)

    logger.info("level={level}".format(level=level))
    logger.info("root level={root_level}".format(root_level=root_level))
