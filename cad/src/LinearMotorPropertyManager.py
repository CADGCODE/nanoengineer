# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
LinearMotorPropertyManager.py

@author: Ninad
@version: $Id$
@copyright: 2004-2007 Nanorex, Inc.  See LICENSE file for details. 

History:
ninad 2007-10-11: Created, deprecating the LinearMototorPropDialog.py
"""

from PyQt4.Qt import SIGNAL

from PM.PM_GroupBox      import PM_GroupBox
from PM.PM_DoubleSpinBox import PM_DoubleSpinBox
from PM.PM_CheckBox      import PM_CheckBox
from PM.PM_PushButton    import PM_PushButton

from widgets import RGBf_to_QColor

from MotorPropertyManager import MotorPropertyManager

from constants import gray

class LinearMotorPropertyManager(MotorPropertyManager):
    """
    The LinearMotorProperty manager class provides UI and propMgr object for the
    LinearMotor_EditCommand.
    """
    # The title that appears in the Property Manager header.
    title = "Linear Motor"
    # The name of this Property Manager. This will be set to
    # the name of the PM_Dialog object via setObjectName().
    pmName = title
    # The relative path to the PNG file that appears in the header
    iconPath = "ui/actions/Simulation/Linear_Motor.png"
    
    def __init__(self, win, motorEditCommand):
        """
        Construct the Linear Motor Property Manager.    
        """
                
        MotorPropertyManager.__init__( self, 
                                       win,
                                       motorEditCommand) 
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        This can be overridden in subclasses. By default it does nothing.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        """
        if isConnect:
            change_connect = self.win.connect
        else:
            change_connect = self.win.disconnect
        
        MotorPropertyManager.connect_or_disconnect_signals(self, isConnect)
        
        change_connect(self.directionPushButton, 
                     SIGNAL("clicked()"), 
                     self.reverse_direction)
        change_connect(self.motorLengthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        change_connect(self.motorWidthDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        change_connect(self.spokeRadiusDblSpinBox, 
                     SIGNAL("valueChanged(double)"), 
                     self.change_motor_size)
        change_connect(self.colorPushButton, 
                     SIGNAL("clicked()"), 
                     self.change_jig_color)
    
    def _update_widgets_in_PM_before_show(self):
        """
        Update various widgets  in this Property manager.
        Overrides MotorPropertyManager._update_widgets_in_PM_before_show. 
        The various  widgets , (e.g. spinboxes) will get values from the 
        structure for which this propMgr is constructed for 
        (self.editcCntroller.struct)
        
        @see: MotorPropertyManager._update_widgets_in_PM_before_show
        @see: self.show where it is called. 
        """       
        if self.editCommand and self.editCommand.struct:            
            force = self.editCommand.struct.force
            stiffness = self.editCommand.struct.stiffness
            enable_minimize = self.editCommand.struct.enable_minimize
            
            length = self.editCommand.struct.length
            width = self.editCommand.struct.width
            spoke_radius = self.editCommand.struct.sradius
            normcolor = self.editCommand.struct.normcolor
        else:
            force = 0.0
            stiffness = 0.0
            enable_minimize = False
            
            length = 10
            width = 1
            spoke_radius = 0.2
            normcolor = gray
            
        self.forceDblSpinBox.setValue(force)
        self.stiffnessDblSpinBox.setValue(stiffness)
        self.enableMinimizeCheckBox.setChecked(enable_minimize)
        
        self.motorLengthDblSpinBox.setValue(length)
        self.motorWidthDblSpinBox.setValue(width)
        self.spokeRadiusDblSpinBox.setValue(spoke_radius)
        self.jig_QColor = RGBf_to_QColor(normcolor)
        
    
    def change_motor_size(self, gl_update=True):
        """
        Slot method to change the jig's length, width and/or spoke radius.
        """
        self.editCommand.struct.length = self.motorLengthDblSpinBox.value()
        self.editCommand.struct.width =  self.motorWidthDblSpinBox.value()
        # spoke radius --
        self.editCommand.struct.sradius = self.spokeRadiusDblSpinBox.value()
        if gl_update:
            self.glpane.gl_update()
            
    def _loadGroupBox1(self, pmGroupBox):
        """
        Load widgets in MotorParamsGroupBox.
        """                
        if self.editCommand and self.editCommand.struct:
            force = self.editCommand.struct.force
            stiffness = self.editCommand.struct.stiffness
            enable_minimize = self.editCommand.struct.enable_minimize
        else:
            force = 0.0
            stiffness = 0.0
            enable_minimize = False
            
        self.forceDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label = "Force:", 
                             value = force, 
                             setAsDefault = True,
                             minimum    = 0.0, 
                             maximum    = 5000.0, 
                             singleStep = 1.0, 
                             decimals   = 1, 
                             suffix     =' pN')
        self.stiffnessDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                             label = "Stiffness:", 
                             value = stiffness, 
                             setAsDefault = True,
                             minimum    = 0.0, 
                             maximum    = 1000.0, 
                             singleStep = 1.0, 
                             decimals   = 1, 
                             suffix     =' N/m')
                       
        self.enableMinimizeCheckBox = \
            PM_CheckBox(pmGroupBox,
                        text ="Enable in Minimize",
                        widgetColumn = 1
                        )
        self.enableMinimizeCheckBox.setChecked(enable_minimize)
        
        self.directionPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Direction :",
                          text = "Reverse",
                          spanWidth = False)
    
    
    def _loadGroupBox2(self, pmGroupBox):
        """
        Load widgets in groubox 2.
        """
        
        if self.editCommand and self.editCommand.struct:
            length = self.editCommand.struct.length
            width = self.editCommand.struct.width
            spoke_radius = self.editCommand.struct.sradius
            normcolor = self.editCommand.struct.normcolor
        else:
            length = 10
            width = 1
            spoke_radius = 0.2
            normcolor = gray
                        
        
        self.motorLengthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Motor Length :", 
                                value = length, 
                                setAsDefault = True,
                                minimum = 0.5, 
                                maximum = 500.0, 
                                singleStep = 0.5, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        
        self.motorWidthDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label="Motor Width :", 
                                value = width, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        
        self.spokeRadiusDblSpinBox = \
            PM_DoubleSpinBox(pmGroupBox, 
                                label = "Spoke Radius :", 
                                value = spoke_radius, 
                                setAsDefault = True,
                                minimum = 0.1, 
                                maximum = 50.0, 
                                singleStep = 0.1, 
                                decimals = 1, 
                                suffix = ' Angstroms')
        
        # Used as default color by Color Chooser
        self.jig_QColor = RGBf_to_QColor(normcolor) 
        
        self.colorPushButton = \
            PM_PushButton(pmGroupBox,
                          label = "Color :",
                          text = "Choose...")
        
    def _addWhatsThisText(self):
        """
        What's This text for widgets in this Property Manager.  
        """
        from gui.WhatsThisText_for_PropertyManagers import whatsThis_LinearMotorPropertyManager
        whatsThis_LinearMotorPropertyManager(self)
        

    def _addToolTipText(self):
        """
        What's Tool Tip text for widgets in this Property Manager.  
        """       
        from gui.ToolTipText_for_PropertyManagers import ToolTip_LinearMotorPropertyManager
        ToolTip_LinearMotorPropertyManager(self)
