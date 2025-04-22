from MayaUtils import *
from PySide2.QtWidgets import QLineEdit, QMessageBox, QPushButton, QVBoxLayout
import maya.cmds as mc

def TryAction(actionFunc):
    def wrapper(*args, **kwargs):
        try:
            actionFunc(*args, **kwargs)
        except Exception as e:
            QMessageBox().critical(None, "Error!", f"{e}")

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

    def AddRootJoint(self):
        if not self.rootJnt:
            raise Exception("No Root Joint Assigned, please set the root joint of your rig first")
        
        if mc.objExists(self.rootJnt):
            currentRootPos = mc.xform(self.rootJnt, q=True, ws=True, t=True)
            if currentRootPos[0] == 0 and currentRootPos[1] == 0 and currentRootPos[2] == 0:
                raise Exception("current root joint is at origin already, no need to make a new one!")
            
            mc.select(cl=True)
            rootJntName = self.rootJnt + "_root"
            mc.joint(n=rootJntName)
            mc.parent(self.rootJnt, rootJntName)
            self.rootJnt = rootJntName


    def SetSelectedJointAsRoot(self):
        selection = mc.ls(sl=True, Type="joint")
        if not selection:
            raise Exception("Wrong Selection please select the root joint of your rig!")
        
        self.rootJnt = selection[0]

class MayaToUEWidget(MayaWindow):
    def GetWidgetUniqueName(self):
        return "MayaToUEWidget"
    
    def __init__(self):
        super().__init__()
        self.mayaToUE = MayaToUE()

        self.setWindowTitle("Maya to UE")
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        self.rootJntText = QLineEdit()
        self.rootJntText.setEnabled(False)
        self.masterLayout.addWidget(self.rootJntText)

        setSelectionAsRootjntBtn = QPushButton("Set Root Joint")
        setSelectionAsRootjntBtn.clicked.connect(self.SetSelectedAsRootJntBtnClicked)

        addRootJntBtn = QPushButton("add Root Joint")
        addRootJntBtn.clicked.connect(self.AddRootJntBtnClicked)

    @TryAction
    def AddRootJntBtnClicked(self):
        self.mayaToUE.AddRootJoint()
        self.rootJntText.setText(self.mayaToUE.rootJnt)

    def SetSelectedAsRootJntBtnClicked(self):
            self.mayaToUE.SetSelectedJointAsRoot()
            self.rootJnttext.setText(self.mayaToUE.rootJnt)
        

MayaToUEWidget().show()
    