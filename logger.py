from logtype import LogType
import logging, os

def log(message: str, type: int = LogType.INFO):
  color = "\033[37;1m" # white color (Info)
  logger = logging.getLogger('Zealdoc')
  logger.handlers = []
  handler = logging.StreamHandler(os.sys.stdout)

  if(type == LogType.ERROR):
    color = "\033[31;1m"
  if (type == LogType.WARNING):
    color = "\033[33;1m"
  if (type == LogType.DEBUG):
    color = "\033[34;1m"
  formatter = logging.Formatter('%(asctime)s | ' + color + '%(levelname)s\033[0m | \033[1m%(name)s\033[0m |-> %(message)s')
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  if(type == LogType.ERROR):
    logger.error(message)
  if (type == LogType.WARNING):
    logger.warning(message)
  if (type == LogType.DEBUG):
    logger.debug(message)
  if (type == LogType.INFO):
    logger.info(message)