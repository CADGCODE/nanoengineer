# Copyright 2007-2008 Nanorex, Inc.  See LICENSE file for details. 
"""
Plane_EditCommand.py

@author: Ninad,
@copyright: 2007-2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
ninad 20070606: Created.
ninad 2007-10-05: Refactored, Also renamed PlaneGenerator to Plane_EditCommand
                  while refactoring the old GeometryGeneratorBaseClass
ninad 2007-12-26: Changes to make Plane_EditCommand a command on command stack

@TODO 2008-04-15:
Note that Plane_EditCommand was originally implemented before the command 
sequencer was operational. This class and its Property Manager has some methods 
that need cleanup to matchup with the command/commandsequencer API. 
e.g. in its PM, the method update_props_if_needed_before_closing need to be 
revised because there is any easy way now, to know which command is currently 
active.Also a general clanup is due -- Ninad
"""

from utilities.Log import greenmsg
from command_support.EditCommand import EditCommand
from commands.PlaneProperties.PlanePropertyManager import PlanePropertyManager
from model.Plane import Plane
from commands.SelectAtoms.SelectAtoms_GraphicsMode import SelectAtoms_GraphicsMode
from utilities.Comparison import same_vals


class Plane_EditCommand(EditCommand):
    """
    The Plane_EditCommand class  provides an editCommand Object.
    The editCommand, depending on what client code needs it to do, may create 
    a new plane or it may be used for an existing plane. 
    """

    #@NOTE: self.struct is the Plane object

    cmd = greenmsg("Plane: ")
    #
    prefix = '' # Not used by jigs.
    # All jigs like rotary and linear motors already created their
    # name, so do not (re)create it (in GeneratorBaseClass) from the prefix.
    create_name_from_prefix = False 
    # We now support multiple keywords in a list or tuple
    # sponsor_keyword = ('Graphenes', 'Carbon')
    sponsor_keyword = 'Plane'
    #See Command.anyCommand for details about the following flags

    #command_can_be_suspended = False mitigates bug similar to bug 2699
    #(atleast it removes the property manager) . Actual fix will be cleanup of 
    #command/command sequencer and inscreasing the command stack depth
    #-- Ninad 2008-04-15
    command_can_be_suspended = False 
    command_should_resume_prevMode = True
    command_has_its_own_gui = True
        # When <command_should_resume_prevMode> and <command_has_its_own_gui>
        # are both set to True (like here), want_confirmation_corner_type()
        # will determine that the confirmation corner should include the
        # Transient-Done image, which is sometimes OK and sometimes not OK.
        # This is what bug 2701 is about (assigned to me). I will talk to Ninad
        # and Bruce about fixing this (after Rattlesnake). 
        # --Mark 2008-03-24

    commandName = 'REFERENCE_PLANE'
    featurename = "Reference Plane"

    GraphicsMode_class = SelectAtoms_GraphicsMode


    def __init__(self, commandSequencer, struct = None):
        """
        Constructs an Edit Controller Object. The editCommand, 
        depending on what client code needs it to do, may create a new plane 
        or it may be used for an existing plane. 

        @param win: The NE1 main window.
        @type  win: QMainWindow

        @param struct: The model object (in this case plane) that the 
                       Plane_EditCommand may create and/or edit
                       If struct object is specified, it means this 
                       editCommand will be used to edit that struct. 
        @type  struct: L{Plane} or None

        @see: L{Plane.__init__}
        """     
        EditCommand.__init__(self, commandSequencer)
        self.struct = struct   

    def Enter(self):
        """
        Enter this command. 
        @see: EditCommand.Enter
        """
        #See EditCommand.Enter for a detailed comment on why self.struct is 
        #set to None while entering this command.
        if self.struct:
            self.struct = None

        EditCommand.Enter(self)

    def restore_gui(self):
        """
        @see: EditCommand.restore_gui
        """
        EditCommand.restore_gui(self)
        #Following call doesn't update the struct with steps similar to 
        #ones in bug 2699. Instead calling struct.updateCosmeticProps directly
        ##self.propMgr.update_props_if_needed_before_closing()
        if self.hasValidStructure():
            self.struct.updateCosmeticProps() 


    def _getStructureType(self):
        """
        Subclasses override this method to define their own structure type. 
        Returns the type of the structure this editCommand supports. 
        This is used in isinstance test. 
        @see: EditCommand._getStructureType() (overridden here)
        """
        return Plane

    def _createPropMgrObject(self):
        """
        Creates a property manager  object (that defines UI things) for this 
        editCommand. 
        """
        assert not self.propMgr

        propMgr = self.win.createPlanePropMgr_if_needed(self)

        return propMgr


    def placePlaneParallelToScreen(self):
        """
        Orient this plane such that it is placed parallel to the screen
        """
        self.struct.placePlaneParallelToScreen()


    def placePlaneThroughAtoms(self):
        """
        Orient this plane such that its center is same as the common center of 
        three or more selected atoms.
        """
        self.struct.placePlaneThroughAtoms()
        #NOTE: This log message can be used to either display a history message 
        #if using NE1 UI or for consol print when command is executed via 
        #command prompt. Its upto the client to use this message. This, 
        #however needs a global updater that will clear previous log message 
        #from this object, in order to avoid errors. (if in some cases, the 
        #logMessage is not there, client could accidentaly use garbage 
        #logMessage hanging out from some previous execution) 
        #This is subject to revision. May not be needed after once Logging 
        #facility (see Log.py) is fully implemented -- Ninad 20070921
        self.logMessage = self.cmd + self.struct.logMessage

    def placePlaneOffsetToAnother(self):
        """
        Orient the plane such that it is parallel to a selected plane , with an
        offset.
        """
        self.struct.placePlaneOffsetToAnother()
        self.logMessage = self.cmd + self.struct.logMessage


    ##=========== Structure Generator like interface ======##
    def _gatherParameters(self):
        """
        Return all the parameters from the Plane Property Manager.
        """
        height  =  self.propMgr.heightDblSpinBox.value()
        width   =  self.propMgr.widthDblSpinBox.value()
        atmList =  self.win.assy.selatoms_list()
        self.propMgr.changePlanePlacement(
            self.propMgr.pmPlacementOptions.checkedId())
        if self.struct:            
            ctr     =  self.struct.center 
            imagePath = self.struct.imagePath    
        else:
            ctr = None
        
        #gather grid related values
        showGrid = self.propMgr.gridPlaneCheckBox.isChecked()
        gridColor = self.propMgr.gridColor
        gridXSpacing = self.propMgr.gridXSpacing
        gridYSpacing = self.propMgr.gridYSpacing
        gridLineType = self.propMgr.gridLineType
        displayLabels = self.propMgr.displayLabels
        originLocation = self.propMgr.originLocation 
        labelDisplayStyle = self.propMgr.labelDisplayStyle 
        
        return (width, height, ctr, atmList, imagePath, showGrid, 
                gridColor, gridLineType, gridXSpacing, 
                gridYSpacing, displayLabels, originLocation, labelDisplayStyle)
        
    def _createStructure(self):
        """
        Create a Plane object. (The model object which this edit controller 
        creates) 
        """
        assert not self.struct

        struct = Plane(self.win, self)

        return struct


    def _modifyStructure(self, params):
        """
        Modifies the structure (Plane) using the provided params.
        @param params: The parameters used as an input to modify the structure
                       (Plane created using this Plane_EditCommand) 
        @type  params: tuple
        """
        assert self.struct
        assert params 
        assert len(params) == 13             
        width, height, center_junk, atmList_junk, imagePath, \
             showGrid, gridColor, gridLineType, gridXSpacing, \
             gridYSpacing, displayLabels, originLocation, displayLabelStyle = params
      
        self.struct.width   =  width        
        self.struct.height  =  height 
        self.struct.imagePath = imagePath
        self.struct.showGrid = showGrid
        self.struct.gridColor = gridColor
        self.struct.gridLineType = gridLineType
        self.struct.gridXSpacing = gridXSpacing
        self.struct.gridYSpacing = gridYSpacing
        self.struct.displayLabels = displayLabels 
        self.struct.originLocation = originLocation
        self.struct.displayLabelStyle = displayLabelStyle
        
        self.win.win_update() # Update model tree
        self.win.assy.changed()        

    ##=====================================##
    
    def model_changed(self):
        
        #check first if the plane object exists first
        if self.hasValidStructure() is None:
            return
        
        # piotr 080617 
        # fixed plane resizing bug - should return if the plane
        # is being interactively modified
        if self.propMgr.resized_from_glpane:
            return
        
        #see if values in PM has changed
        currentParams = self._gatherParameters()

        if same_vals(currentParams,self.propMgr.previousPMParams):
            return
        
        self.propMgr.previousPMParams = currentParams
        self._modifyStructure(currentParams)
        
        