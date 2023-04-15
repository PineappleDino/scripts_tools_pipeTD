#Reference Code to get center of face: 
#___http://mayastation.typepad.com/maya-station/2009/11/where-is-the-center-of-a-polygon.html
#___http://forums.cgsociety.org/showthread.php?t=1025306
#___
 
import string
import maya.cmds as maya
import maya.OpenMaya as om
import math
 
#+++++++++++++++++++++FUNCTIONS_SECTION++++++++++++++++++++++++++
def getVerticesInFace():
    vtx = []
    numberVtx = []
 
    faceToVtx = maya.polyInfo(faceToVertex = True)
    faceNormal = maya.polyInfo(faceNormals = True)
    print "Vertexes in Face =", faceToVtx[0]
    faceToVtx = string.split(faceToVtx[0], "      ")
    print "Face Normals =", faceNormal
    
    for i in faceToVtx:
        print faceToVtx
        print i
        print numberVtx.append[str(i)]
        print numberVtx
        
    print vtx
 
 
def locatorSet(i):
    loc = maya.spaceLocator(name=item + '_%s_lctr' % (i))
    print 'Locator:', str(loc)
 
def vtxAverage():
 
    return
 
def selectVertices(faceToVtx):
    i = faceToVtx
    vertLocalX = []
    vertLocalY = []
    vertLocalZ = []
    while i < totalVtx:
        vtxSel = str(item + '.vtx[{}]'.format(i))
        print 'vtxSel =', vtxSel 
        maya.select(vtxSel)
        
        vertLocalXYZ = maya.pointPosition(str(item + '.vtx[{}]'.format(i)), local=True)
        vertLocalX = round(float(vertLocalXYZ[0]), 3)
        vertLocalY = round(float(vertLocalXYZ[1]), 3)
        vertLocalZ = round(float(vertLocalXYZ[2]), 3)
        print 'Local XYZ =', vertLocalX, vertLocalY, vertLocalZ
        
        vertWorldXYZ = maya.pointPosition(str(item + '.vtx[{}]'.format(i)), world=True)        
        vertWorldX = round(float(vertWorldXYZ[0]), 3)
        vertWorldY = round(float(vertWorldXYZ[1]), 3)
        vertWorldZ = round(float(vertWorldXYZ[2]), 3)
        print 'World XYZ =', vertWorldX, vertWorldY, vertWorldZ
        
        i += 1
        return i, vtxSel, vertWorldX, vertWorldY, vertWorldZ, vertLocalX, vertLocalY, vertLocalZ
 
def selectFace():
    i = 0
    while i < totalFaces:
        faceSel = str(item + '.f[{}]'.format(i))
        print 'faceSel =', faceSel
        maya.select(faceSel)
        getVerticesInFace()
        i += 1
    return i, faceSel
 
#=================END_OF_FUNCTIONS===============================
 
 
sel = maya.ls(selection = True)
print 'Selection:', sel
 
totalFaces = []
totalVtx = []
 
for item in sel:
    totalFaces = maya.polyEvaluate(face = True)
    print 'Faces =', totalFaces
 
    totalVtx = maya.polyEvaluate(vertex = True)
    print 'Vertices =', totalVtx
    print 'item =', item
    print 'sel =', sel
    selectFace()
