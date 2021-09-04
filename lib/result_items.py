"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import os

# ULauncher
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

# Local
import lib.i18n

_ = lib.i18n.__

class ResultItems:
  """Gives result items to pass to ULauncher"""

  @staticmethod
  def assert_valid_docset(item):
    """Check items has required attributes"""

    attrs = ["id", "name", "icon", "icon2"]
    for attr in attrs:
      if attr not in item:
        raise Exception("Missing %s in %s" % (attr, item))

  @staticmethod
  def docset_searchforin_result(item, query):
    """Creates a docset 'search for in' result
    Zeal doc action example dash-plugin://keys=python,django&query=string
    """

    ResultItems.assert_valid_docset(item)
    return ExtensionResultItem(
        icon=item["icon2"],
        name=_("Search for %s in %s") % (query, item["name"]),
        on_enter=OpenAction(
            path="dash-plugin:keys=%s&query=%s" % (item["id"], query)
        ),
    )

  @staticmethod
  def docset_result(item):
    """Creates a docset result"""

    ResultItems.assert_valid_docset(item)
    return ExtensionResultItem(
        icon=item["icon2"],
        name=item["name"],
        description=_("Search in %s") % (item["name"]),
        on_enter=ExtensionCustomAction(item, keep_app_open=True),
    )

  @staticmethod
  def docset_change_result():
    """Creates a docset result"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    sep = os.path.sep

    return ExtensionResultItem(
        icon=dir_path + sep + ".." + sep + "images" + os.path.sep + "icon.png",
        name=_("Look in another docset"),
        on_enter=ExtensionCustomAction({"reset": True}, keep_app_open=True),
    )
