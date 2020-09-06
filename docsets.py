"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import os
import configparser
import plistlib
import traceback
from os.path import sep as SEP

# QT5
from PyQt5.QtCore import QStandardPaths as QsPath

# Ulauncher
from ulauncher.utils.fuzzy_search import get_score as searchScore

# Local
from logger import log
from logtype import LogType


class Docsets:
  """
  Provides Zeal docsets
  """

  docsetDict = {}
  docsetsList = []
  configPath = "Zeal%sZeal.conf" % (SEP)
  docsetPath = "Zeal%sZeal%sdocsets" % (SEP, SEP)
  Config = configparser.ConfigParser()

  config_locations = QsPath.standardLocations(QsPath.ConfigLocation)
  data_locations = QsPath.standardLocations(QsPath.DataLocation)

  @staticmethod
  def parse_docsets():
    """Looks for Zeal config file and parse docsets plists"""
    self = Docsets
    try:
      # Try to get config location
      for config_location in self.config_locations:
        c_path = config_location + SEP + self.configPath
        if os.path.exists(c_path):
          self.configPath = c_path

      # Try to get docset location
      try:
        if self.configPath:
          self.Config.read(self.configPath)
          self.docsetPath = self.Config["docsets"].get("path")
      except Exception as error:  # pylint: disable=broad-except
        log("Could not get config file %s" % self.configPath, LogType.DEBUG)
      if self.docsetPath is None:
        for data_location in self.data_locations:
          d_path = data_location + SEP + self.docsetPath
          if os.path.exists(d_path):
            self.docsetPath = d_path

      # try to get docset info
      for docset in os.listdir(self.docsetPath):
        docset = self.docsetPath + SEP + docset
        icon = docset + SEP + "icon.png"
        icon2 = docset + SEP + "icon@2x.png"
        p_list = docset + SEP + "Contents" + SEP + "Info.plist"
        with open(p_list, "rb") as plist_file:
          plist_data = plistlib.load(plist_file)
        d_id = plist_data.get("CFBundleIdentifier")
        self.docsetDict[d_id] = {
            "id": d_id,
            "name": plist_data.get("CFBundleName"),
            "icon": icon if os.path.exists(icon) else None,
            "icon2": icon2 if os.path.exists(icon2) else None,
        }
        self.docsetsList.append(self.docsetDict[d_id])
      return self.docsetsList
    except Exception as error:  # pylint: disable=broad-except
      log(error, LogType.ERROR)
      log(traceback.format_exc(), LogType.DEBUG)
      return []

  @staticmethod
  def sort_docsets(query: str):
    """
    Sorts docsets using damerau levenstein

    query: The query string to calculate the score with
    """
    self = Docsets
    ordered_docsets = []
    for docset in self.docsetsList:
      ordered_docsets.append(
          {
              "docset": docset,
              "score": searchScore(query, docset["name"]),
          }
      )
    # sort items and assign them to CustomAction
    return sorted(ordered_docsets, key=lambda x: x.get("score"), reverse=True)
