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

    log("preferences  %s" % self.preferences, LogType.WARNING)

  def update_ui_query_string(self, event, query):
    """Changes Ui query string"""
    log("preferences  %s" % self.variables.keyword, LogType.WARNING)

    # pylint: disable=(protected-access)
    self._client.send(
        Response(event, SetUserQueryAction(self.variables.keyword + " " + query))
    )

  def select_docset(self, docset_or_docset_name):
    """Select an active docset"""
    if isinstance(docset_or_docset_name, str):
      docset = Docsets.docsetDict.get(docset_or_docset_name)
    else:
      docset = docset_or_docset_name
    log(" select  %s" % docset, LogType.WARNING)
    vrs = self.variables
    vrs.is_sel = True
    vrs.sel_docset = docset
    vrs.docset_query = docset["id"]

  def unselect_docset(self):
    """Removes docset selection to show the list instead"""
    vrs = self.variables
    vrs.is_sel = False
    vrs.sel_docset = {}
    vrs.docset_query = None

  def get_sorted_docsets(self, query):
    """Returns an array with sorted docsets"""
    ext_results_sorted = []
    for item in Docsets.sort_docsets(query):
      ext_results_sorted.append(ResultItems.docset_result(item["docset"]))
    return ext_results_sorted


class KeywordQueryEventListener(EventListener):
  """On type event"""

  def on_event(self, event, extension):
    try:
      vrs = extension.variables
      vrs.keyword = event.query.split(" ")[0]  # store docset used keyword
      query = vrs.query = event.query.replace(vrs.keyword + " ", "", 1)

      # Is a docset selected ?
      if vrs.is_sel:
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

      # If User types a docset ID withinz keyword
      if Docsets.docsetDict.get(query):
        log("SELECTED A DOCSET", LogType.DEBUG)
        # Select a docset
        extension.select_docset(query)
        # Update UI query string
        extension.update_ui_query_string(event, "")

        return RenderResultListAction(
            [
                ResultItems.docset_searchforin_result(vrs.sel_docset, ""),
                ResultItems.docset_change_result(),
            ]
        )

      # ELSE User would select a docset
      log("LIST DOCSETS", LogType.DEBUG)
      # Unselect docset
      extension.unselect_docset()
      # List docsets
      return RenderResultListAction(extension.get_sorted_docsets(query))
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


class ItemEnterEventListener(EventListener):
  """When an item is selected"""

  def on_event(self, event, extension):
    try:
      vrs = extension.variables
      data = event.get_data()

      if "reset" in data:
        log("LIST DOCSETS RESET", LogType.DEBUG)
        # Unselect docset
        extension.unselect_docset()
        # List docsets
        return RenderResultListAction(extension.get_sorted_docsets(vrs.query))

      log("QUERY IN DOCSET", LogType.DEBUG)
      # Select a docset
      extension.select_docset(data)
      # Reset query to allow keyword search in the docset
      vrs.query = ""
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
