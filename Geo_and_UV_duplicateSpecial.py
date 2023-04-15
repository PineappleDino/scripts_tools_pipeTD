# Script tool for duplcating UVs of a geometry, in Maya.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
#import maya.api.OpenMaya as om
import maya.cmds as cmds

class _UVandGeoDuplicator(QWidget):
    def __init__(self):
        super(self.__class__, self).__init__()
        self. initUI()

    def initUI(self):
        #GUI HERE -------------
        self.setWindowTitle("Duplicate Special - Geo and UV")
        self.setGeometry(1100, 40, 400, 100)
        self.setLayout(QVBoxLayout())
        self.guiLayout_TransformXYZ = QHBoxLayout()
        self.guiLayout_RotateXYZ = QHBoxLayout()
        self.guiLayout_UVs = QHBoxLayout()
        self.guiLayout_buttons = QHBoxLayout()
        self.guiLayout_LabelTranslate = QVBoxLayout()
        self.guiLayout_LabelRotate = QVBoxLayout()
        self.guiLayout_LabelUV = QVBoxLayout()
        self.layout().addLayout(self.guiLayout_LabelTranslate)
        self.layout().addLayout(self.guiLayout_TransformXYZ)
        self.layout().addLayout(self.guiLayout_LabelRotate)
        self.layout().addLayout(self.guiLayout_RotateXYZ)
        self.layout().addLayout(self.guiLayout_LabelUV)
        self.layout().addLayout(self.guiLayout_UVs)
        self.layout().addLayout(self.guiLayout_buttons)

        #__GUI Elements Variables__________________________
        self.xT_label = QLabel()
        self.xT_label.setText("TransformX")
        self.yT_label = QLabel()
        self.yT_label.setText("TransformY")
        self.zT_label = QLabel()
        self.zT_label.setText("TransformZ")
        self.xR_label = QLabel()
        self.xR_label.setText("RotationX")
        self.yR_label = QLabel()
        self.yR_label.setText("RotationY")
        self.zR_label = QLabel()
        self.zR_label.setText("RotationZ")
        self.uT_label = QLabel()
        self.uT_label.setText("TransformU")
        self.vT_label = QLabel()
        self.vT_label.setText("TransformV")
        self.uvR_label = QLabel()
        self.uvR_label.setText("Rotation Angle UV")
        self.duplicationNumber_label = QLabel()
        self.duplicationNumber_label.setText("Number of Duplicates")
        self.xT_input = QLineEdit()
        self.xT_input.setText('0')
        self.yT_input = QLineEdit()
        self.yT_input.setText('0')
        self.zT_input = QLineEdit()
        self.zT_input.setText('0')
        self.xR_input = QLineEdit()
        self.xR_input.setText('0')
        self.yR_input = QLineEdit()
        self.yR_input.setText('0')
        self.zR_input = QLineEdit()
        self.zR_input.setText('0')
        self.uT_input = QLineEdit()
        self.uT_input.setText('0')
        self.vT_input = QLineEdit()
        self.vT_input.setText('0')
        self.uvR_input = QLineEdit()
        self.uvR_input.setText('0')

        self.guiLabels_Translate = QLabel()
        self.guiLabels_Translate.setText("\t\t______Translate:______")
        self.guiLabels_Rotate = QLabel()
        self.guiLabels_Rotate.setText("\n\t_______________Rotate:_________________")
        self.guiLabels_UVTransform = QLabel()
        self.guiLabels_UVTransform.setText('\n          _____ UV Transform and Rotation Angle: ____')

        self.duplicationNumber_input = QLineEdit()
        self.duplicationNumber_input.setText('1')
        self.applyChanges_Button = QPushButton("Apply Changes")

        #__GUI Elements add to Layout______________________
        self.guiLayout_LabelTranslate.addWidget(self.guiLabels_Translate)
        self.guiLayout_TransformXYZ.addWidget(self.xT_label)
        self.guiLayout_TransformXYZ.addWidget(self.xT_input)
        self.guiLayout_TransformXYZ.addWidget(self.yT_label)
        self.guiLayout_TransformXYZ.addWidget(self.yT_input)
        self.guiLayout_TransformXYZ.addWidget(self.zT_label)
        self.guiLayout_TransformXYZ.addWidget(self.zT_input)

        self.guiLayout_LabelRotate.addWidget(self.guiLabels_Rotate)
        self.guiLayout_RotateXYZ.addWidget(self.xR_label)
        self.guiLayout_RotateXYZ.addWidget(self.xR_input)
        self.guiLayout_RotateXYZ.addWidget(self.yR_label)
        self.guiLayout_RotateXYZ.addWidget(self.yR_input)
        self.guiLayout_RotateXYZ.addWidget(self.zR_label)
        self.guiLayout_RotateXYZ.addWidget(self.zR_input)

        self.guiLayout_LabelUV.addWidget(self.guiLabels_UVTransform)
        self.guiLayout_UVs.addWidget(self.uT_label)
        self.guiLayout_UVs.addWidget(self.uT_input)
        self.guiLayout_UVs.addWidget(self.vT_label)
        self.guiLayout_UVs.addWidget(self.vT_input)
        self.guiLayout_UVs.addWidget(self.uvR_label)
        self.guiLayout_UVs.addWidget(self.uvR_input)

        self.guiLayout_buttons.addWidget(self.duplicationNumber_label)
        self.guiLayout_buttons.addWidget(self.duplicationNumber_input)
        self.guiLayout_buttons.addWidget(self.applyChanges_Button)


        #___ GUI ELEMENT ATTRIBUTION TO FUNCTION:
        self.show()
        self.applyChanges_Button.clicked.connect(self._buttonPressed)

    def _buttonPressed(self):
        #Code when you press the APPLY button

        obj = cmds.ls(selection=True)
        print obj

        globals()['objList'] = []

        xT = float(self.xT_input.text())
        yT = float(self.yT_input.text())
        zT = float(self.zT_input.text())
        xR = float(self.xR_input.text())
        yR = float(self.yR_input.text())
        zR = float(self.zR_input.text())

        uT = float(self.uT_input.text())
        vT = float(self.vT_input.text())
        uvR = float(self.uvR_input.text())

        numberToDuplicate = int(self.duplicationNumber_input.text())

        print "\n ____DUPLICATING MESH ======"
        self.objDuplicate(numberToDuplicate, xT, yT, zT, xR, yR, zR)
        print "\nCreated duplicates =", objList
        print '---END ____ Duplicating Mesh ------ \n'

        numberObj = len(objList)
        print 'numberObj =', numberObj

        print '\n_____ MOVING UVs ================='
        self.objUVMove(obj, objList, uT, vT, uvR, numberObj)
        print '---END ____ MOVING UVs ----------\n'

        print "====== Duplicate Special with UVs ==== END ===="

    def objUVMove(self, obj, objList, uT, vT, uvR, numberObj):
        print 'obj =', obj
        cmds.select(obj)
        obj = cmds.ls(selection = True, flatten = True, dagObjects = True)
        print 'obj (dag)=', obj

        uvMaps = cmds.polyEvaluate(obj, uvComponent = True)
        print 'uvMaps =', uvMaps
        uvPosition = cmds.polyEditUV('{0}.map[0]'.format(obj[0]), query = True)
        print 'UVPosition =', uvPosition
        print 'obj Shape =', obj[1]

        print 'uTransform =', uT
        print 'vTransform =', vT
        print 'vRotate =', uvR
        uT_original = uT
        vT_original = vT
        uvR_original = uvR

        numFaces = cmds.polyEvaluate(face = True)
        print 'numFaces =', numFaces

        i = 1
        if i == numberObj:
            for obj in sorted(objList):
                cmds.select(obj, replace = True)
                obj = cmds.ls(selection = True, flatten = True, dagObjects = True)
                print 'obj =', obj
                uvMaps = cmds.polyEvaluate(obj, uvComponent = True)
                uvPosition = cmds.polyEditUV('{0}.map[0]'.format(obj[1]), query = True)

                cmds.select('{0}.f[0:{1}]'.format(obj[1], numFaces), replace = True)
                cmds.setAttr('{0}.uvPivot'.format(obj[1]), query = True)
                cmds.setAttr('{0}.uvPivot'.format(obj[0]), uvPosition[0], uvPosition[1], type = 'double2')
                cmds.polyEditUV(relative = True, uValue = uT, vValue = vT, angle = uvR)
        else:
            for obj in sorted(objList):
                cmds.select(obj, replace = True)
                obj = cmds.ls(selection = True, flatten = True, dagObjects = True)
                print 'obj =', obj
                uvMaps = cmds.polyEvaluate(obj, uvComponent = True)
                uvPosition = cmds.polyEditUV('{0}.map[0]'.format(obj[1]), query = True)

                cmds.select('{0}.f[0:{1}]'.format(obj[1], numFaces), replace = True)
                cmds.setAttr('{0}.uvPivot'.format(obj[1]), query = True)
                cmds.setAttr('{0}.uvPivot'.format(obj[0]), uvPosition[0], uvPosition[1], type = 'double2')
                cmds.polyEditUV(relative = True, uValue = uT, vValue = vT)
                cmds.polyEditUV(relative = True, pivotU = uvPosition[0], pivotV = uvPosition[1], angle = uvR)
                uT = uT + uT_original
                print "uT =", uT
                vT = vT + vT_original
                print "vT =", vT
                uvR = uvR + uvR_original
                print "uvR =", uvR

    def objDuplicate(self, x, xT, yT, zT, xR, yR, zR):
        i = 1
        if i == x:
            print '\n i =', i
            newObj = cmds.duplicate()
            print 'newObj =', newObj
            objList.append(newObj)
            print 'objList =', objList
            cmds.select(newObj)
            cmds.move(xT,yT,zT, relative = True)
            cmds.rotate(xR,yR,zR, relative = True)
        else:
            while i <= x:
                print '\n i =', i
                newObj = cmds.duplicate()
                print 'newObj =', newObj
                objList.append(newObj)
                print 'objList =', objList
                cmds.select(newObj)
                cmds.move(xT,yT,zT, relative = True)
                cmds.rotate(xR,yR,zR, relative = True)
                i += 1
        return objList

window = _UVandGeoDuplicator()
window.show()
