# Copyright 2004-2007 Nanorex, Inc.  See LICENSE file for details. 
"""
Command.py -- 

$Id$


WARNING: this file is temporarily OWNED by bruce,
since it is being split out of modes.py.


History:

bruce 071009 split modes.py into Command.py and GraphicsMode.py,
leaving only temporary compatibility mixins in modes.py.
For prior history see modes.py docstring before the split.

TODO:

A lot of methods in class Command are private helper methods,
available to subclasses and/or to default implems of public methods,
but are not yet named as private or otherwise distinguished
from API methods. We should turn anyCommand into Command_API,
add all the API methods to it, and rename the other methods
in class Command to look private.
"""

from PyQt4.Qt import QToolButton

from debug import print_compact_traceback

import platform
from PlatformDependent import shift_name
from PlatformDependent import control_name
from PlatformDependent import context_menu_prefix

import env # not used as of 071010 morning
from state_utils import StateMixin

from constants import noop

from jigs import Jig

# ==

class anyCommand(object, StateMixin): #bruce 071008 added object superclass; 071009 split anyMode -> anyCommand
    """
    abstract superclass for all Command objects, including nullCommand
    """

    # TODO: revise 'mode' term in this comment and in modename, msg_modename attributes.
    
    # default values for mode-object attributes.  external code
    # assumes every mode has these attributes, but it should pretend
    # they're read-only; mode-related code (in this file) can override
    # them in subclasses and/or instances, and modify them directly.
    
    # internal name of mode, e.g. 'DEPOSIT',
    # only seen by users in "debug" error messages
    modename = "(bug: missing modename 1)" 
    # name of mode to be shown to users, as a phrase, e.g. 'sketch mode'
    msg_modename = "(bug: unknown mode)"
    
    # Command's property manager. Subclasses should initialize the propMgr object 
    # if they need one.     
    propMgr = None
    
    def get_mode_status_text(self):
        # I think this will never be shown [bruce 040927]
        return "(bug: mode status text)"

    # (default methods that should be noops in both nullCommand and Command
    #  can be put here instead if desired)
    
    def selection_changed(self): #bruce 070925
        return
    
    def model_changed(self): #bruce 070925
        return

    def state_may_have_changed(self): #bruce 070925
        return

    def isCurrentCommand(self): #bruce 071008
        return False

    pass # end of class anyCommand


class nullCommand(anyCommand):
    """
    do-nothing command (for internal use only) to avoid crashes
    in case of certain bugs during transition between commands
    """

    # needs no __init__ method; constructor takes no arguments
    
    # WARNING: the next two methods are similar in all "null objects", of which
    # we have nullCommand and nullGraphicsMode so far. They ought to be moved
    # into a common nullObjectMixin for all kinds of "null objects". [bruce 071009]
    
    def noop_method(self, *args, **kws):
        if platform.atom_debug:
            print "fyi: atom_debug: nullCommand noop method called -- probably ok; ignored"
        return None #e print a warning?
    def __getattr__(self, attr): # in class nullCommand
        # note: this is not inherited by other Command classes,
        # since we are not their superclass
        if not attr.startswith('_'):
            if platform.atom_debug:
                print "fyi: atom_debug: nullCommand.__getattr__(%r) -- probably ok; returned noop method" % attr
            return self.noop_method
        else:
            raise AttributeError, attr #e args?

    # Command-specific attribute null values

    # TODO: revise the 'mode' term in the following

    # (the nullCommand instance is not put into the glpane's commandTable)
    modename = 'nullCommand'
    msg_modename = 'nullCommand'
        # this will be overwritten in the nullCommand instance
        # when the currentCommand is changing [bruce 050106]
    
    # Command-specific null methods
    
    def Done(self, *args, **kws): #bruce 060316 added this to remove frequent harmless debug print
        pass
    
    pass # end of class nullCommand


