# Deletes the mentioned camera's cropmasks.

import maya.cmds as cmds #imports Maya Python commands library
 
#_____FUNCTIONS_____________________________________________________________________
 
def deleteCropMask(camName):
    print
    if cmds.objExists("{0}_:camera_:rig_:render_:cameraLeft_cropMask".format(camName)): #Checks if the object exists in the outliner
        cmds.select("{0}_:camera_:rig_:render_:cameraLeft_cropMask".format(camName)) #Selects the cropMask asset inside of Camera rig
        cmds.delete( hierarchy='cameraLeft_cropMask' ) #Deletes the cropMask
    else:
        print("ATTENTION: There is no cropMask present in this camera.")
        print("Please check in the Attribute Editor of the selected Camera, under ImagePlanes group!")
#______________________________________</>Functions</end>_____________________    
 
cam = cmds.promptDialog(message="Please write the camera name or full camera asset name: ") #Pops a dialog box to type the camera name
deleteCropMask(cam) #Runs Function to delete the cropMask

