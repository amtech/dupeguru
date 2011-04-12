# Created By: Virgil Dupras
# Created On: 2009-05-24
# Copyright 2011 Hardcoded Software (http://www.hardcoded.net)
# 
# This software is licensed under the "BSD" License as described in the "LICENSE" file, 
# which should be included with this package. The terms are also available at 
# http://www.hardcoded.net/licenses/bsd_license

import logging

from hscommon import io
from hscommon.path import Path
from hscommon.cocoa.objcmin import NSWorkspace

from core import fs
from core.app_cocoa import DupeGuru as DupeGuruBase
from core.directories import Directories as DirectoriesBase, STATE_EXCLUDED
from . import data
from .fs import Bundle as BundleBase

def is_bundle(str_path):
    sw = NSWorkspace.sharedWorkspace()
    uti, error = sw.typeOfFile_error_(str_path, None)
    if error is not None:
        logging.warning('There was an error trying to detect the UTI of %s', str_path)
    return sw.type_conformsToType_(uti, 'com.apple.bundle') or sw.type_conformsToType_(uti, 'com.apple.package')

class Bundle(BundleBase):
    @classmethod
    def can_handle(cls, path):
        return not io.islink(path) and io.isdir(path) and is_bundle(str(path))
    

class Directories(DirectoriesBase):
    ROOT_PATH_TO_EXCLUDE = list(map(Path, ['/Library', '/Volumes', '/System', '/bin', '/sbin', '/opt', '/private', '/dev']))
    HOME_PATH_TO_EXCLUDE = [Path('Library')]
    def __init__(self):
        DirectoriesBase.__init__(self, fileclasses=[Bundle, fs.File])
    
    def _default_state_for_path(self, path):
        result = DirectoriesBase._default_state_for_path(self, path)
        if result is not None:
            return result
        if path in self.ROOT_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
        if path[:2] == Path('/Users') and path[3:] in self.HOME_PATH_TO_EXCLUDE:
            return STATE_EXCLUDED
    
    @staticmethod
    def get_subfolders(path):
        result = DirectoriesBase.get_subfolders(path)
        return [p for p in result if not is_bundle(str(p))]
    

class DupeGuru(DupeGuruBase):
    def __init__(self):
        DupeGuruBase.__init__(self, data, 'dupeGuru')
        self.directories = Directories()
    
