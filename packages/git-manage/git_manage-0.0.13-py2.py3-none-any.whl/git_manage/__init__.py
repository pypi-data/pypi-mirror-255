# -*- coding: utf-8 -*-
"""
Created on Mon Apr 22 19:45:01 2019

@author: danaukes
"""

import os
import sys

def clean_path(path_in):
    path_out = os.path.normpath(os.path.abspath(os.path.expanduser(path_in)))
    return path_out

if hasattr(sys, 'frozen'):
    module_path = os.path.normpath(os.path.join(os.path.dirname(sys.executable),''))
else:
    module_path = sys.modules['git_manage'].__path__[0]

personal_config_folder = clean_path('~/.config/gitman')
personal_config_path = clean_path(os.path.join(personal_config_folder,'config.yaml'))
package_config_path = clean_path(os.path.join(module_path,'support','config.yaml'))
