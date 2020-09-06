import os, configparser, plistlib
from pathlib import Path
from logger import log
from logtype import LogType
from os.path import sep as SEP
from PyQt5.QtCore import QStandardPaths as QsPath
from ulauncher.utils.fuzzy_search import get_score as searchScore
import traceback

class Docsets:

  docsetDict = {}
  docsetsList = []
  configPath = "Zeal%sZeal.conf" % (SEP)
  docsetPath = "Zeal%sZeal%sdocsets" % (SEP, SEP)
  Config = configparser.ConfigParser()

  configLocations = QsPath.standardLocations(QsPath.ConfigLocation)
  dataLocations = QsPath.standardLocations(QsPath.DataLocation)

  @staticmethod
  def parseDocsets():
    self = Docsets
    try:
      # Try to get config location
      for configLocation in self.configLocations:
        cPath = configLocation + SEP + self.configPath
        if os.path.exists(cPath):
          self.configPath = cPath

      # Try to get docset location
      try:
        if self.configPath:
          self.Config.read(self.configPath)
          self.docsetPath = self.Config['docsets'].get('path')
      except Exception as e:
        log("Could not get config file %s" % self.configPath, LogType.DEBUG)
      if self.docsetPath is None:
        for dataLocation in self.dataLocations:
          dPath = dataLocation + SEP + self.docsetPath
          if os.path.exists(dPath):
            self.docsetPath = dPath

      # try to get docset info
      for docset in os.listdir(self.docsetPath):
        docset = self.docsetPath + SEP + docset
        icon = docset + SEP + 'icon.png'
        icon2 = docset + SEP + 'icon@2x.png'
        pList =  docset + SEP + "Contents" + SEP + "Info.plist"
        with open(pList, 'rb') as f:
          plist_data = plistlib.load(f)
        dId = plist_data.get('CFBundleIdentifier')
        self.docsetDict[dId] = {
          'id': dId,
          'name': plist_data.get('CFBundleName'),
          'icon': icon if os.path.exists(icon) else None,
          'icon2': icon2 if os.path.exists(icon2) else None,
        }
        self.docsetsList.append(self.docsetDict[dId])
      return self.docsetsList
    except Exception as e:
      log(e, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)
      return []

  @staticmethod
  def sortDocsets(query: str):
    self = Docsets
    orderedDocsets = []
    for docset in self.docsetsList:
      orderedDocsets.append({
        'docset': docset,
        'score': searchScore(query, docset['name']),
      })
    # sort items and assign them to CustomAction
    return sorted(orderedDocsets, key=lambda x: x.get('score'), reverse=True)
