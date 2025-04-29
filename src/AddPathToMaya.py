import sys

prjPath = "D:/profile redirect/jaquint2/Documents/mayaPlugins/src"
moduleDir = "D:/profile_redirect/jaquint2"
if prjPath not in sys.path:
    sys.path.append(prjPath)

if moduleDir not in sys.path:
    sys.path.append(moduleDir)

