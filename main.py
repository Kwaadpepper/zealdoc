"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import traceback

# ULauncher
from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import (
    KeywordQueryEvent,
    ItemEnterEvent,
)
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.Response import Response
from ulauncher.api.shared.action.SetUserQueryAction import SetUserQueryAction

# Local
from docsets import Docsets
from logger import log
from logtype import LogType
from variables import Variables
from result_items import ResultItems
# from change_query import update_query


class Zealdocs(Extension):
  """Zealdoc plugin class"""

  variables = Variables()

  def __init__(self):
    super().__init__()
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    self.subscribe(ItemEnterEvent, ItemEnterEventListener())  # <-- add this line
    Docsets.parse_docsets()

    log('preferences  %s' % self.preferences, LogType.WARNING)

  def update_ui_query_string(self, event, query):
    """Changes Ui query string"""
    log('preferences  %s' % self.variables.keyword , LogType.WARNING)

    # pylint: disable=(protected-access)
    self._client.send(Response(event, SetUserQueryAction(self.variables.keyword + ' ' + query)))


class KeywordQueryEventListener(EventListener):
  """On type event"""

  def on_event(self, event, extension):
    try:
      vrs = extension.variables
      vrs.keyword = event.query.split(' ')[0]
      query = vrs.query = event.query.replace(vrs.keyword + " ", "", 1)
      ext_results_sorted = []

      if vrs.is_sel:
        # open with dash-plugin://keys=python,django&query=string
        log("EXEC SEARCH", LogType.DEBUG)
        vrs.query = query.strip()

        return RenderResultListAction(
            [
                ResultItems.docset_searchforin_result(
                    vrs.sel_docset, vrs.query
                ),
                ResultItems.docset_change_result(),
            ]
        )

      query = event.query.replace(vrs.keyword + " ", "", 1)

      # If User types a docset ID with keyword
      if Docsets.docsetDict.get(query):
        log("SELECTED A DOCSET", LogType.DEBUG)
        # filter query to remove docset ID if needed or assign a
        # selected docset
        vrs.is_sel = True
        vrs.sel_docset = Docsets.docsetDict.get(query)
        vrs.docset_query = vrs.sel_docset["id"]
        # Update UI query string
        extension.update_ui_query_string(event, '')

        return RenderResultListAction(
            [
                ResultItems.docset_searchforin_result(
                    vrs.sel_docset, ''
                ),
                ResultItems.docset_change_result(),
            ]
        )

      # ELSE User would select a docset
      log("LIST DOCSETS", LogType.DEBUG)
      vrs.is_sel = False
      vrs.sel_docset = {}
      for item in Docsets.sort_docsets(event.query):
        ext_results_sorted.append(ResultItems.docset_result(item["docset"]))

      # return docsets sorted by score
      return RenderResultListAction(ext_results_sorted)
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


class ItemEnterEventListener(EventListener):
  """When an item is selected"""

  def on_event(self, event, extension):
    try:
      vrs = extension.variables
      data = event.get_data()
      ext_results_sorted = []
      # do additional actions here...
      log(data, LogType.DEBUG)
      log(event, LogType.DEBUG)

      if "reset" in data:
        # print docsets
        log("LIST DOCSETS RESET", LogType.DEBUG)
        vrs.is_sel = False
        vrs.sel_docset = {}
        for item in Docsets.sort_docsets(vrs.query):
          ext_results_sorted.append(ResultItems.docset_result(item["docset"]))
        return RenderResultListAction(ext_results_sorted)

      log("QUERY IN DOCSET", LogType.DEBUG)
      # reset query to allow search in a specific docset
      vrs.docset_query = vrs.query # save docset keyword
      vrs.query = ""
      vrs.is_sel = True
      # store docset typed keyword
      vrs.sel_docset = data
      # Update UI query string
      extension.update_ui_query_string(event, vrs.query)
      # you may want to return another list of results
      return RenderResultListAction(
          [
              ResultItems.docset_searchforin_result(vrs.sel_docset, vrs.query),
              ResultItems.docset_change_result(),
          ]
      )
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


if __name__ == "__main__":
  Zealdocs().run()