class basicCommand(anyCommand):
    """
    Common code between class Command (see its docstring)
    and old-code-compatibility class basicMode.
    Will be merged with class Command (keeping that one's name)
    when basicMode is no longer needed.
    """
    
    # Subclasses should define the following class constants,
    # and normally need no __init__ method.
    # If they have an __init__ method, it must call Command.__init__
    # and pass the CommandSequencer in which this command is running.
    modename = "(bug: missing modename)"
    msg_modename = "(bug: unknown command)"
    default_mode_status_text = "(bug: missing command status text)"
    
    def user_modename(self): #bruce 051130 (apparently this is new; it can be the official user-visible-modename method for now)
        "Return a string such as 'Move Mode' or 'Build Mode' -- the name of this mode for users; or '' if unknown."
        ### TODO: move below __init__ or make it a property or so
        if self.default_mode_status_text.startswith("Mode: "):
            return self.default_mode_status_text[len("Mode: "):] + " Mode"
        if self.default_mode_status_text.startswith("Tool: "): 
            # Added for Pan, Rotate and Zoom Tools. Fixes bug 1298. mark 060323
            return self.default_mode_status_text[len("Tool: "):] + " Tool"
        return ''
    
    def __init__(self, commandSequencer):
        """
        This is called once on each newly constructed Command.
        Some kinds of Commands are constructed again each time they are
        invoked; others have a single instance which is reused for
        multiple invocations, but never across open files -- at least
        in the old mode code before 071009 -- not sure, after that).
        In the old code, it's called once per new assembly, since the
        commands store the assembly internally, and that happens once or
        twice when we open a new file, or once when we use file->close.

        This method sets up that command to be available (but not yet active)
        in that commandSequencer's commandTable (mapping modename to command object
        for reusable command objects -- for now that means all of them, by default --
        TODO, revise this somehow, maybe control it by a per-Command class constant).

        REVIEW: are there ever more args, or if the UI wants this to immediately
        do something, does it call some other method immediately? Guess: the latter.
        """

        glpane = commandSequencer ### TODO: clean this up
        
        self.pw = None # pw = part window
            # TODO: remove this, or at least rename it -- most code uses .win for the same thing

        ### REVIEW: with what attrs do a Command and GraphicsMode instance find each other?
        # (let them be properties so they can return self without a cyclic ref)

        } got to here in this method
        
        # init or verify modename and msg_modename
        name = self.modename
        assert not name.startswith('('), \
            "bug: modename class constant missing from subclass %s" % self.__class__.__name__
        if self.msg_modename.startswith('('):
            self.msg_modename = name[0:1].upper() + name[1:].lower() + ' Mode'
                # Capitalized 'Mode'. Fixes bug 612. mark 060323
                # [bruce 050106 capitalized first letter above]
            if 0: # bruce 040923 never mind this suggestion
                print "fyi: it might be better to define 'msg_modename = %r' as a class constant in %s" % \
                  (self.msg_modename, self.__class__.__name__)
        # check whether subclasses override methods we don't want them to
        # (after this works I might remove it, we'll see)
        ### bruce 050130 removing 'Done' temporarily; see PanMode.Done for why.
        # later note: as of 070521, we always get warned "subclass movieMode overrides basicMode._exitMode".
        # I am not sure whether this override is legitimate so I'm not removing the warning for now. [bruce 070521]
        weird_to_override = ['Cancel', 'Flush', 'StartOver', 'Restart',
                             'userSetMode', '_exitMode', 'Abandon', '_cleanup']
            # not 'modifyTransmute', 'keyPress', they are normal to override;
            # not 'draw_selection_curve', 'Wheel', they are none of my business;
            # not 'makemenu' since no relation to new mode changes per se.
            # [bruce 040924]
        for attr in weird_to_override:
            def same_method(m1,m2):
                # m1/m2.im_class will differ (it's the class of the query,
                # not where func is defined), so only test im_func
                return m1.im_func == m2.im_func
            if not same_method( getattr(self,attr) , getattr(basicMode,attr) ):
                print "fyi (for developers): subclass %s overrides basicMode.%s; this is deprecated after mode changes of 040924." % \
                      (self.__class__.__name__, attr)

        # other inits
        self.glpane = glpane
        self.win = glpane.win
        # this doesn't work, since when self is first created during GLPane creation,
        # self.win doesn't yet have this attribute:
        ## self.commandSequencer = self.win.commandSequencer #bruce 070108
        # (note that the exception from this is not very understandable.)
        # So instead, we define a property that does this alias, below.
        
        # Note: the attributes self.o and self.w are deprecated, but often used.
        # New code should use some other attribute, such as self.glpane or
        # self.commandSequencer or self.win, as appropriate. [bruce 070613, 071008]
        self.o = self.glpane
        self.w = self.win
        
        ## self.init_prefs() # no longer needed --
        # Between Alpha 1-8, each mode had its own background color and display mode.
        # For Alpha 9, background color and display mode attrs were moved to the GLPane class where they
        # are global for all modes.
        
        # store ourselves in our glpane's mode table, commandTable
        ###REVIEW whether this is used for anything except changing to new mode by name [bruce 070613 comment]
        self.o.commandTable[self.modename] = self
            # bruce comment 040922: current code can overwrite a prior
            # instance of same mode, when setassy called, eg for file
            # open; this might (or might not) cause some bugs; i
            # should fix this but didn't yet do so as of 040923
            ###REVIEW whether this is still an issue, or newly one [bruce 070613 comment]

        self.setup_menus_in_init()

        return # from basicCommand.__init__

    def get_commandSequencer(self):
        return self.win.commandSequencer #bruce 070108
    
    commandSequencer = property(get_commandSequencer)
    
    def isCurrentCommand(self): #bruce 071008, for Command API
        """
        Return a boolean to indicate whether self is the currently active command.
        Note: this is False even if self is temporarily suspended by e.g. Pan Tool,
        but self's UI is still fully displayed; this needs to be considered when
        this method is used to determine whether UI actions should have an effect.
        """
        return self.commandSequencer.currentCommand is self

    def set_cmdname(self, name):
        """
        Helper method for setting the cmdname to be used by Undo/Redo.
        Called by undoable user operations which run within the context
        of this Command.
        """
        self.win.assy.current_command_info(cmdname = name)

    ### TODO: move this up, and rename to indicate it's about the graphics area's empty space context menus
    call_makeMenus_for_each_event = False # default value of class attribute; subclasses can override

    def setup_graphics_menu_specs(self):
        ### TODO: make this more easily customized, esp the web help part;
        ### TODO if possible: fix the API (also of makeMenus) to not depend on setting attrs as side effect
        """
        Call self.makeMenus(), postprocess the menu_spec attrs
        it sets on self [###doc: name them here],
        and leave those set on self for the caller to (presumably)
        turn into actual menus.
        
        (TODO: when we know we're called for each event, optim by producing
         only whichever menu_specs are needed. This is not always just one,
         since we sometimes copy one into a submenu of another.)
        """
        # Note: this was split between Command.setup_graphics_menu_specs and
        # GraphicsMode.setup_menus, bruce 071009

        # lists of attributes of self we examine and perhaps remake:
        mod_attrs = ['Menu_spec_shift', 'Menu_spec_control']
        all_attrs = ['Menu_spec'] + mod_attrs + ['debug_Menu_spec']

        # delete any Menu_spec attrs previously set on self
        # (needed when self.call_makeMenus_for_each_event is true)
        for attr in all_attrs:
            if hasattr(self, attr):
                del self.__dict__[attr]
        
        #bruce 050416: give it a default menu; for modes we have now, this won't ever be seen unless there are bugs
        #bruce 060407 update: improve the text, re bug 1739 comment #3, since it's now visible for zoom/pan/rotate tools
        self.Menu_spec = [("%s" % self.user_modename(), noop, 'disabled')]
        self.makeMenus() # bruce 040923 moved this here, from the subclasses; for most modes, it replaces self.Menu_spec
        # bruce 041103 changed details of what self.makeMenus() should do
        
        # self.makeMenus should have set self.Menu_spec, and maybe some sister attrs
        assert hasattr(self, 'Menu_spec'), "%r.makeMenus() failed to set up" \
               " self.Menu_spec (to be a menu spec list)" % self # should never happen after 050416
        orig_Menu_spec = list(self.Menu_spec)
            # save a copy for comparisons, before we modify it
        # define the ones not defined by self.makeMenus;
        # make them all unique lists by copying them,
        # to avoid trouble when we modify them later.
        for attr in mod_attrs:
            if not hasattr(self, attr):
                setattr(self, attr, list(self.Menu_spec))
                # note: spec should be a list (which is copyable)
        for attr in ['debug_Menu_spec']:
            if not hasattr(self, attr):
                setattr(self, attr, [])
        for attr in ['Menu_spec']:
            setattr(self, attr, list(getattr(self, attr)))
        if platform.atom_debug and self.debug_Menu_spec:
            # put the debug items into the main menu
            self.Menu_spec.extend( [None] + self.debug_Menu_spec )
            # [note, bruce 050914, re bug 971: [edited 071009, 'mode' -> 'command']
            #  for commands that don't remake their menus on each use,
            #  the user who turns on ATOM-DEBUG won't see the menu items defined by debug_Menu_spec
            #  until they remake all command objects (lazily?) by opening a new file. This might change if we remake command objects
            #  more often (like whenever the command is entered), but the best fix would be to remake all menus on each use.
            #  But this requires review of the menu-spec making code for each command (for correctness when run often),
            #  so for now, it has to be enabled per-command by setting command.call_makeMenus_for_each_event for that command.
            #  It's worth doing this in the commands that define command.debug_Menu_spec.]
        
        # new feature, bruce 041103:
        # add submenus to Menu_spec for each modifier-key menu which is
        # nonempty and different than Menu_spec
        # (was prototyped in extrudeMode.py, bruce 041010]
        doit = []
        for attr, modkeyname in [
                ('Menu_spec_shift', shift_name()),
                ('Menu_spec_control', control_name()) ]:
            submenu_spec = getattr(self, attr)
            if orig_Menu_spec != submenu_spec and submenu_spec:
                doit.append( (modkeyname, submenu_spec) )
        if doit:
            self.Menu_spec.append(None)
            for modkeyname, submenu_spec in doit:
                itemtext = '%s-%s Menu' % (context_menu_prefix(), modkeyname)
                self.Menu_spec.append( (itemtext, submenu_spec) )
            # note: use platform.py functions so names work on Mac or non-Mac,
            # e.g. "Control-Shift Menu" vs. "Right-Shift Menu",
            # or   "Control-Command Menu" vs. "Right-Control Menu".
            # [bruce 041014]
        if isinstance( self.o.selobj, Jig): # NFR 1740. mark 060322
            # TODO: find out whether this works at all (I would be surprised if it does,
            #  since I'd think that we'd never call this if selobj is not None);
            # if it does, put it on the Jig's cmenu maker, not here, if possible;
            # if it doesn't, also put it there if NFR 1740 remains undone and desired.
            # [bruce comment 071009]
            from wiki_help import wiki_help_menuspec_for_object
            ms = wiki_help_menuspec_for_object( self.o.selobj )
            if ms:
                self.Menu_spec.append( None )
                self.Menu_spec.extend( ms )
        else:
            featurename = self.user_modename()
            if featurename:
                from wiki_help import wiki_help_menuspec_for_featurename
                ms = wiki_help_menuspec_for_featurename( featurename )
                if ms:
                    self.Menu_spec.append( None ) # there's a bug in this separator, for cookiemode...
                        # [did I fix that? I vaguely recall fixing a separator logic bug in the menu_spec processor... bruce 071009]
                    # might this look better before the above submenus, with no separator?
                    ## self.Menu_spec.append( ("web help: " + self.user_modename(), self.menucmd_open_wiki_help_page) )
                    self.Menu_spec.extend( ms )
        return # from setup_graphics_menu_specs

    def makeMenus(self):
        ### TODO: rename to indicate it's about the graphics area's empty space context menus; move above setup_graphics_menu_specs
        """
        [Subclasses can override this to assign menu_spec lists (describing
        the context menus they want to have) to self.Menu_specs (and related attributes).
        [### TODO: doc the related attributes, or point to an example that shows them all.]
        Depending on a class constant call_makeMenus_for_each_event (default False),
        this will be called once during init (default behavior) or on every mousedown
        that needs to put up a context menu (useful for "dynamic context menus").]
        """
        pass ###e move the default menu_spec to here in case subclasses want to use it?

    # ==

    # confirmation corner methods [bruce 070405-070409, 070627]

    # Note [obs?]: if we extend the conf. corner to "generators" in the short term,
    # before the "command sequencer" is implemented, some of the following methods
    # may be revised to delegate to the "current generator" or its PM.
    # If so, when doing this, note that many modes currently act as their own PM widget.

    def _KLUGE_current_PM(self): #bruce 070627
        "private, and a kluge; see KLUGE_current_PropertyManager docstring for more info"
        pw = self.w.activePartWindow()
        if not pw:
            # I don't know if pw can be None
            print "fyi: _KLUGE_current_PM sees pw of None" ###
            return None
        try:
            res = pw.KLUGE_current_PropertyManager()
            # print "debug note: _KLUGE_current_PM returns %r" % (res,)
            return res
        except:
            # I don't know if this can happen
            print_compact_traceback("ignoring exception in %r.KLUGE_current_PropertyManager(): " % (pw,))
            return None
        pass

    def _KLUGE_visible_PM_buttons(self): #bruce 070627
        """private (but ok for use by self._ccinstance), and a kluge:
        return the Done and Cancel QToolButtons of the current PM,
        if they are visible, or None for each one that is not visible.
           Used both for deciding what CC buttons to show, and for acting on the buttons
        (assuming they are QToolButtons).
        """
        pm = self._KLUGE_current_PM()
        if not pm:
            return None, None # no CC if no PM is visible
        def examine(buttonname):
            try:
                button = getattr(pm, buttonname)
                assert button
                assert isinstance(button, QToolButton)
                vis = button.isVisibleTo(pm)
                    # note: we use isVisibleTo(pm) rather than isVisible(),
                    # as part of fixing bug 2523 [bruce 070829]
                if vis:
                    res = button
                else:
                    res = None
            except:
                print_compact_traceback("ignoring exception (%r): " % buttonname)
                res = None
            return res
        return ( examine('done_btn'), examine('abort_btn') )

    def want_confirmation_corner_type(self):
        """
        Subclasses should return the type of confirmation corner they currently want,
        typically computed from their current state. The return value can be one of the
        strings 'Done+Cancel' or 'Done' or 'Cancel', or None (for no conf. corner).
        Later we may add another possible value, 'Exit'.
        [See confirmation_corner.py for related info.]
        [Many subclasses will need to override this; we might also revise the default
         to be computed in a more often correct manner.]
        """
        # What we do:
        # find the current PM (self or an active generator, at the moment -- very klugy),
        # and ask which of these buttons are visible to it (rather than using self.haveNontrivialState()):
        #   pm.done_btn.isVisibleTo(pm)
        #   pm.abort_btn.isVisibleTo(pm).
        # WE also use them to perform the actions (they are QToolButtons). KLUGE: we do this in
        # other code which finds them again redundantly (calling the same kluge helper function).
        from debug_prefs import debug_pref, Choice_boolean_False
        if debug_pref("Conf corner test: use haveNontrivialState", Choice_boolean_False, prefs_key = True):
            # old code, works, but not correct for default mode or when generators active
            if self.haveNontrivialState():
                return 'Done+Cancel'
            else:
                # when would we just return 'Cancel'? only for a generator?
                return 'Done' # in future this will sometimes or always be 'Exit'
        else:
            done_button_vis, cancel_button_vis = self._KLUGE_visible_PM_buttons()
                # each one is either None, or a QToolButton (a true value) currently displayed on the current PM

            res = []
            if done_button_vis:
                res.append('Done')
            if cancel_button_vis:
                res.append('Cancel')
            if not res:
                res = None
            else:
                res = '+'.join(res)
            # print "want cc got", res
            return res
        pass
    
    # ==

    def warning(self, *args, **kws):
        self.o.warning(*args, **kws)

    # == entering this mode
    
    def _enterMode(self, resuming = False): #bruce 070813 added resuming option, 
        
        """Private method (called only by our glpane) -- immediately
           enter this mode, i.e. prepare it for use, not worrying at
           all about any prior current mode.  Return something false
           (e.g. None) normally, or something true if you want to
           refuse entry to the new mode (see comments in the call to
           this for why you might want to do that).  Note that the
           calling glpane has not yet set its self.mode to point to us
           when it calls this method, and it will never do so unless
           we return something false (as we usually do).  Should not
           be overridden by subclasses.
           
           [by bruce 040922; see head comment of this file for how
           this relates to previous code]

           @param resuming: whether we're resuming this mode (after a completed
                            subcommand); otherwise we're entering it as if anew.
                            This is for use by Subcommands resuming their parent
                            commands.
           @type resuming: bool
        """
        if not resuming:
            refused = self.refuseEnter(warn = 1)
            if not refused:
                # do mode-specific entry initialization;
                # this method is still allowed to refuse, as well
                refused = self.Enter() 
                if refused:
                    print "fyi: late refusal by %r, better if it had been in refuseEnter" % self # (but sometimes it might be necessary)
        else:
            refused = False
        if not refused:
            self.init_gui() ###FIX: perhaps use resume_gui instead, if resuming -- or pass that option.
            self.update_gui() # see also UpdateDashboard
            self.update_mode_status_text()
        # caller (our glpane) will set its self.mode to point to us,
        # but only if we return false
        return refused

    def refuseEnter(self, warn):
        """Subclasses should override this: examine the current
           selection state of your glpane, and anything else you care
           about, and decide whether you would refuse to become the
           new current mode, if asked to. If you would refuse, and if
           warn = true, then emit an error message explaining this.
           In any case, return whether you refuse entry (i.e. true if
           you do, false if you don't).           
           [by bruce 040922. I expect no existing modes to override
           this, but extrude and revolve probably will.]           
        """
        return 0
    
    def Enter(self):
        # bruce 040922 split each subclass setMode into Enter and init_gui
        # -- see file head comment for details
        """Subclasses should override this: first call basicMode.Enter(self).
           Then set whatever internal state you need to upon being entered,
           modify settings in your glpane (self.o) if necessary,
           and return None.           
           If something goes wrong, so that you don't accept being the
           new current mode, emit an error message explaining why
           (perhaps in a dialog or status bar), and return True -- but
           it's better if you can figure this out earlier, in
           refuseEnter().           
           [by bruce 040922; see head comment of this file for how
           this relates to previous code]           
        """
        self.UpdateDashboard() # Added to hide Done button for Default mode. Mark 050922.
        self.picking = False
        self.update_cursor()
        return None

    def init_gui(self):
        # bruce 041124 clarified docstring, revised illegitimate calls.
        """Subclasses should define this to set up UI stuff like dashboards,
        cursors, toggle icons, etc.
           It should be called only once each time the mode is entered.
        Therefore, it should not be called by other code (for that,
        see UpdateDashboard()), nor defined by modes to do things that
        need redoing many times per mode-entry (for that, see
        update_gui()).
        """
        pass

    def update_gui(self): # bruce 041124
        """Subclasses should define this to update their dashboard to reflect state
        that might have changed in the rest of the program, e.g. selection state
        in the model tree. Not intended to be called directly by external code;
        for that, see UpdateDashboard().
        """
        pass

    def UpdateDashboard(self): # bruce 041124
        """Public method, meant to be called only on the current mode object:
           Make sure this mode's dashboard is updated before the processing of
        the current user event is finished.
           External code that might change things which some modes
        need to reflect in their dashboard should call this one or more times
        after any such changes, before the end of the same user event.
           Multiple calls per event are ok (but in the initial implem might
        be slow). Subclasses should not override this; for that, see update_gui().
        """
        # For now, this method just updates the dashboard immediately.
        # This might be too slow if it's called many times per event, so someday
        # we might split this into separate invalidation and update code;
        # this will then be the invalidation routine, in spite of the name.
        # We *don't* also call update_mode_status_text -- that's separate.
        
        # This shows the Done button on the dashboard unless the current mode is the 
        # Default mode. Resolves bug #958 and #959. Mark 050922.
        import UserPrefs
        if self.modename == UserPrefs.default_modename(): #bruce 060403 revised this
            self.w.toolsDoneAction.setVisible(0)
        else:
            self.w.toolsDoneAction.setVisible(1)
        
        if self.now_using_this_mode_object(): #bruce 050122 added this condition
            self.update_gui()
        return

    def now_using_this_mode_object(self): #bruce 050122 moved this here from extrudeMode.py
        """Return true if the glpane is presently using this mode object
        (not just a mode object with the same name!)
           Useful in "slot methods" that receive Qt signals from a dashboard
        to reject signals that are meant for a newer mode object of the same class,
        in case the old mode didn't disconnect those signals from its own methods
        (as it ideally should do).
           Warning: this returns false while a mode is still being entered (i.e.
        during the calls of Enter and init_gui, and the first call of update_gui).
        But it's not a good idea to rely on that behavior -- if you do, you should
        redefine this function to guarantee it, and add suitable comments near the
        places which *could* set self.o.mode to the mode object being entered,
        earlier than they do now.
        """
        return self.o.mode == self
        
    def update_mode_status_text(self):        
        """##### new method, bruce 040927; here is my guess at its doc
           [maybe already obs?]: Update the mode-status widget to show
           the currently correct mode-status text for this mode.
           Subclasses should not override this; its main purpose is to
           know how to do this in the environment of any mode.  This
           is called by the standard mode-entering code when it's sure
           we're entering a new mode, and whenever it suspects the
           correct status text might have changed (e.g. after certain
           user events #nim).  It can also be called by modes
           themselves when they think the correct text might have
           changed.  To actually *specify* that text, they should do
           whatever they need to do (which might differ for each mode)
           to change the value which would be returned by their
           mode-specific method get_mode_status_text().           
        """
        self.w.update_mode_status( mode_obj = self)
            # fyi: this gets the text from self.get_mode_status_text();
            # mode_obj = self is needed in case glpane.mode == nullMode
            #  at the moment.

    def selection_changed(self): #bruce 070925 added this to mode/command API
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any selection state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.
        It will be called at most approximately once per user mouse or key
        event. The calling code should try not to call it when not needed,
        but needn't guarantee this, so implementations should try to be fast
        when the call was not needed.
           Model state or other selection state should NOT be updated by
        this method -- doing so may cause bugs of a variety of kinds,
        for example in the division of changes into undoable commands
        or in the consistency of state which requires update calls after
        it's changed.
           See also update_gui; this method is typically implemented
        more efficiently and called much more widely, and (together with
        similar new methods for other kinds of state) should eventually
        replace update_gui.
        """
        ### REVIEW: Decide whether highlighting (selobj) is covered by it (guess yes -- all kinds of selection).
        ### maybe TODO: call when entering/resuming the mode, and say so, and document order of call
        # relative to update_gui. And deprecate update_gui or make it more efficient.
        # And add other methods that only use usage-tracked state and are only called as needed.
        if self.propMgr:
            if hasattr( self.propMgr, 'selection_changed'):
                self.propMgr.selection_changed()
        return

    def model_changed(self): #bruce 070925 added this to mode/command API
        """
        Subclasses should extend this (or make sure their self.propMgr defines
        it) to check whether any model state has changed that should be
        reflected in their UI, and if so, update their UI accordingly.
           Model state or selection state should NOT be updated by
        this method.
           See selection_changed docstring for more info.
        """
        ### maybe TODO: same as for selection_changed.
        if self.propMgr:
            if hasattr( self.propMgr, 'model_changed'):
                self.propMgr.model_changed()
        return

    def state_may_have_changed(self): #bruce 070925 added this to command API
        """
        Call model_changed and/or selection_changed as needed, in that order.
        Not normally overridden by subclasses [I hope].
        Called by env.do_post_event_updates.
        """
        ### TODO: call each method only when needed, using assy change counters, and maybe a selobj test.
        self.model_changed()
        self.selection_changed()
        return
    
    def get_mode_status_text(self):        
        """##### new method, bruce 040927; doc is tentative [maybe
           already obs?]; btw this overrides an AnyMode method:        
           Return the correct text to show right now in the
           mode-status widget (e.g."Mode: Build",
           "Mode: Select Chunks").           
           The default implementation is suitable for modes in which this
           text never varies, assuming they properly define the class
           constant default_mode_status_text; other modes will need to
           override this method to compute that text in the correct way,
           and will *also* need to ensure that their update_mode_status_text()
           method is called
           whenever the correct mode status text might have changed,
           if it might not be called often enough by default.           
           [### but how often it's called by default is not yet known
           -- e.g. if we do it after every button or menu event, maybe no
           special calls should be needed... we'll see.]            
        """
        return self.default_mode_status_text

    # methods for changing to some other mode
    
    def userSetMode(self, modename, **options):        
        """User has asked to change to the given modename; we might or
           might not permit this, depending on our own state.  If we
           permit it, do it; if not, show an appropriate error
           message.  Exception: if we're already in that mode, do
           nothing.           
           [bruce 040922]
        """
        if self.modename == modename:
            if self.o.mode == self:
                # changing from the active mode to itself -- do nothing
                # (special case, not equivalent to behavior without it)
                return
            else:
                # I don't think this can happen, but if it does,
                #it's either a bug or we're some fake mode like nullMode. #k
                print "fyi (for developers): self.modename == modename but not self.o.mode == self (probably ok)" ###
                # now change modes in the normal way
        # bruce 041007 removing code for warning about changes and requiring
        # explicit Done or Cancel if self.haveNontrivialState()
        self.Done( modename, **options)
        return

    # methods for leaving this mode (from a dashboard tool or an
    # internal request).

    # Notes on state-accumulating modes, e.g. cookie extrude revolve
    # deposit [bruce 040923]:
    #
    # Each mode which accumulates state, meant to be put into its
    # glpane's assembly in the end, decides how much to put in as it
    # goes -- that part needs to be "undone" (removed from the
    # assembly) to support a Cancel event -- versus how much to retain
    # internally -- that part needs to be "done" (put into in the
    # assembly) upon a Done event.  (BTW, as I write this, I think
    # that only depositMode (so far) puts any state into the assembly
    # before it's Done.)
    #
    # Both kinds of state (stored in the mode or in the assembly)
    # should be considered when overriding self.haveNontrivialState()
    # -- it should say whether Done and Cancel should have different
    # ultimate effects. (Note "should" rather than "would" --
    # i.e. even if Cancel does not yet work, like in depositMode,
    # haveNontrivialState should return True based on what Cancel
    # ought to do, not based on what it actually does. That way the
    # user won't miss a warning message saying that Cancel doesn't
    # work yet.)
    #
    # StateDone should actually put the unsaved state from here into
    # the assembly; StateCancel should remove the state which was
    # already put into the assembly by this mode's operation (but only
    # since the last time it was entered). Either of those can also
    # emit an error message and return True to refuse to do the
    # requested operation of Done or Cancel (they normally return
    # None).  If they return True, we assume they made no changes to
    # the stored state, in the mode or in the assembly (but we have no
    # way of enforcing that; bugs are likely if they get this wrong).
    #
    # I believe that exactly one of StateDone and StateCancel will be
    # called, for any way of leaving a mode, except for Abandon, if
    # self.haveNontrivialState() returns true; if it returns false,
    # neither of them will be called.
    #
    # -- bruce 040923

    def Done(self, new_mode = None, suspend_old_mode = False, **new_mode_options):
        """Done tool in dashboard; also called internally (in
           userSetMode and elsewhere) if user asks to start a new mode
           and current mode decides that's ok, without needing an
           explicit Done.  Change [bruce 040922]: Should not be
           overridden in subclasses; instead they should override
           haveNontrivialState and/or StateDone and/or StateCancel as
           appropriate.
        """
        if not suspend_old_mode:
            if self.haveNontrivialState(): # use this (tho it should be just an optim), to make sure it's not giving false negatives
                refused = self.StateDone()
                if refused:
                    # subclass says not to honor the Done request (and it already emitted an appropriate message)
                    return
        new_mode_options['suspend_old_mode'] = suspend_old_mode
        self._exitMode( new_mode, **new_mode_options)
        return

    def StateDone(self):
        """Mode objects (e.g. cookieMode) which might have accumulated
           state which is not yet put into the model (their glpane's
           assembly) should override this StateDone method to put that
           state into the model, and return None.  If, however, for
           some reason they want to refuse to let the user's Done
           event be honored, they should instead (not changing the
           model) emit an error message and return True.
        """
        assert 0, "bug: mode subclass %r needs custom StateDone method, since its haveNontrivialState() apparently returned True" % \
               self.__class__.__name__
    
    def Cancel(self, new_mode = None, **new_mode_options):
        """Cancel tool in dashboard; might also be called internally
           (but is not as of 040922, I think).  Change [bruce 040922]:
           Should not be overridden in subclasses; instead they should
           override haveNontrivialState and/or StateDone and/or
           StateCancel as appropriate.
        """
        ###REVIEW: any need to support suspend_old_mode here? I doubt it...
        # but maybe complain if it's passed. [bruce 070814]
        if self.haveNontrivialState():
            refused = self.StateCancel()
            if refused:
                # subclass says not to honor the Cancel request (and it already emitted an appropriate message)
                return
        self._exitMode( new_mode, **new_mode_options)

    def StateCancel(self):
        """Mode objects (e.g. depositMode) which might have
           accumulated state directly into the model (their glpane's
           assembly) should override this StateCancel method to undo
           those changes in the model, and return None.
           Alternatively, if they are unable to remove that state from
           the model (e.g. if that code is not yet implemented, or too
           hard to implement correctly), they should warn the user,
           and then either leave all state unchanged (in mode object
           and model) and return True (to refuse to honor the user's
           Cancel request), or go ahead and leave the unwanted state
           in the model, and return None (which honors the Cancel but
           leaves the user with unwanted new state in the model).
           Perhaps, when they warn the user, they would ask which of
           those two things to do.
        """
        return None # this is correct for all existing modes except depositMode
                    # -- bruce 040923
        ## assert 0, "bug: mode subclass %r needs custom StateCancel method, since its haveNontrivialState() apparently returned True" % \
        ##       self.__class__.__name__

    def haveNontrivialState(self):
        """Subclasses which accumulate state (either in the mode
           object or in their glpane's assembly, or both) should
           override this appropriately (see long comment above for
           details).  False positive is annoying, but permitted (its
           only harm is forcing the user to explicitly Cancel or Done
           when switching directly into some other mode); but false
           negative would be a bug, and would cause lost state after
           Done or (for some modes) incorrectly
           uncancelled/un-warned-about state after Cancel.
        """
        return False
    
    def _exitMode(self, new_mode = None, suspend_old_mode = False, **new_mode_options):
        """Internal method -- immediately leave this mode, discarding
           any internal state it might have without checking whether
           that's ok (if that check might be needed, we assume it
           already happened).  Ask our glpane to change to new_mode
           (which might be a modename or a mode object or None), if provided
           (and if that mode accepts being the new mode), otherwise to
           its default mode.  Unlikely to be overridden by subclasses.
           [by bruce 040922]
        """
        if not suspend_old_mode:
            self._cleanup()
        if new_mode is None:
            new_mode = '$DEFAULT_MODE'
        self.o.start_using_mode(new_mode, **new_mode_options)
            ## REVIEW: is suspend_old_mode needed in start_using_mode?
            # Tentative conclusion: its only effect would be how to fall back
            # if using the new mode fails -- it would make us fall back to
            # old mode rather than to default mode. Ideally we'd use a
            # continuation-like style, wrapping new_mode with a fallback
            # mode, and pass that as new_mode. So it's not worth fixing this
            # for now -- save it for when we have a real command-sequencer.
            # [bruce 070814 comment]
        return

    def Abandon(self):
        """This is only used when we are forced to Cancel, whether or not this
           is ok (with the user) to do now -- someday it should never be called.
           Basically, every call of this is by definition a bug -- but
           one that can't be fixed in the mode-related code alone.
           [But it would be easy to fix in the file-opening code, once we
           agree on how.]
        """
        if self.haveNontrivialState():
            msg = "%s with changes is being forced to abandon those changes!\n" \
                  "Sorry, no choice for now." % (self.msg_modename,)
            self.o.warning( msg, bother_user_with_dialog = 1 )
        # don't do self._exitMode(), since it sets a new mode and
        #ultimately asks glpane to update for that... which is
        #premature now.  #e should we extend _exitMode to accept
        #modenames of 'nullMode', and not update? also 'default'?
        #probably not...
        self._cleanup()

    def _cleanup(self):
        # (the following are probably only called together, but it's
        # good to split up their effects as documented in case we
        # someday call them separately, and also just for code
        # clarity. -- bruce 040923)
        self.o.stop_sending_us_events( self)
            # stop receiving events from our glpane (i.e. use nullMode)
        self.restore_gui()
        self.w.setFocus() #bruce 041010 bugfix (needed in two places)
            # (I think that was needed to prevent key events from being sent to
            #  no-longer-shown mode dashboards. [bruce 041220])
        self.restore_patches()
        self.clear() # clear our internal state, if any
        
    def restore_gui(self):
        "subclasses use this to restore UI stuff like dashboards, cursors, toggle icons, etc."
        pass

    def restore_patches(self):
        """subclasses should restore anything they temporarily
        modified in client objects (such as display modes in their
        glpane)"""
        pass
    
    def clear(self):
        """subclasses with internal state should reset it to null
        values (somewhat redundant with Enter; best to clear things
        now)"""
        pass
        
    # [bruce comment 040923]
    
    # The preceding and following methods, StartOver Cancel Backup
    # Done, handle the common tools on the dashboards.  (Before
    # 040923, Cancel was called Flush and StartOver was called
    # Restart. Now the internal names match the user-visible names.)
    #
    # Each dashboard uses instances of the same tools, for a uniform
    # look and action; the tool itself does not know which mode it
    # belongs to -- its action just calls glpane.mode.method for the
    # current glpane and for one of the specified methods (or Flush,
    # the old name of Cancel, until we fix MWSemantics).
    #
    # Of these methods, Done and Cancel should never be customized
    # directly -- rather, subclasses for specific modes should
    # override some of the methods they call, as described in this
    # file's header comment.
    #
    # StartOver should also never be customized, since the generic
    # method here should always work.
    #
    # For Backup, I [bruce 040923] have not yet revised it in any
    # way. Some subclasses override it, but AFAIK mostly don't do so
    # properly yet.

    # other dashboard tools
    
    def StartOver(self):
        # it looks like only cookieMode tried to do this [bruce 040923];
        # now we do it generically here [bruce 040924]
        """Start Over tool in dashboard (used to be called Restart);
        subclasses should NOT override this"""
        self.Cancel(new_mode = self.modename)
#### works, but has wrong error message when nim in sketch mode -- fix later

    def Backup(self):
        # it looks like only cookieMode tries to do this [bruce 040923]
        "Backup tool in dashboard; subclasses should override this"
        print "%s: Backup not implemented yet" % self.msg_modename

    # compatibility methods -- remove these after we fix
    # MWSemantics.py for their new names
    
    def Flush(self):
        self.Cancel() # let old name work for now

    def Restart(self):
        self.StartOver() # let old name work for now

    pass # end of class basicCommand

# ==

class Command(basicCommand):
    """
    Subclass this class to create a new Command, or more often,
    a new general type of Command. This class contains code which
    most Command classes need. [See basicCommand docstring about
    how and when that class will be merged with this class.]

    A Command is a temporary mode of interaction
    for the entire UI which the user enters in order to accomplish
    a specific operation or kind of interaction. Some Commands exit
    very soon and on their own, but most can endure indefinitely
    until the user activates a Done or Cancel action to exit them.

    An instance of a Command subclass corresponds to a single run
    of a command, which may or may not have actually become active
    and/or still be active. Mode-like commands may repeatedly become
    active due to separate user actions, whereas operation-like commands
    are more likely to be active just once (with new instances of the
    same class being created when the user again asks for the same
    operation to occur).
    """
    def __init__(self, commandSequencer):
        }
    pass

# end
