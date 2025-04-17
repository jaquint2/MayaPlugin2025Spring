from MayaUtils import *
from PySide2.QtWidgets import QVBoxLayout
import maya.cmds as mc

class AnimClip:
    def __init__(self):
        self.subfix = ""
        self.frameMin = mc.playbackOptions(q=True, min=True)
        self.frameMax = mc.playbackOptions(q=True, max=True)
        self.shouldExport = True


class MayaToUE:
    def __init__(self):
        self.rootjnt = ""
        self.models = set()
        self.animations : list[AnimClip] = []
        self.fileName = ""
        self.saveDir = ""


class MayaToUEWidget(MayaWindow):
    def GetWidgetUniqueName(self):
        return "MayaToUEWidget"
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maya to UE")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

MayaToUEWidget().show()
    