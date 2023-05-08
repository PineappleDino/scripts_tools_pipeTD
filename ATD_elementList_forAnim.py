#!/usr/bin/env python

import sys, os, shutil, argparse
from <studio-asset-api>.session import Session
from <studio-asset-api>.session.search import *
from <studio-asset-api>.session.constants import *
# ElementList imports
import <studio-element-lister-UI>.asset
from <studio-element-lister-UI>.editor.ui.elementlisteditorwidget import ElementListEditorWidget
import <studio-pipeline>.core.lib as pipeLib
from <studio-asset-api>.ui.assetselectordialog import AssetSelectorDialog
from <ATD-scripts-library.qt.widgets import ShotPicker
 
try:
    from PySide2 import QtCore, QtGui, QtWidgets
    Signal = QtCore.Signal
except ImportError:
    from PyQt4 import QtCore, QtGui, QtGui as QtWidgets
    Signal = QtCore.pyqtSignal
 
# ============================= Main CLASS = self =============================
class mainWindow(QtWidgets.QWidget):
    #_________________________________________________________________________________
    #_________________/ MAIN GUI \____________________________________________________
    def __init__(self):
        super(self.__class__, self).__init__()
 
        self.refresh = False
 
        self.setWindowTitle("Element List assets VS Animation Instances")
        self.setGeometry(500, 70, 1100, 1000)
 
        self.setLayout(QtWidgets.QVBoxLayout())
        self.shotPickLayout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(self.shotPickLayout)
        self.textInfoLayout = QtWidgets.QHBoxLayout()
        self.layout().addLayout(self.textInfoLayout)
 
        self.eleText = QtWidgets.QTextEdit()
        self.otherInfo = QtWidgets.QTextEdit()
        self.animInstText = QtWidgets.QTextEdit()
        self.runButton = QtWidgets.QPushButton("\n\nRefresh!\n\n")
        self.missingElements = QtWidgets.QPushButton("\n\nAdd and Publish\nMISSING \nElements\n\n")
        self.openEle = QtWidgets.QPushButton("\nOpen \nElement List \nEditor\n")
 
        self.statusBar = QtWidgets.QStatusBar()
             self.statusBar.showMessage("Select the Division, Sequence and Shot on the top-left.")
        self.layout().addWidget(self.statusBar)
 
        # ========= SHOT PICKER  ========
        self.shotPick = ShotPicker(shot=_shot,sequence=_sequence, division=_division, show=_show)
        print _shot, _sequence, _division, _show
        self.shotPickLayout.addWidget(self.shotPick)
        self.shotPick.setGeometry(10,10,100,100)
        self.shotPick.completed.connect(self._refresh) #Calls function ShotPicker with the function refresh, to cancel out loading the function two times.
 
        self.shotPick.shotCombo.setCurrentIndex(self.shotPick.shotCombo.findText(_shot))
        print self.shotPick.shot
        # ========= /end SHOT PICKER ======
 
        # Element List box
        self.eleText.setReadOnly(True)
        self.eleText.setGeometry(10,80,300,810)
        self.textInfoLayout.addWidget(self.eleText)
 
        # Comparison Info Box
        self.otherInfo.setReadOnly(True)
        self.otherInfo.setGeometry(630,80,300,810)
        self.otherInfo.setStyleSheet("background-color: rgb(192, 192, 192);")
        self.textInfoLayout.addWidget(self.otherInfo)
 
        # Animation Instances List box
        self.animInstText.setReadOnly(True)
        self.animInstText.setGeometry(320,80,300,810)
        self.textInfoLayout.addWidget(self.animInstText)
 
        #Buttons to run scripts
        self.runButton.move(500,30)
        self.runButton.clicked.connect(self._latestElementList_AnimInstances)
        self.shotPickLayout.addWidget(self.runButton)
 
        self.missingElements.move(462,23)
        self.missingElements.clicked.connect(self._addMissingElementInstances)
        self.shotPickLayout.addWidget(self.missingElements)
 
        self.openEle.move(462,23)
        self.openEle.clicked.connect(self._openElementListEditor)
        self.shotPickLayout.addWidget(self.openEle)
        
        self.show()
 
    #_________________________________________________________________________________
    #_______Functions and Main Script_______________________________________________
    def _refresh(self):
        if not self.refresh:
            self._latestElementList_AnimInstances()
            self.refresh = True
        else:
            self.refresh = False
    def _latestElementList_AnimInstances(self):
        #------------Main Variables----------------------------
        self.animPackInstanceList = []
        self.animInstanceListName = []
        self.animInstanceUID = []
        self.animInst_noEle = []
        
        self.shot_asset_path = ("shot", {"show": self.shotPick.show, 
                                "division": self.shotPick.division,
                                "sequence": self.shotPick.sequence,
                                "shot": self.shotPick.shot
                                })
 
        self.eleText.clear()
        self.shot_element_list = elementlist.asset.get(self.shot_asset_path)
 
        if self.shot_element_list == [] or self.shot_element_list == None:
            self.statusBar.setStyleSheet('background-color: rgb(255, 102, 102)')
            self.statusBar.showMessage("There are no Element Lists in this shot. "+
                                       "Please publish a new Element List through"+
                                       " the ElementListEditor")
            self.eleText.append('There are no Element Lists in this shot!')
            pass
        else:
            self.eleText.append("Assets in the latest Element List of this shot: ")
            for element in sorted(self.shot_element_list):
                self.eleText.append('     ' + element)
 
            self.eleText.append("\nVersion of Element List and UID:")
            searchFilterEle = VersionFilter("element_list")
            searchFilterEle.tags.show = self.shotPick.show
            searchFilterEle.tags.division = self.shotPick.division
            searchFilterEle.tags.sequence = self.shotPick.sequence
            searchFilterEle.tags.shot = self.shotPick.shot
            searchFilterEle.version = LATEST
            searchFilterEle.context_name = 'shot'
            resultEle = list(session.advanced_search(searchFilterEle))
 
            for assetEle in resultEle:
                self.eleText.append("     UID       : {0}\n".format(assetEle.uid.value) +
                                    "     Version  : {0}\n".format(assetEle.version.value) +
                                    "     Created : {0}, by {1}".format(assetEle.creation_time.value, assetEle.creator.value))
                self.elelistUID = assetEle.uid.value
 
 
            #----- Animation Instances = LATEST APPROVED -------
            self.animInstText.clear()
            self.animInstText.append("Latest APPROVED Animation Instances:")
            searchFilterAnimInstApproved = VersionFilter('animation_instance')
            searchFilterAnimInstApproved.tags.show = self.shotPick.show
            searchFilterAnimInstApproved.tags.division = self.shotPick.division
            searchFilterAnimInstApproved.tags.sequence = self.shotPick.sequence
            searchFilterAnimInstApproved.tags.shot = self.shotPick.shot
            searchFilterAnimInstApproved.version = RecommendedFilter(approval=REQUIRED)
            searchFilterAnimInstApproved.context_name = 'shot_instance'
            resultAnimInstanceApproved = list(session.advanced_search(searchFilterAnimInstApproved))
 
            if resultAnimInstanceApproved == [] or resultAnimInstanceApproved == None:
                self.animInstText.append('There are no Animation Instances for this shot!')
            else:
                for assetAIApproved in sorted(resultAnimInstanceApproved):
                    self.animInstText.append("    Name     : {0}\n".format(assetAIApproved.instance_name.value) +
                                             "    UID        : {0}\n".format(assetAIApproved.uid.value) +
                                             "    Category: {0}\n".format(assetAIApproved.category.value) +
                                             "    Version   : {0}\n".format(assetAIApproved.version.value) +
                                             "    Created  : {0}, by {1}\n".format(assetAIApproved.creation_time.value, assetAIApproved.creator.value))
                    #self.animInstanceListName.append(assetAIApproved.instance_name.value)
                    self.animInstanceUID.append(assetAIApproved.uid.value)
                self.statusBar.showMessage("Latest Element List and Animation Instances loaded!")
                self.statusBar.setStyleSheet('background-color: rgb(204, 229, 255)')
 
            #---/END\-- Animation Instances = LATEST APPROVED -------
 
            #----- Animation Instances = LATEST -------
            self.animInstText.append("_________________________________")
            self.animInstText.append("\nLatest Animation Instances:")
            searchFilterAnimInst = VersionFilter('animation_instance')
            searchFilterAnimInst.tags.show = self.shotPick.show
            searchFilterAnimInst.tags.division = self.shotPick.division
            searchFilterAnimInst.tags.sequence = self.shotPick.sequence
            searchFilterAnimInst.tags.shot = self.shotPick.shot
            searchFilterAnimInst.version = LATEST
            searchFilterAnimInst.context_name = 'shot_instance'
            resultAnimInstance = list(session.advanced_search(searchFilterAnimInst))
 
            if resultAnimInstance == [] or resultAnimInstance == None:
                self.animInstText.append('There are no Animation Instances for this shot!')
            else:
                for assetAI in sorted(resultAnimInstance):
                    if assetAI.uid.value in self.animInstanceUID:
                        self.animInstText.append("    Name     : {0}\n".format(assetAI.instance_name.value) +
                                                 "    UID        : {0}\n".format(assetAI.uid.value) +
                                                 "    Category: {0}\n".format(assetAI.category.value) +
                                                 "    Version   : {0}\n".format(assetAI.version.value) +
                                                 "    Created  : {0}, by {1}\n".format(assetAI.creation_time.value, assetAI.creator.value) +
                                                 "    APPROVED?   =   Yes!\n")
                        self.animInstanceListName.append(assetAI.instance_name.value)
                    else:
                        self.animInstText.append("    Name     : {0}\n".format(assetAI.instance_name.value) +
                                                 "    UID        : {0}\n".format(assetAI.uid.value) +
                                                 "    Category: {0}\n".format(assetAI.category.value) +
                                                 "    Version   : {0}\n".format(assetAI.version.value) +
                                                 "    Created  : {0}, by {1}\n".format(assetAI.creation_time.value, assetAI.creator.value) +
                                                 "    APPROVED?   =   No...\n")
                        self.animInstanceListName.append(assetAI.instance_name.value)
 
                self.statusBar.showMessage("Latest Element List and Animation Instances loaded!")
                self.statusBar.setStyleSheet('background-color: rgb(204, 229, 255)')
 
            #---/END\-- Animation Instances = LATEST  -------    
 
 
            #--- Animation Package lister -----
            self.animInstText.append('_____________________________\nVersion of Latest Animation Package:')
            searchFilterAnimPack = VersionFilter('animation_package')
            searchFilterAnimPack.context_name = 'shot'
            searchFilterAnimPack.tags.show = self.shotPick.show
            searchFilterAnimPack.tags.division = self.shotPick.division
            searchFilterAnimPack.tags.sequence = self.shotPick.sequence
            searchFilterAnimPack.tags.shot = self.shotPick.shot
            searchFilterAnimPack.version = LATEST
            resultAnimPack = list(session.advanced_search(searchFilterAnimPack))
 
            if resultAnimPack == [] or resultAnimPack == None:
                self.animInstText.append('\nNo Animation Packages for this shot...')
            else:
                for assetAP in sorted(resultAnimPack):
                    self.animInstText.append("   UID   : {0}\n".format(assetAP.uid.value) +
                                            "   Version : {0}\n".format(assetAP.version.value) +
                                            "   Created : {0}, by {1}\n".format(assetAP.creation_time.value, assetAP.creator.value))
 
                    #  List members of latest Animation Package
                    animPackMembers = session.get_group_members(assetAP)
                    self.animInstText.append('__________________')
                    self.animInstText.append('This Animation Package contains these instances:')
                    for member in sorted(animPackMembers):
                        if str(member) in self.animInstanceListName:
                            self.animInstText.append('   {0}'.format(member))
 
            #------/END\----- Animation Package lister ---------------
 
 
 
            #........... Compare Latest Element list with Animation Instances
            self.otherInfo.clear()
            list_of_elements = []
            list_of_elements_noAnim = []
            list_of_animInst_noEle = []
  
            ele_list = sorted(self.shot_element_list)
            animInst_list = sorted(self.animInstanceListName)
 
            for x in ele_list:
                if x in animInst_list:
                    list_of_elements.append(x)
                else:
                    list_of_elements_noAnim.append(x)
 
            for y in animInst_list:
                if y not in ele_list:
                    list_of_animInst_noEle.append(y)
 
            self.otherInfo.append('Elements WITHOUT Animation Instances:')
            if list_of_elements_noAnim == [] or list_of_elements_noAnim == None:
                self.otherInfo.append('      None!')
            else:
                for ele_noanim in sorted(list_of_elements_noAnim):
                    self.otherInfo.append('    {0}'.format(ele_noanim))
 
            self.otherInfo.append('\nElements WITH Animation Instances:')
            if list_of_elements == [] or list_of_elements == None:
                self.otherInfo.append('      None!')
            else:
                for ele in sorted(list_of_elements):
                    self.otherInfo.append('    {0}'.format(ele))
 
            self.otherInfo.append('_____________________________________________')
            self.otherInfo.append('MISSING Animation Instances from \nthe Element List:')
            if list_of_animInst_noEle == [] or list_of_animInst_noEle == None:
                self.otherInfo.append('      None!')
            else:
                for animInstance_noanim in sorted(list_of_animInst_noEle):
                    self.otherInfo.append('    {0}'.format(animInstance_noanim))
 
            self.animInst_noEle = list_of_animInst_noEle
 
            if self.animInst_noEle == []:
                self.statusBar.showMessage("All Animation Instances are already in the Element List")
                self.statusBar.setStyleSheet("background-color: rgb(102, 255, 102)")
            else:
                self.statusBar.showMessage("There are Animation Instances missing from the Element list. Please check the middle box above!")
                self.statusBar.setStyleSheet("background-color: rgb(255, 204, 153)")    
    
    
    def get_animation_instance(self):
        """
        get animation instance using user selected cointext
        """
        searchFilterAnimInst = VersionFilter('animation_instance')
        searchFilterAnimInst.tags.show = self.shotPick.show
        searchFilterAnimInst.tags.division = self.shotPick.division
        searchFilterAnimInst.tags.sequence = self.shotPick.sequence
        searchFilterAnimInst.tags.shot = self.shotPick.shot
        searchFilterAnimInst.version = LATEST
        searchFilterAnimInst.context_name = 'shot_instance'
        resultAnimInstance = list(session.advanced_search(searchFilterAnimInst))
        
        self.animation_instances = resultAnimInstance
        return self.animation_instances
        def get_param_dict(self, name):
        """
        get the defasult parameter dictionary fopr the asset
        """
        show = self.shot_asset_path[1]['show']
        catSubcat = elementlist.asset.get_category_and_subcategory(show, name)
        
        param_dict = {'category':catSubcat[0]
                      ,'name':name
                      ,'subcategory':catSubcat[1]
                      ,'type':'element'}
        
        return param_dict
    
    
    def get_instance_variant(self, anim_inst):
        """
        gets an animation instances rig variant using relationships
        """
        rig_rels = session.get_relationships(destination=anim_inst,
                                             type='dependency', 
                                             source_type='rig_group')
        
        #if for whatever reason theres no rig, just return None, 
        #so it's set to default
        if not rig_rels:
            return None
        
        variant = rig_rels[0].source.variant.value
        
        #if it's default we don't care about it
        if variant == 'default':
            return None
        
        return variant
    
    
    def _addMissingElementInstances(self):
        """
        adds the missing elements to the elementlist, re-written by sporter,
        to fix a number of issues!
        """
        
        #get the elementlist
        self.shot_element_list = elementlist.asset.get(self.shot_asset_path)
        
        #get anim instance
        self.get_animation_instance()
        
        #list to filter by
        cat_list = ['character','vehicle','gizmo','prop','crowd','effects']
                #filters each instance to what is already in the element list, iters through and add instances.
        print sorted(self.animInst_noEle)
        for anim_instance in sorted(self.animation_instances):  
            for AI in sorted(self.animInst_noEle):
                print "AI =", AI
                if AI == anim_instance.instance_name.value:
                    #add instances that are not in element list
                    
                    category = anim_instance.category.value
                
                    #if we don't want it skip it
                    if category not in cat_list:
                        continue
                    
                    #setup some vars
                    instanceName = anim_instance.instance_name.value
                    name = anim_instance.name.value
                    
                    #get the default param dict for the asset
                    param_dict = self.get_param_dict(name)
                    
                    #check if we need a custom variant for the rig that was used
                    #and add if needed
                    variant = self.get_instance_variant(anim_instance)
                    
                    if variant:
                        param_dict['variant'] = variant
                    
                    #add to elementlist
                    self.shot_element_list.add_instance_parameters(instanceName, 
                                                                        param_dict)
                else:
                    pass
        print self.shot_element_list
        self.otherInfo.append("\n______________________________________________")
        self.otherInfo.append("======= NEW ELEMENT LIST =======")
        for element in sorted(self.shot_element_list):
            self.otherInfo.append('    {0}'.format(element))
         self.statusBar.showMessage("New assets added to the new Element List ===> To Publish, press the Publish NEW Element List. Otherwise, edit through the Element List Editor!")
        self.statusBar.setStyleSheet("background-color: rgb(255, 255, 0)")
        
        #---Publishes the new Element List --- Confirmation Dialog
        confirm = QtWidgets.QMessageBox.question(self, 'Publish a new Element List', 'Do want to publish the missing elements into a new Element List?', QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
        if confirm == QtWidgets.QMessageBox.Yes:
            elementlist.asset.publish_element_list(self.shot_element_list, self.shot_asset_path)
            self.statusBar.showMessage("=========  New Element List PUBLISHED!  ==========")
            self.statusBar.setStyleSheet("background-color: rgb(0, 255, 0)")
        else:
            pass
 
    def _openElementListEditor(self):
        self.statusBar.setStyleSheet("background-color: rgb(102, 178, 255)")
        self.statusBar.showMessage(" ===========   OPENING : Element List Editor   =========== ")
        
        os.system("elementlisteditor --show {0} --division {1} --sequence {2} --shot {3}".format(self.shotPick.show, self.shotPick.division, self.shotPick.sequence, self.shotPick.shot)) #sends direct command to Terminal to open elementlisteditor 
 
# ======================== \END/ GUI code ==================    
#==================================================================================    
#==================================================================================
#=================================================================================
#===================================================================================
# __________________________________________________________________________________________
 
#-------------- NON GUI CODE ------------------------------------       
class _noGUI:
    def _elelistVSAnimInst(self):
        self.animPackInstanceList = []
        self.animInstanceListName = []
        self.animInstanceUID = []
        self.animInst_noEle = []
                
        shot_asset_path = ("shot", {"show": _show, 
                                "division": _division,
                                "sequence": _sequence,
                                "shot": _shot
                                })
 
        shot_element_list = elementlist.asset.get(shot_asset_path)
 
        if shot_element_list == [] or shot_element_list == None:
            print "No Element Lists in this shot. Please publish a new Element List through the ElementListEditor"
            pass
        else:
            searchFilterEle = VersionFilter("element_list")
            searchFilterEle.tags.show = _show
            searchFilterEle.tags.division = _division
            searchFilterEle.tags.sequence = _sequence
            searchFilterEle.tags.shot = _shot
            searchFilterEle.version = LATEST
            searchFilterEle.context_name = 'shot'
            resultEle = list(session.advanced_search(searchFilterEle))
 
            for assetEle in resultEle:
                elelistUID = assetEle.uid.value
 
 
            #----- Animation Instances = LATEST APPROVED -------
            searchFilterAnimInstApproved = VersionFilter('animation_instance')
            searchFilterAnimInstApproved.tags.show = _show
            searchFilterAnimInstApproved.tags.division = _division
            searchFilterAnimInstApproved.tags.sequence = _sequence
            searchFilterAnimInstApproved.tags.shot = _shot
            searchFilterAnimInstApproved.version = RecommendedFilter(approval=REQUIRED)
            searchFilterAnimInstApproved.context_name = 'shot_instance'
            resultAnimInstanceApproved = list(session.advanced_search(searchFilterAnimInstApproved))
 
            if resultAnimInstanceApproved == [] or resultAnimInstanceApproved == None:
                print '\nNo Approved Animation Instances for this shot!'
            else:
                for assetAIApproved in sorted(resultAnimInstanceApproved):
                    self.animInstanceUID.append(assetAIApproved.uid.value)
 
            #---/END\-- Animation Instances = LATEST APPROVED -------
 
            #----- Animation Instances = LATEST -------
            searchFilterAnimInst = VersionFilter('animation_instance')
            searchFilterAnimInst.tags.show = _show
            searchFilterAnimInst.tags.division = _division
            searchFilterAnimInst.tags.sequence = _sequence
            searchFilterAnimInst.tags.shot = _shot
            searchFilterAnimInst.version = LATEST
            searchFilterAnimInst.context_name = 'shot_instance'
            resultAnimInstance = list(session.advanced_search(searchFilterAnimInst))
 
            if resultAnimInstance == [] or resultAnimInstance == None:
                print '\nNo Animation Instances for this shot!'
            else:
                for assetAI in sorted(resultAnimInstance):
                    if assetAI.uid.value in self.animInstanceUID:
                        self.animInstanceListName.append(assetAI.instance_name.value)
                    else:
                        self.animInstanceListName.append(assetAI.instance_name.value)
 
            #---/END\-- Animation Instances = LATEST  -------    
 
 
            #--- Animation Package lister -----
            searchFilterAnimPack = VersionFilter('animation_package')
            searchFilterAnimPack.context_name = 'shot'
            searchFilterAnimPack.tags.show = _show
            searchFilterAnimPack.tags.division = _division
            searchFilterAnimPack.tags.sequence = _sequence
            searchFilterAnimPack.tags.shot = _shot
            searchFilterAnimPack.version = LATEST
            resultAnimPack = list(session.advanced_search(searchFilterAnimPack))
 
            if resultAnimPack == [] or resultAnimPack == None:
                print "\n\n No animation packages found...\n"
            else:
                for assetAP in sorted(resultAnimPack):
                    self.animPackInstanceList.append(assetAP.uid.value)
                    # ----- List members of latest Animation Package
                    animPackMembers = session.get_group_members(assetAP)
            #------/END\----- Animation Package lister ---------------
 
 
 
            #........... Compare Latest Element list with Animation Instances
            self.list_of_elements = []
            self.list_of_elements_noAnim = []
            self.list_of_animInst_noEle = []
 
            ele_list = sorted(shot_element_list)
            animInst_list = sorted(self.animInstanceListName)
 
            for x in ele_list:
                if x in animInst_list:
                    self.list_of_elements.append(x)
                else:
                    self.list_of_elements_noAnim.append(x)
 
            for y in animInst_list:
                if y not in ele_list:
                    self.list_of_animInst_noEle.append(y)
 
            print '_____________________________________________'
            print 'MISSING elements from the Element List:'
            if self.list_of_animInst_noEle == [] or self.list_of_animInst_noEle == None:
                print '      None!'
            else:
                for animInstance_noanim in sorted(self.list_of_animInst_noEle):
                    print '    {0}'.format(animInstance_noanim)
 
            self.animInst_noEle = self.list_of_animInst_noEle
 
            if self.animInst_noEle == []:
                print "\nAll Animation Instances are already in the Element List"
            else:
                print "\nThere are Animation Instances missing from the Element list."
 
        return self.animPackInstanceList
        return self.animInstanceListName
        return self.animInstanceUID
        return self.animInst_noEle
        return self.list_of_elements
        return self.list_of_elements_noAnim
        return self.list_of_animInst_noEle
 
    def _addMissingElementInstances_noGUI(self):
            character_listName = []
            vehicle_listName = []
            gizmo_listName = []
            prop_listName = []
            crowd_listName = []
            effects_listName = []
 
            shot_asset_path = ("shot", {"show": _show, 
                                "division": _division,
                                "sequence": _sequence,
                                "shot": _shot
                                })
 
            searchFilterAnimInst = VersionFilter('animation_instance')
            searchFilterAnimInst.tags.show = _show
            searchFilterAnimInst.tags.division = _division
            searchFilterAnimInst.tags.sequence = _sequence
            searchFilterAnimInst.tags.shot = _shot
            searchFilterAnimInst.version = LATEST
            searchFilterAnimInst.context_name = 'shot_instance'
            resultAnimInstance = list(session.advanced_search(searchFilterAnimInst))
                        for AI in resultAnimInstance:
                if AI.category.value == 'character':
                    character_listName.append(AI.instance_name.value)
                elif AI.category.value == 'vehicle':
                    vehicle_listName.append(AI.instance_name.value)
                elif AI.category.value == 'gizmo':
                    gizmo_listName.append(AI.instance_name.value)
                elif AI.category.value == 'prop':
                    prop_listName.append(AI.instance_name.value)
                elif AI.category.value == 'crowd':
                    crowd_listName.append(AI.instance_name.value)
                elif AI.category.value == 'effects':
                    effects_listName.append(AI.instance_name.value)
 
            shot_element_list = elementlist.asset.get(shot_asset_path)
            
            for instance in sorted(self.animInst_noEle):
                instanceName = instance
 
                if instanceName in character_listName:
                    for name in character_listName:
                        if name == instanceName:
                            param_dict = {"category": "character",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
                if instanceName in vehicle_listName:
                    for name in vehicle_listName:
                        if name == instanceName:
                            param_dict = {"category": "vehicle",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
                if instanceName in gizmo_listName:
                    for name in gizmo_listName:
                        if name == instanceName:
                            param_dict = {"category": "gizmo",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
                if instanceName in prop_listName:
                    for name in prop_listName:
                        if name == instanceName:
                            param_dict = {"category": "prop",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
                if instanceName in crowd_listName:
                    for name in crowd_listName:
                        if name == instanceName:
                            param_dict = {"category": "crowd",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
                if instanceName in effects_listName:
                    for name in effects_listName:
                        if name == instanceName:
                            param_dict = {"category": "effects",
                                        "type": "element",
                                        "name": name,
                                        "subcategory": "default"}
                            shot_element_list.add_instance_parameters(instanceName, param_dict)
                        else:
                            pass
 
            print "______________________________________________\n"
            print "======= NEW ELEMENT LIST ======="
            for element in sorted(shot_element_list):
                print '    {0}'.format(element)
 
            #---Publishes the new Element List --- Confirmation Dialog
            confirmYes = ['yes','y']
            confirmNo = ['no','n']
            confirm = raw_input('\nDo want to publish the missing elements into a new Element List? [y/n] \n').lower()
            if confirm in confirmYes:
                elementlist.asset.publish_element_list(shot_element_list, shot_asset_path)
            elif confirm in confirmNo:
                print "\t ==== Skipped publishing the NEW element list ===="
                pass
            else:
                print "Please type Yes or No. Skipping publishing the NEW element list"
                pass
 
#======================== CALLING FUNCTIONS AND UI = __main__  =====================
if __name__ == '__main__':
    args = argparse.ArgumentParser('Query Element List VS Latest approved Animation Instances')
    args.add_argument('-no_gui','-n', required = False, help = 'Use this flag to use the script in Text mode', default = False, action = 'store_true')
    args, extraArgs = args.parse_known_args()
 
    _show = os.environ['PL_SHOW']
    _division = os.environ['PL_DIVISION']
    _sequence = os.environ['PL_SEQ']
    _shot = os.environ['PL_SHOT']
 
    if args.no_gui:
        session = Session()
 
        os.system('clear')
        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        print "     +++++++++ Compare ElementList VS AnimationInstance +++++++++++"
        print '++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++'
        n = _noGUI()
        n._elelistVSAnimInst()
        n._addMissingElementInstances_noGUI()
 
    else:
        try:
            session = Session()
 
            app = QtWidgets.QApplication(sys.argv)
            ui = mainWindow()
            sys.exit(app.exec_())
        except KeyError :
            print 'Please set your environment before using this tool!'
