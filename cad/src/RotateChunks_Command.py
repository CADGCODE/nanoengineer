# Copyright 2008 Nanorex, Inc.  See LICENSE file for details. 
"""

@author: Ninad
@copyright: 2008 Nanorex, Inc.  See LICENSE file for details.
@version:$Id$

History:
Created while splititng class modifyMode into command and GraphicsMode. 

NOTE:
As of 2008-01-25, this command is not yet used however its graphics mode class
(RotateChunks_GraphicsMode) is used as an alternative graphics mode in 
Move_Command
"""
from Move_Command import Move_Command
from RotateChunks_GraphicsMode import RotateChunks_GraphicsMode

_superclass = Move_Command
class RotateChunks_Command(Move_Command):
     
    commandName = 'ROTATE_CHUNKS'
    featurename = "Rotate Chunks"
    
    command_can_be_suspended = False
    command_should_resume_prevMode = True 
    command_has_its_own_gui = False
    
    GraphicsMode_class = RotateChunks_GraphicsMode
    
    
    def init_gui(self):
        """
        Do changes to the GUI while entering this command.      
        Called once each time the command is entered; should be called only by 
        code  in modes.py
        As of 2008-01-25, this method does nothing.
        
        @see: L{self.restore_gui}
        """
        pass
    
    def connect_or_disconnect_signals(self, isConnect):
        """
        Connect or disconnect widget signals sent to their slot methods.
        @param isConnect: If True the widget will send the signals to the slot 
                          method. 
        @type  isConnect: boolean
        As of 2008-01-25, this method does nothing.
        """
        pass
        
    def restore_gui(self):
        """
        Do changes to the GUI while exiting this command. 
        As of 2008-01-25, this method does nothing.
        @see: L{self.init_gui}
        """
        pass
    