"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import os
import traceback

# ULauncher
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    ItemEnterEvent,
)
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

# Local
from docsets import Docsets
from logger import log
from logtype import LogType
from variables import Variables
from result_items import ResultItems

dir_path = os.path.dirname(os.path.realpath(__file__))
Vars = Variables()
log(Vars.query, LogType.WARNING)


class Zealdocs(Extension):
  """Zealdoc plugin class"""

  def __init__(self):
    super(Zealdocs, self).__init__()
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    self.subscribe(ItemEnterEvent, ItemEnterEventListener())  # <-- add this line
    Docsets.parse_docsets()


class KeywordQueryEventListener(EventListener):
  """On type event"""

  def on_event(self, event, extension):
    try:
      log(extension, LogType.DEBUG)
      log("Selected and items ? %d" % (Vars.is_sel))
      query = Vars.query = event.query.replace("zd ", "", 1)
      log(query, LogType.WARNING)
      ext_results_sorted = []

      if Vars.is_sel:
        # open with dash-plugin://keys=python,django&query=string
        log("EXEC SEARCH", LogType.WARNING)
        Vars.query = query.replace(Vars.docset_query, "", 1).strip()

        return RenderResultListAction(
            [
                ResultItems.docset_searchforin_result(Vars.sel_docset, Vars.query),
                ResultItems.docset_change_result(),
            ]
        )
      else:
        log("LIST DOCSETS", LogType.WARNING)
        query = event.query.replace("zd ", "", 1)

        # If User types a docset ID with keyword
        if Docsets.docsetDict.get(query) or Vars.sel_docset:

          # filter query to remove docset ID if needed or assign a
          # selected docset
          if not Vars.is_sel:
            Vars.is_sel = True
            Vars.sel_docset = Docsets.docsetDict.get(query)
          else:
            Vars.query = query.replace(
                Vars.sel_docset["id"], "", 1
            ).strip()

          return RenderResultListAction(
              [
                  ResultItems.docset_searchforin_result(Vars.sel_docset, query),
                  ResultItems.docset_change_result(),
              ]
          )

        # User would select a docset
        else:
          Vars.is_sel = False
          Vars.sel_docset = {}
          for item in Docsets.sort_docsets(event.query):
            ext_results_sorted.append(ResultItems.docset_result(item['docset']))

      # return docsets sorted by score
      return RenderResultListAction(ext_results_sorted)
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


class ItemEnterEventListener(EventListener):
  """When an item is selected"""

  def on_event(self, event, extension):
    try:
      data = event.get_data()
      ext_results_sorted = []
      # do additional actions here...
      log(data, LogType.DEBUG)
      log(event, LogType.DEBUG)

      if "reset" in data:
        # print docsets
        log("LIST DOCSETS RESET", LogType.WARNING)
        Vars.is_sel = False
        Vars.sel_docset = {}
        for item in Docsets.sort_docsets(Vars.query):
          ext_results_sorted.append(
              ResultItems.docset_result(item["docset"])
          )
        return RenderResultListAction(ext_results_sorted)
      else:
        log("QUERY IN DOCSET", LogType.WARNING)
        # reset query to allow search in a specific docset
        Vars.query = ""
        Vars.is_sel = True
        Vars.sel_docset = data
        # store docset typed keyword
        Vars.docset_query = Vars.sel_docset['id']
        # you may want to return another list of results
        return RenderResultListAction(
            [
                ResultItems.docset_searchforin_result(Vars.sel_docset, Vars.query),
                ResultItems.docset_change_result(),
            ]
        )
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


if __name__ == "__main__":
  Zealdocs().run()
