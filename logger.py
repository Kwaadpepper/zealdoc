"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

import os
import logging
from logtype import LogType


def log(message: str, log_type: int = LogType.INFO):
  """
    Log a message in std.out on a specified channel.
    Default is info

    message: A message string

    log_type: A channel of LogType (INFO, DEBUG, WARNING, ERROR)
  """
  color = "\033[37;1m"  # white color (Info)
  logger = logging.getLogger("Zealdoc")
  logger.handlers = []
  handler = logging.StreamHandler(os.sys.stdout)

  if log_type == LogType.ERROR:
    color = "\033[31;1m"
  if log_type == LogType.WARNING:
    color = "\033[33;1m"
  if log_type == LogType.DEBUG:
    color = "\033[34;1m"
  formatter = logging.Formatter(
      "%(asctime)s | "
      + color
      + "%(levelname)s\033[0m | \033[1m%(name)s\033[0m |-> %(message)s"
  )
  handler.setFormatter(formatter)
  logger.addHandler(handler)
  if log_type == LogType.ERROR:
    logger.error(message)
  if log_type == LogType.WARNING:
    logger.warning(message)
  if log_type == LogType.DEBUG:
    logger.debug(message)
  if log_type == LogType.INFO:
    logger.info(message)
