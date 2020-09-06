import os

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent, SystemExitEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.item.ExtensionSmallResultItem import ExtensionSmallResultItem
from ulauncher.api.client.EventListener import EventListener

from ulauncher.api.shared.action.OpenAction import OpenAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction

# Local
from docsets import Docsets
from logger import log
from logtype import LogType
import traceback

dir_path = os.path.dirname(os.path.realpath(__file__))

variables = {
  'selectedAndItem': False,
  'selectedDocset': None,
  'query': '',
  'docsetQuery': '',
}
docsets = []

class Zealdocs(Extension):

  def __init__(self):
    super(Zealdocs, self).__init__()
    self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
    self.subscribe(ItemEnterEvent, ItemEnterEventListener())  # <-- add this line
    Docsets.parseDocsets()

class KeywordQueryEventListener(EventListener):

  def on_event(self, event, extension):
    try:
      log('Selected and items ? %d' % (variables['selectedAndItem']))
      # log('TOTOTOTOTOT', LogType.DEBUG)
      # log(event.query, LogType.DEBUG)
      query = variables['query'] = event.query.replace('dm ', '', 1)
      log(query, LogType.WARNING)
      items = []
      extResultsSorted = []

      if (variables['selectedAndItem']):
        # open with dash-plugin://keys=python,django&query=string
        log('EXEC SEARCH', LogType.WARNING)
        log(variables, LogType.WARNING)
        log(dir_path + os.path.sep + 'images' + os.path.sep + 'icon.png', LogType.WARNING)
        variables['query'].replace(variables['docsetQuery'], '', 1) 
        query = event.query.replace('dm ', '', 1).replace(variables['docsetQuery'], '', 1).strip()
        return RenderResultListAction([ExtensionResultItem(
          icon=variables['selectedDocset']['icon2'],
          name='Search for %s in %s' % (query, variables['selectedDocset']['name']),
          on_enter=OpenAction(path='dash-plugin://keys=%s&query=%s' % (variables['selectedDocset']['id'], query))
        ), ExtensionResultItem(
          icon=dir_path + os.path.sep + 'images' + os.path.sep + 'icon.png',
          name='Look in another docset',
          on_enter=ExtensionCustomAction({
              'reset': True
            }, keep_app_open=True)
        )])
      else:
        log('LIST DOCSETS', LogType.WARNING)
        query = event.query.replace('dm ', '', 1)

        # If User types a docset ID with keyword
        if(Docsets.docsetDict.get(query) or variables['selectedDocset']):

          # filter query to remove docset ID if needed or assign a selected docset
          if(not variables['selectedDocset']): variables['selectedDocset'] = Docsets.docsetDict.get(query)
          else: query = query.replace(variables['selectedDocset']['id'], '', 1).strip()

          return RenderResultListAction([ExtensionResultItem(
            icon=variables['selectedDocset']['icon2'],
            name='Search for %s in %s' % (query, variables['selectedDocset']['name']),
            on_enter=OpenAction(path='dash-plugin://keys=%s&query=%s' % (variables['selectedDocset']['id'], query))
          ), ExtensionResultItem(
          icon=dir_path + os.path.sep + 'images' + os.path.sep + 'icon.png',
          name='Look in another docset',
          on_enter=ExtensionCustomAction({
              'reset': True
            }, keep_app_open=True)
        )])
        
        # User would select a docset
        else:
          variables['selectedDocset'] = None
          for item in Docsets.sortDocsets(event.query):
                extResultsSorted.append(ExtensionResultItem(
                  icon = item['docset']['icon2'],
                  name= item['docset']['name'],
                  description='Search in %s' % item['docset']['name'],
                  on_enter=ExtensionCustomAction(item, keep_app_open=True))
                )

      #return docsets sorted by score
      return RenderResultListAction(extResultsSorted)
    except Exception as e:
      log(e, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)

class ItemEnterEventListener(EventListener):

  def on_event(self, event, extension):
    try:
      data = event.get_data()
      extResultsSorted = []
      # do additional actions here...
      log(data, LogType.DEBUG)
      log(event, LogType.DEBUG)

      if('reset' in data):
        # print docsets
        log('LIST DOCSETS RESET', LogType.WARNING)
        variables['selectedAndItem'] = False
        variables['selectedDocset'] = None
        for item in Docsets.sortDocsets(variables['query']):
              extResultsSorted.append(ExtensionResultItem(
          icon = item['docset']['icon2'],
          name= item['docset']['name'],
          description='Search in %s' % item['docset']['name'],
          on_enter=ExtensionCustomAction(item, keep_app_open=True)))
        return RenderResultListAction(extResultsSorted)
      else:
        log('QUERY IN DOCSET', LogType.WARNING)
        # store docset typed keyword
        variables['docsetQuery'] = variables['query']
        # reset query to allow search in a specific docset
        variables['query'] = ''
        variables['selectedAndItem'] = True
        variables['selectedDocset'] = data['docset']
        # you may want to return another list of results
        return RenderResultListAction([ExtensionResultItem(
          icon=data['docset']['icon2'],
          name='Search for %s in %s' % (variables['query'], data['docset']['name']),
          on_enter=ExtensionCustomAction(data))
          , ExtensionResultItem(
          icon=dir_path + os.path.sep + 'images' + os.path.sep + 'icon.png',
          name='Look in another docset',
          on_enter=ExtensionCustomAction({
              'reset': True
            }, keep_app_open=True)
        )])
    except Exception as e:
      log(e, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)

# class SystemExitEvent(EventListener):
#   def on_event(self, event):
#     Docsets.clear()

if __name__ == '__main__':
  Zealdocs().run()