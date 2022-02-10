import os
import logging
import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *
from slicer.util import updateVolumeFromArray
import numpy as np
import unittest

#
# Slicerscript_CallingFile
#

class Slicerscript_CallingNumpyFile(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Slicerscript_CallingNumpyFile"  # TODO: make this more human readable by adding spaces
    self.parent.categories = ["SlicerData"]  # TODO: set categories (folders where the module shows up in the module selector)
    self.parent.dependencies = []  # TODO: add here list of module names that this module requires
    self.parent.contributors = ["Steven A. Lewis (University at Buffalo"]  # TODO: replace with "Firstname Lastname (Organization)"
    # TODO: update with short description of the module and a link to online module documentation
    self.parent.helpText = """
    This is a scripted module to help with importing numpy and npz files into 3D Slicer from deep learning outputs."
    """
    # TODO: replace with organization, grant and thanks
    self.parent.acknowledgementText = """
    This file was originally developed by Steven Lewis as part of Univeristy at Buffalo. This module was supported by an NIH F31 grant from the NIBIB, "Improving Virtual Gross Anatomy Education: Enhancing the Information Content of Cadaveric CT Scans."
        awarded to Steven Lewis (1F31EB030904-01): https://reporter.nih.gov/search/aWV_xOncPkCur37APurQHg/project-details/10141430.
    """
    self.parent.helpText += self.getDefaultModuleDocumentationLink()
    self.parent.acknowledgementText = """
    This module was developed by Steven Lewis from University at Buffalo.
    """ # replace with organization, grant and thanks.
    

class Slicerscript_CallingNumpyFileWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setup(self):
    """
    Called when the user opens the module the first time and the widget is initialized.
    """
    # self.operationRadioButtons = []
    self.buttonToOperationNameMap = {}
    ScriptedLoadableModuleWidget.setup(self)

    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)
    # Layout within the dummy collapsible button
    parametersFormLayout = qt.QFormLayout(parametersCollapsibleButton)
    
    #
    # Select Numpy folder to import
    #
    
    self.inputDirectory = ctk.ctkDirectoryButton()
    self.inputDirectory.directory = qt.QDir.homePath()
    self.inputDirectory.setToolTip('Select Directory with npy or npz files')
    parametersFormLayout.addRow("Input Directory:", self.inputDirectory)
    self.FileConstraints = qt.QLineEdit()
    self.FileConstraints.setToolTip('Input Specific Search Parameters for Filenames')
    self.FileConstraints.text = "Filename Search Parameter"
    parametersFormLayout.addRow("Filename Constraints:", self.FileConstraints)
    
    #
    # enter filetype parameters for files
    #
    self.FileTypeNPY = qt.QRadioButton("NPY")
    self.FileTypeNPY.setToolTip('Select for NPY Files in Directory')
    # self.operationRadioButtons.append(self.FileTypeNPY)
    self.buttonToOperationNameMap[self.FileTypeNPY] = '.npy'
    self.FileTypeNPZ = qt.QRadioButton("NPZ")
    self.FileTypeNPZ.setToolTip('Select for NPZ Files in Directory')
    # self.operationRadioButtons.append(self.FileTypeNPZ)
    self.buttonToOperationNameMap[self.FileTypeNPZ] = '.npz'
    self.NPZArrayName = qt.QLineEdit()
    self.NPZArrayName.text = "arr_0"
    
    # self.parameters.addLabeledOptionsWidget("Operation:", operationLayout)
    
    typesLayout = qt.QGridLayout()
    typesLayout.addWidget(self.FileTypeNPY, 0, 0)
    typesLayout.addWidget(self.FileTypeNPZ, 0, 1)
    typesLayout.addWidget(self.NPZArrayName, 0, 2)
    
    parametersFormLayout.addRow("File Information:", typesLayout)
    
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.objectName = self.__class__.__name__ + 'Apply'
    self.applyButton.toolTip = "Run the Loading."
    self.applyButton.enabled = False
    parametersFormLayout.addRow(self.applyButton)
    
    # connections
    self.applyButton.connect('clicked(bool)', self.onApply)    
    self.inputDirectory.connect('validInputChanged(bool)', self.onSelectInput) 
    
    # Add vertical spacer
    self.layout.addStretch(1)

    # Refresh Apply button state
    self.onSelectInput()

    # Create logic class. Logic implements all computations that should be possible to run
    # in batch mode, without a graphical user interface.
    self.logic = Slicerscript_CallingNumpyFileLogic()
    
  def onApply(self):
    constraints = self.FileConstraints.text
    if constraints != "Filename Search Parameter":
	    params = True
    else:
        params = False
    isFormatNpy = self.FileTypeNPY.checked
    if(isFormatNpy == True):
        data_type = '.npy'
    else:
        data_type = '.npz'
    # operationButton = list(self.buttonToOperationNameMap.keys())[list(self.buttonToOperationNameMap.values()).index(operationName)]
    # operationButton.setChecked(True)
    logic = Slicerscript_CallingNumpyFileLogic()
    params = bool(self.FileConstraints)
    if(params == True):
        Data = [f for f in os.listdir(self.inputDirectory.directory) if self.FileConstraints and data_type in f]
    else:
        Data == [f for f in os.listdir(self.inputDirectory.directory) if data_type in f]
    if(Data == []):
        logging.info("No numpy files found in: ", self.inputDirectory.Directory)
        return False
    NPZarrayname = self.NPZArrayName.text
    logic.run(self.inputDirectory.directory, Data, data_type, NPZarrayname)
    
  # def onOperationSelectionChanged(self, data_type, toggle):
    # if not toggle:
      # return
    # parameter = {"Operation": [self.buttonToOperationNameMap[self.FileTypeNPY], self.buttonToOperationNameMap[self.FileTypeNPZ]]}
    # print(parameter)
    
  def onSelectInput(self):
    self.applyButton.enabled = bool(self.inputDirectory.directory)

class Slicerscript_CallingNumpyFileLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def run(self, inputDirectory, Data, data_type, NPZarrayname):
    for idx, nodeName in enumerate(Data):
        name = nodeName.replace(data_type, "")
        img_path = os.path.join(inputDirectory, nodeName)
        data_type = data_type
        if data_type == (".npz"):
            img = np.load(img_path)[NPZarrayname]
        else:
            img = np.load(img_path)
        if len(np.shape(img)) == 4:
            for c in range(0,4):
                i = img[c,:,:,:]
                nodeName = 'index_{}_output_{}'.format(idx, c)
                volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", name)
                updateVolumeFromArray(volumeNode, i)
        else:
            volumeNode = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLScalarVolumeNode", name)
            updateVolumeFromArray(volumeNode, img)
        print('Done Loading Volume: {}'.format(name))
    logging.info("Processing complete")   
    return True