"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

from enum import Enum


class LogType(Enum):
  """Provides log types definition"""
  DEBUG = 0
  INFO = 1
  WARNING = 2
  ERROR = 3
