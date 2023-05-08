#!/usr/bin/env python
#-*- coding:utf-8 -*-…
 
""" 
==============================================================
    
    Rename Base Code by: Pierre-Luc Seguin/Guillaume Arrieux
    Qt GUI Interface and extra adjustments: Alex Santos/PineappleDino
 
==============================================================
 
"""
import os, sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
 
 
class _fileRenamer(QDialog):
    def __init__(self):
        super(self.__class__, self).__init__()
        self.refresh = False
        self.setWindowTitle("Filename Editor")
        self.setGeometry(500,80,450,300)
 
        self.setLayout(QVBoxLayout())
        self.path_namesLayout = QVBoxLayout()
        self.layout().addLayout(self.path_namesLayout)
 
        #__GUI Elements Variables___________________________________
        self.path_Label = QLabel()
        self.path_Edit = QLineEdit()
        self.oldName_Label = QLabel()
        self.oldName_Edit = QLineEdit()
        self.newName_Label = QLabel()
        self.newName_Edit = QLineEdit()
        self.applyChanges_Button = QPushButton("Apply Changes")
        self.revertChanges_Button = QPushButton("Revert Changes")
        self.statusBar = QStatusBar()
 
        #__GUI Elements add to Layout________________________________
        self.path_namesLayout.addWidget(self.path_Label)
        self.path_namesLayout.addWidget(self.path_Edit)
        self.path_namesLayout.addWidget(self.oldName_Label)
        self.path_namesLayout.addWidget(self.oldName_Edit)
        self.path_namesLayout.addWidget(self.newName_Label)
        self.path_namesLayout.addWidget(self.newName_Edit)
        self.path_namesLayout.addWidget(self.applyChanges_Button)
        self.path_namesLayout.addWidget(self.revertChanges_Button)
        self.path_namesLayout.addWidget(self.statusBar)

        #__GUI Elements Edit____________________________
        self.path_Label.setText("Type or paste the PATH of the directory below, " +
            "where the files are located:")
        self.oldName_Label.setText("\nType or paste the OLD name, or " + 
            "section of the filename you want to edit:")
        self.newName_Label.setText("Type or paste the NEW name, " + 
            "that you want to edit to:")
 
        self.statusBar.showMessage("Welcome!")
        
        
        #__GUI SetStyleSheet/Colors_________________________
        self.setStyleSheet("background-color: rgb(50,50,50); color: white;")
 
        self.path_Label.setStyleSheet("padding: 0 25px -2")
        self.path_Edit.setStyleSheet("background-color: rgb(0, 0, 0); color: yellow; border: 1px #303030; padding: 7; border-style: inset; border-width:6px")
 
        self.oldName_Label.setStyleSheet("padding: 10 0 -2")
        self.oldName_Edit.setStyleSheet("background-color: rgb(0, 0, 0); color: #B3FFFF; border: 2px #303030; padding: 2 10px; border-style: inset; border-width:4px; border-radius: 10px;")
 
        self.newName_Label.setStyleSheet("padding: 3 0 -2")
        self.newName_Edit.setStyleSheet("background-color: rgb(0, 0, 0); color: #00FF00; border: 2px #303030; padding: 2 10px; border-style: inset; border-width:4px; border-radius: 10px;")
 
        self.applyChanges_Button.setStyleSheet("QPushButton {background-color: #282828; border-style: outset; border-width: 8px; border-color: #404040; padding: 10px;}"
                                               "QPushButton:pressed {border-style: inset}")
 
        self.revertChanges_Button.setStyleSheet("QPushButton {background-color: #282828; border-style: outset; border-width: 8px; border-color: #404040; padding: 3px;}"
                                                "QPushButton:pressed {border-style: inset}")
 
        self.statusBar.setStyleSheet("background-color: black; color: white;")
 
        #__GUI Element Attribution to Function ___________________________
        self.show()
 
        self.applyChanges_Button.clicked.connect(self._buttonPress)
        self.revertChanges_Button.clicked.connect(self._buttonPressRevert)
 
    def _buttonPress(self):
        filepath = self.path_Edit.text()
        print filepath
        
        old = self.oldName_Edit.text()
        print old
        new = self.newName_Edit.text()
        print new
 
        if filepath == '' or old == '' or new == '':
            self.statusBar.showMessage("Please fill the required info above............")
            self.statusBar.setStyleSheet("background-color: rgb(255, 102, 102); color: black")
        else:
            self._getPath(filepath)
            self._renamer(filepath, old, new)
 
            self.statusBar.showMessage("Files have been renamed!")
            self.statusBar.setStyleSheet("background-color: rgb(153, 255, 153); color: black")
 
    def _buttonPressRevert(self):
        filepath = self.path_Edit.text()
        print filepath
        
        new = self.newName_Edit.text()
        print new
        old = self.oldName_Edit.text()
        print old
 
        if filepath == '' or old == '' or new == '':
            self.statusBar.showMessage("Please fill the required info above...........")
            self.statusBar.setStyleSheet("background-color: rgb(255, 102, 102); color: black")
        else:
            self._getPath(filepath)
            self._renamerRevert(filepath, old, new)
 
            self.statusBar.showMessage("Changes have been reverted!")
            self.statusBar.setStyleSheet("background-color: rgb(221, 255, 153); color: black")

 
    def _getPath(self, filepath):
        print filepath
        path = str(filepath)
        print "path =", path
        return path, filepath
 
    def _renamer(self, filepath, old, new):
        filenames = os.listdir(filepath)
        print "Filenames =", filenames
        print "OldName =", old, "\nNewName=", new
 
        for filename in filenames:
            print "Filename =", filename
            oldName = filepath+'/'+filename
            print "OldName =", oldName
            newName = filepath+'/'+filename.replace(old, new)
            print "NewName =", newName
            os.rename(oldName, newName)
 
    def _renamerRevert(self, filepath, old, new):
        filenames = os.listdir(filepath)
        print "Filenames =", filenames
        print "NewName =", new, "OldName", old
 
        for filename in filenames:
            print "Filename =", filename
            newName = filepath+'/'+filename
            print "NewName =", newName
            oldName = filepath+'/'+filename.replace(new, old)
            print "OldName =", oldName
            os.rename(newName, oldName)
 
if __name__ == '__main__':
    #session = Session()
    app = QApplication(sys.argv)
    ui = _fileRenamer()
    sys.exit(app.exec_())
