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

dir_path = os.path.dirname(os.path.realpath(__file__))

variables = {
    "selected_and_item": False,
    "selected_docset": {},
    "query": "",
    "docset_query": "",
}
docsets = []


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
      log("Selected and items ? %d" % (variables["selected_and_item"]))
      query = variables["query"] = event.query.replace("zd ", "", 1)
      log(query, LogType.WARNING)
      ext_results_sorted = []

      if variables["selected_and_item"]:
        # open with dash-plugin://keys=python,django&query=string
        log("EXEC SEARCH", LogType.WARNING)
        log(variables, LogType.WARNING)
        log(
            dir_path + os.path.sep + "images" + os.path.sep + "icon.png",
            LogType.WARNING,
        )
        variables["query"].replace(variables["docset_query"], "", 1)
        query = (
            event.query.replace("zd ", "", 1)
            .replace(variables["docset_query"], "", 1)
            .strip()
        )
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=variables["selected_docset"]["icon2"],
                    name="Search for %s in %s"
                    % (query, variables["selected_docset"]["name"]),
                    on_enter=OpenAction(
                        path="dash-plugin://keys=%s&query=%s"
                        % (variables["selected_docset"]["id"], query)
                    ),
                ),
                ExtensionResultItem(
                    icon=dir_path
                    + os.path.sep
                    + "images"
                    + os.path.sep
                    + "icon.png",
                    name="Look in another docset",
                    on_enter=ExtensionCustomAction(
                        {"reset": True}, keep_app_open=True
                    ),
                ),
            ]
        )
      else:
        log("LIST DOCSETS", LogType.WARNING)
        query = event.query.replace("zd ", "", 1)

        # If User types a docset ID with keyword
        if Docsets.docsetDict.get(query) or variables["selected_docset"]:

          # filter query to remove docset ID if needed or assign a
          # selected docset
          if not variables["selected_and_item"]:
            variables["selected_and_item"] = True
            variables["selected_docset"] = Docsets.docsetDict.get(query)
          else:
            query = query.replace(
                variables["selected_docset"]["id"], "", 1
            ).strip()

          return RenderResultListAction(
              [
                  ExtensionResultItem(
                      icon=variables["selected_docset"]["icon2"],
                      name="Search for %s in %s"
                      % (query, variables["selected_docset"]["name"]),
                      on_enter=OpenAction(
                          path="dash-plugin://keys=%s&query=%s"
                          % (variables["selected_docset"]["id"], query)
                      ),
                  ),
                  ExtensionResultItem(
                      icon=dir_path
                      + os.path.sep
                      + "images"
                      + os.path.sep
                      + "icon.png",
                      name="Look in another docset",
                      on_enter=ExtensionCustomAction(
                          {"reset": True}, keep_app_open=True
                      ),
                  ),
              ]
          )

        # User would select a docset
        else:
          variables["selected_and_item"] = False
          variables["selected_docset"] = {}
          for item in Docsets.sort_docsets(event.query):
            ext_results_sorted.append(
                ExtensionResultItem(
                    icon=item["docset"]["icon2"],
                    name=item["docset"]["name"],
                    description="Search in %s" % item["docset"]["name"],
                    on_enter=ExtensionCustomAction(
                        item, keep_app_open=True
                    ),
                )
            )

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
        variables["selected_and_item"] = False
        variables["selected_docset"] = {}
        for item in Docsets.sort_docsets(variables["query"]):
          ext_results_sorted.append(
              ExtensionResultItem(
                  icon=item["docset"]["icon2"],
                  name=item["docset"]["name"],
                  description="Search in %s" % item["docset"]["name"],
                  on_enter=ExtensionCustomAction(item, keep_app_open=True),
              )
          )
        return RenderResultListAction(ext_results_sorted)
      else:
        log("QUERY IN DOCSET", LogType.WARNING)
        # store docset typed keyword
        variables["docset_query"] = variables["query"]
        # reset query to allow search in a specific docset
        variables["query"] = ""
        variables["selected_and_item"] = True
        variables["selected_docset"] = data["docset"]
        # you may want to return another list of results
        return RenderResultListAction(
            [
                ExtensionResultItem(
                    icon=data["docset"]["icon2"],
                    name="Search for %s in %s"
                    % (variables["query"], data["docset"]["name"]),
                    on_enter=ExtensionCustomAction(data),
                ),
                ExtensionResultItem(
                    icon=dir_path
                    + os.path.sep
                    + "images"
                    + os.path.sep
                    + "icon.png",
                    name="Look in another docset",
                    on_enter=ExtensionCustomAction(
                        {"reset": True}, keep_app_open=True
                    ),
                ),
            ]
        )
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)


if __name__ == "__main__":
  Zealdocs().run()
