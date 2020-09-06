"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Local
from logger import log
from logtype import LogType


class Variables:
  """Variables storage class"""

  def __init__(self):
    self.is_sel = False
    self.sel_docset = {}
    self.query = ''
    self.docset_query = ''
    self.docsets = []

  def __getitem__(self, name):
    self.assert_attribute_exists(name)
    return getattr(self, name)

  def __setitem__(self, name, value):
    self.assert_attribute_exists(name)
    return setattr(self, name, value)

  def __delitem__(self, name):
    self.assert_attribute_exists(name)
    return delattr(self, name)

  def __contains__(self, name):
    return hasattr(self, name)

  def assert_attribute_exists(self, name):
    """Test if obj has an attribute"""
    if not hasattr(self, name):
      error_string = 'Unknown variable %s' % name
      log(error_string, LogType.ERROR)
      raise Exception(error_string)
