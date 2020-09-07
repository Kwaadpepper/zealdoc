"""
Author: Jérémy Munsch <github@jeremydev.ovh>
Licence: MIT
"""

# Standard
import os
import locale
import gettext

dir_path = os.path.dirname(os.path.realpath(__file__))
current_locale, encoding = locale.getdefaultlocale()
localedir = dir_path + os.path.sep + ".." + os.path.sep + "lang"
trans = gettext.translation('base', localedir, [current_locale], fallback=True)
trans.install()

__= trans.gettext
