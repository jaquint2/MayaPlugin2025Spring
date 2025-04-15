import importlib
import MayaUtils
importlib.reload(MayaUtils)

from MayaUtils import MayaWindow
from PySide2.QtGui import QColor
from PySide2.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QSlider, QVBoxLayout, QColorDialog
from PySide2.QtCore import Qt, Signal
from maya.OpenMaya import MVector
import maya.mel as mel
import maya.cmds as mc

class LimbRigger:
    def __init__(self):
        self.root = ""
        self.mid = ""
        self.end = ""
        self.controllerSize = 5
        self.controllerColor = (1, 1, 0)

    def FindJointsBasedOnSelection(self):
        self.root = mc.ls(sl=True, type="joint")[0]
        self.mid = mc.listRelatives(self.root, c=True, type="joint")[0]
        self.end = mc.listRelatives(self.mid, c=True, type="joint")[0]

    def ApplyColorOverride(self, obj):
        r, g, b = self.controllerColor
        mc.setAttr(obj + ".overrideEnabled", 1)
        mc.setAttr(obj + ".overrideRGBColors", 1)
        mc.setAttr(obj + ".overrideColorRGB", r, g, b)

    def CreateFKControllerForJoint(self, jntName):
        ctrlName = "ac_l_fk_" + jntName
        ctrlGrpName = ctrlName + "_grp"
        mc.circle(n=ctrlName, radius=self.controllerSize, normal=(1, 0, 0))
        self.ApplyColorOverride(ctrlName)
        mc.group(ctrlName, n=ctrlGrpName)
        mc.matchTransform(ctrlGrpName, jntName)
        mc.orientConstraint(ctrlName, jntName)
        return ctrlName, ctrlGrpName

    def CreateBoxController(self, name):
        mel.eval(f"curve -n {name} -d 1 -p 0.5 0.5 0.5 -p 0.5 0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p 0.5 0.5 0.5 -p 0.5 -0.5 0.5 -p 0.5 -0.5 -0.5 -p 0.5 0.5 -0.5 -p 0.5 -0.5 -0.5 -p -0.5 -0.5 -0.5 -p -0.5 0.5 -0.5 -p -0.5 0.5 0.5 -p -0.5 -0.5 0.5 -p -0.5 -0.5 -0.5 -p -0.5 -0.5 0.5 -p 0.5 -0.5 0.5 -k 0 -k 1 -k 2 -k 3 -k 4 -k 5 -k 6 -k 7 -k 8 -k 9 -k 10 -k 11 -k 12 -k 13 -k 14 -k 15;")
        mc.scale(self.controllerSize, self.controllerSize, self.controllerSize, name)
        mc.makeIdentity(name, apply=True)
        self.ApplyColorOverride(name)
        grpName = name + "_grp"
        mc.group(name, n=grpName)
        return name, grpName

    def CreatePlusController(self, name):
        mel.eval(f"curve -n {name}")
        return name, name + "_grp"

    def GetObjectLocation(self, objectName):
        x, y, z = mc.xform(objectName, q=True, ws=True, t=True)
        return MVector(x, y, z)

    def PrintMVector(self, vector):
        print(f"<{vector.x}{vector.y}{vector.z}")

    def RigLimb(self):
        rootCtrl, rootCtrlGrp = self.CreateFKControllerForJoint(self.root)
        midCtrl, midCtrlGrp = self.CreateFKControllerForJoint(self.mid)
        endCtrl, endCtrlGrp = self.CreateFKControllerForJoint(self.end)

        mc.parent(midCtrlGrp, rootCtrl)
        mc.parent(endCtrlGrp, midCtrl)

        ikEndCtrl = "ac_ik_" + self.end
        ikEndCtrl, ikEndCtrlGrp = self.CreateBoxController(ikEndCtrl)
        mc.matchTransform(ikEndCtrlGrp, self.end)
        endOrientConstraint = mc.orientConstraint(ikEndCtrl, self.end)[0]

        rootJntLoc = self.GetObjectLocation(self.root)
        self.PrintMVector(rootJntLoc)

        ikHandleName = "ikHandle_" + self.end
        mc.ikHandle(n=ikHandleName, sol="ikRPsolver", sj=self.root, ee=self.end)

        poleVectorLocationVals = mc.getAttr(ikHandleName + ".poleVector")[0]
        poleVector = MVector(poleVectorLocationVals[0], poleVectorLocationVals[1], poleVectorLocationVals[2])
        poleVector.normalize()

        endJntLoc = self.GetObjectLocation(self.end)
        rootToEndVector = endJntLoc - rootJntLoc

        poleVectorCtrlLoc = rootJntLoc + rootToEndVector / 2 + poleVector * rootToEndVector.length()
        poleVectorCtrl = "ac_ik_" + self.mid
        mc.spaceLocator(n=poleVectorCtrl)
        poleVectorCtrlGrp = poleVectorCtrl + "_grp"
        mc.group(poleVectorCtrl, n=poleVectorCtrlGrp)
        mc.setAttr(poleVectorCtrlGrp + ".t", poleVectorCtrlLoc.x, poleVectorCtrlLoc.y, poleVectorCtrlLoc.z, type="double3")

        mc.poleVectorConstraint(poleVectorCtrl, ikHandleName)

        ikfkBlendCtrl = "ac_ikfkblend_" + self.root
        ikfkBlendCtrl, ikfkBlendCtrlGrp = self.CreatePlusController(ikfkBlendCtrl)
        mc.setAttr(ikfkBlendCtrlGrp + ".t", rootJntLoc.x * 2, rootJntLoc.y, rootJntLoc.z * 2, typ="double3")

        ikfkBlendAttrName = "ikfkBlend"
        mc.addAttr(ikfkBlendCtrl, ln=ikfkBlendAttrName, min=0, max=1, k=True)
        ikfkBlendAttr = ikfkBlendCtrl + "." + ikfkBlendAttrName

        mc.expression(s=f"{ikHandleName}.ikBlend={ikfkBlendAttr}")
        mc.expression(s=f"{ikEndCtrlGrp}.v={poleVectorCtrlGrp}.v={ikfkBlendAttr}")
        mc.expression(s=f"{rootCtrlGrp}.v=1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{endCtrl}W0 = 1-{ikfkBlendAttr}")
        mc.expression(s=f"{endOrientConstraint}.{ikEndCtrl}W1 = {ikfkBlendAttr}")

        topGrpName = f"{self.root}_rig_grp"
        mc.group([rootCtrlGrp, ikEndCtrlGrp, poleVectorCtrlGrp, ikfkBlendCtrlGrp], n=topGrpName)
        mc.parent(ikHandleName, ikEndCtrl)

