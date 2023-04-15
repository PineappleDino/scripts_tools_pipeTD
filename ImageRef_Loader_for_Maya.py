#Created by Alex Santos - Montreal
 
import pymel.core as pm
import maya.cmds as cmds
import maya
import os, sys
from PIL import Image, ExifTags
 
#LoadImageRef
#Load an Image as Reference
#Loads an image of your choice, to use as a reference on a plane object. (Turn ON "Textured" option in viewport)
 
class ImageReference():
    def _fileDialog():
        file_path = pm.fileDialog2(fileMode=4)
        return file_path
 
    def _getImageInfo(file_):
        #picFile = Image.open("/job/pipeline/dev/sandbox/sandbox_adocoito/work/adocoito/maya/images/imageSeqexample/Total_Swimming02_reference_Reference_v002_main.1001.jpg")
        print file_
        picFile = Image.open(file_)
        print 'Format = {0};\n Size = {1};\n ColorMode = {2}'.format(picFile.format, picFile.size, picFile.mode)
        return picFile.size
 
    def _createPolyPlane(x, y, fileImage, xTranslate):
        plane = cmds.polyPlane(name = 'Image_Reference',
                            object = True,
                            width = x, 
                            height = y, 
                            subdivisionsX = 1,
                            subdivisionsY = 1,
                            constructionHistory = True,
                            createUVs = 1)
        print plane
        cmds.select(plane)
        cmds.scale(0.05, 1, 0.05)
        
 
        #creates shader
        shader = cmds.shadingNode("blinn",
                                asShader = True, 
                                name = 'surfaceShader_Ref')
        print shader
 
        #creates a file texture node and defines the 'imagesequence' file location
        file_node = cmds.shadingNode("file", asTexture = True, name = 'texture_ImageTexture')
        file = fileImage
        print file
 
        #create a shading group
        cmds.select(plane, shader, file_node)
        shading_group = cmds.sets(name = "texture_ImageReferenceSG",
                                renderable = True,
                                noSurfaceShader = False,
                                empty = True)
        cmds.sets(e=True, forceElement= shading_group)
 
        cmds.connectAttr('%s.outColor' %shader, '%s.surfaceShader' %shading_group, force = True)
        cmds.connectAttr('%s.outColor' %file_node, '%s.color' %shader, force = True)
 
        pm.setAttr('%s.fileTextureName'%file_node, file)
        pm.setAttr('%s.incandescence'%shader, 1, 1, 1, type = 'double3')
        pm.setAttr('%s.diffuse'%shader, 1 )
        pm.setAttr('%s.translucenceDepth'%shader, 0 )
        pm.setAttr('%s.translucenceFocus'%shader, 0 )
        pm.setAttr('%s.eccentricity'%shader, 0 )
        pm.setAttr('%s.specularRollOff'%shader, 0 )
        pm.setAttr('%s.specularColor'%shader, 0, 0, 0, type='double3')
        pm.setAttr('%s.reflectivity'%shader, 0 )
 
        cmds.move(xTranslate, moveX = True)
 
    file_path = []
    file_path = _fileDialog() #result in _fileDialog func needs to be attributed to the variable file_path.
    xMove = 0
 
    for i in file_path:
        print "File =", i
        print "File Path =", file_path
        image_size = _getImageInfo(i)
        print "Image Size =", image_size
        subdivWidth = image_size[0]
        subdivHeight = image_size[1]
        planeObj = _createPolyPlane(subdivWidth, subdivHeight, i, xMove)
        xMove += 100
 
ImageReference()