class LimbRiggerWidget(MayaWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Limb Rigger")
        self.rigger = LimbRigger()
        self.masterLayout = QVBoxLayout()
        self.setLayout(self.masterLayout)

        toolTipLabel = QLabel("Select the first joint of the Limb, and press the auto find button")
        self.masterLayout.addWidget(toolTipLabel)

        self.jnt1 = None
        self.jntsListLineEdit = QLineEdit()
        self.jntsListLineEdit.setEnabled(False)
        self.masterLayout.addWidget(self.jntsListLineEdit)

        autoFindBtn = QPushButton("Auto Find")
        autoFindBtn.clicked.connect(self.AutoFindJntBtnClicked)
        self.masterLayout.addWidget(autoFindBtn)

        # Color Picker
        self.colorButton = QPushButton("Pick Controller Color")
        self.colorButton.clicked.connect(self.PickColor)
        self.colorSwatch = QLabel()
        self.colorSwatch.setFixedSize(40, 20)
        self.colorSwatch.setStyleSheet("background-color: rgb(255, 255, 0);")

        colorLayout = QHBoxLayout()
        colorLayout.addWidget(self.colorButton)
        colorLayout.addWidget(self.colorSwatch)
        self.masterLayout.addLayout(colorLayout)

        # Set Color Button
        self.setColorButton = QPushButton("Set Color")
        self.setColorButton.clicked.connect(self.SetColorToSelected)
        self.masterLayout.addWidget(self.setColorButton)

        ctrlSizeSlider = QSlider()
        ctrlSizeSlider.setOrientation(Qt.Horizontal)
        ctrlSizeSlider.setRange(1, 30)
        ctrlSizeSlider.setValue(self.rigger.controllerSize)
        self.ctrlSizeLabel = QLabel(f"{self.rigger.controllerSize}")
        ctrlSizeSlider.valueChanged.connect(self.CtrSizeSliderChanged)

        ctrlSizeLayout = QHBoxLayout()
        ctrlSizeLayout.addWidget(ctrlSizeSlider)
        ctrlSizeLayout.addWidget(self.ctrlSizeLabel)
        self.masterLayout.addLayout(ctrlSizeLayout)

        rigjntBtn = QPushButton("Rig Limb")
        rigjntBtn.clicked.connect(lambda: self.rigger.RigLimb())
        self.masterLayout.addWidget(rigjntBtn)

    def CtrSizeSliderChanged(self, newValue):
        self.ctrlSizeLabel.setText(f"{newValue}")
        self.rigger.controllerSize = newValue

    def AutoFindJntBtnClicked(self):
        try:
            self.rigger.FindJointsBasedOnSelection()
            self.jntsListLineEdit.setText(f"{self.rigger.root}, {self.rigger.mid}, {self.rigger.end}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}")

    def PickColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            r = color.red() / 255.0
            g = color.green() / 255.0
            b = color.blue() / 255.0
            self.rigger.controllerColor = (r, g, b)
            self.colorSwatch.setStyleSheet(f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});")

    def SetColorToSelected(self):
        selection = mc.ls(sl=True)
        if not selection:
            QMessageBox.warning(self, "No Selection", "Please select a controller to apply the color.")
            return

        for obj in selection:
            try:
                self.rigger.ApplyColorOverride(obj)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to apply color to {obj}.\n{e}")

limbRiggerWidget = LimbRiggerWidget()
limbRiggerWidget.show()
