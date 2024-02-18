# -*- coding: utf-8 -*-
"""
Created on Tue Apr 05 09:21:39 2016

@author: samwebb
"""


######################################################################
### File: PmwDialog.py
# Based on iwidgets2.2.0/dialog.itk and iwidgets2.2.0/dialogshell.itk code.

# Convention:
#   Each dialog window should have one of these as the rightmost button:
#     Close         Close a window which only displays information.
#     Cancel        Close a window which may be used to change the state of
#                   the application.

import sys
import types
import tkinter

import Pmw


class ScrolledListBox(Pmw.ScrolledListBox):
    
    def see(self,*args):
        self._listbox.see(args)

    def show(self,*args):
        #self._listbox.show(args)
        print(args)

# A Toplevel with a ButtonBox and child site.

class Dialog(Pmw.MegaToplevel):
    def __init__(self, parent = None, **kw):

        # Define the megawidget options.
        
        optiondefs = (
            ('buttonbox_hull_borderwidth',   1,         None),
            ('buttonbox_hull_relief',        'raised',  None),
            ('buttonboxpos',                 's',       Pmw.INITOPT),
            ('buttons',                      ('OK',),   self._buttons),
            ('buttonlength',                 5,         Pmw.INITOPT),
            ('command',                      None,      None),
            ('dialogchildsite_borderwidth',  1,         None),
            ('dialogchildsite_relief',       'raised',  None),
            ('defaultbutton',                None,      self._defaultButton),
            ('master',                       'parent',  None),
            ('separatorwidth',               0,         Pmw.INITOPT),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        Pmw.MegaToplevel.__init__(self, parent)

        # Create the components.

        oldInterior = Pmw.MegaToplevel.interior(self)

        # Set up pack options according to the position of the button box.
        pos = self['buttonboxpos']
        if pos not in 'nsew':
            raise ValueError('bad buttonboxpos option "%s":  should be n, s, e, or w' \
                % pos)

        if pos in 'ns':
            orient = 'horizontal'
            fill = 'x'
            if pos == 'n':
                side = 'top'
            else:
                side = 'bottom'
        else:
            orient = 'vertical'
            fill = 'y'
            if pos == 'w':
                side = 'left'
            else:
                side = 'right'

        # Create the button box.
        self._buttonBox = self.createcomponent('buttonbox',
            (), None,
            ButtonBox, (oldInterior,), orient = orient,bl=self['buttonlength'])
        self._buttonBox.pack(side = side, fill = fill)

        # Create the separating line.
        width = self['separatorwidth']
        if width > 0:
            self._separator = self.createcomponent('separator',
                (), None,
                tkinter.Frame, (oldInterior,), relief = 'sunken',
                height = width, width = width, borderwidth = width / 2)
            self._separator.pack(side = side, fill = fill)
        
        # Create the child site.
        self.__dialogChildSite = self.createcomponent('dialogchildsite',
            (), None,
            tkinter.Frame, (oldInterior,))
        self.__dialogChildSite.pack(side=side, fill='both', expand=1)

        self.oldButtons = ()
        self.oldDefault = None

        self.bind('<Return>', self._invokeDefault)
        self.userdeletefunc(self._doCommand)
        self.usermodaldeletefunc(self._doCommand)
        
        # Check keywords and initialise options.
        self.initialiseoptions()

    def interior(self):
        return self.__dialogChildSite

    def invoke(self, index = Pmw.DEFAULT):
        return self._buttonBox.invoke(index)

    def _invokeDefault(self, event):
        try:
            self._buttonBox.index(Pmw.DEFAULT)
        except ValueError:
            return
        self._buttonBox.invoke()

    def _doCommand(self, name = None):
        if name is not None and self.active() and \
                Pmw.grabstacktopwindow() != self.component('hull'):
            # This is a modal dialog but is not on the top of the grab
            # stack (ie:  should not have the grab), so ignore this
            # event.  This seems to be a bug in Tk and may occur in
            # nested modal dialogs.
            #
            # An example is the PromptDialog demonstration.  To
            # trigger the problem, start the demo, then move the mouse
            # to the main window, hit <TAB> and then <TAB> again.  The
            # highlight border of the "Show prompt dialog" button
            # should now be displayed.  Now hit <SPACE>, <RETURN>,
            # <RETURN> rapidly several times.  Eventually, hitting the
            # return key invokes the password dialog "OK" button even
            # though the confirm dialog is active (and therefore
            # should have the keyboard focus).  Observed under Solaris
            # 2.5.1, python 1.5.2 and Tk8.0.

            # TODO:  Give focus to the window on top of the grabstack.
            return

        command = self['command']
        if callable(command):
            return command(name)
        else:
            if self.active():
                self.deactivate(name)
            else:
                self.withdraw()

    def _buttons(self):
        buttons = self['buttons']
        if type(buttons) != tuple and type(buttons) != list:
            raise ValueError('bad buttons option "%s": should be a tuple' % str(buttons))
        if self.oldButtons == buttons:
          return

        self.oldButtons = buttons

        for index in range(self._buttonBox.numbuttons()):
            self._buttonBox.delete(0)
        for name in buttons:
            self._buttonBox.add(name, command=lambda self=self, name=name: self._doCommand(name))

        if len(buttons) > 0:
            defaultbutton = self['defaultbutton']
            if defaultbutton is None:
                self._buttonBox.setdefault(None)
            else:
                try:
                    self._buttonBox.index(defaultbutton)
                except ValueError:
                    pass
                else:
                    self._buttonBox.setdefault(defaultbutton)
        self._buttonBox.alignbuttons()

    def _defaultButton(self):
        defaultbutton = self['defaultbutton']
        if self.oldDefault == defaultbutton:
          return

        self.oldDefault = defaultbutton

        if len(self['buttons']) > 0:
            if defaultbutton is None:
                self._buttonBox.setdefault(None)
            else:
                try:
                    self._buttonBox.index(defaultbutton)
                except ValueError:
                    pass
                else:
                    self._buttonBox.setdefault(defaultbutton)


######################################################################
### File: PmwButtonBox.py
# Based on iwidgets2.2.0/buttonbox.itk code.


class ButtonBox(Pmw.MegaWidget):
    def __init__(self, parent = None, **kw):

        # Define the megawidget options.
        
        optiondefs = (
            ('labelmargin',       0,              Pmw.INITOPT),
            ('labelpos',          None,           Pmw.INITOPT),
            ('orient',            'horizontal',   Pmw.INITOPT),
            ('padx',              3,              Pmw.INITOPT),
            ('pady',              3,              Pmw.INITOPT),
              ('bl',                5,              Pmw.INITOPT),
        )
        self.defineoptions(kw, optiondefs, dynamicGroups = ('Button',))

        # Initialise the base class (after defining the options).
        Pmw.MegaWidget.__init__(self, parent)

        # Create the components.
        interior = self.interior()
        if self['labelpos'] is None:
            self._buttonBoxFrame = self._hull
            columnOrRow = 0
        else:
            self._buttonBoxFrame = self.createcomponent('frame',
                (), None,
                tkinter.Frame, (interior,))
            self._buttonBoxFrame.grid(column=2, row=2, sticky='nsew')
            columnOrRow = 2

            self.createlabel(interior)

        orient = self['orient']
        if orient == 'horizontal':
            interior.grid_columnconfigure(columnOrRow, weight = 1)
        elif orient == 'vertical':
            interior.grid_rowconfigure(columnOrRow, weight = 1)
        else:
            raise ValueError('bad orient option ' + repr(orient) + \
            ': must be either \'horizontal\' or \'vertical\'')

        # Initialise instance variables.

        # List of tuples describing the buttons:
        #   - name
        #   - button widget
        self._buttonList = []

        # The index of the default button.
        self._defaultButton = None

        self._timerId = None

        # Check keywords and initialise options.
        self.initialiseoptions()

    def destroy(self):
        if self._timerId:
            self.after_cancel(self._timerId)
            self._timerId = None
        Pmw.MegaWidget.destroy(self)

    def numbuttons(self):
        return len(self._buttonList)

    def index(self, index, forInsert = 0):
        listLength = len(self._buttonList)
        if type(index) == int:
            if forInsert and index <= listLength:
                return index
            elif not forInsert and index < listLength:
                return index
            else:
                raise ValueError('index "%s" is out of range' % index)
        elif index is Pmw.END:
            if forInsert:
                return listLength
            elif listLength > 0:
                return listLength - 1
            else:
                raise ValueError('ButtonBox has no buttons')
        elif index is Pmw.DEFAULT:
            if self._defaultButton is not None:
                return self._defaultButton
            raise ValueError('ButtonBox has no default')
        else:
            names = [t[0] for t in self._buttonList]
            if index in names:
                return names.index(index)
            validValues = 'a name, a number, Pmw.END or Pmw.DEFAULT'
            raise ValueError('bad index "%s": must be %s' % (index, validValues))

    def insert(self, componentName, beforeComponent = 0, **kw):
        if componentName in self.components():
            raise ValueError('button "%s" already exists' % componentName)
        if 'text' not in kw:
            kw['text'] = componentName
            kw['default'] = 'normal'
        button = self.createcomponent(*(componentName,
            (), 'Button',
            tkinter.Button, (self._buttonBoxFrame,)), **kw)

        indexInit = self.index(beforeComponent, 1)
        horizontal = self['orient'] == 'horizontal'
        #print("\indexInit: ", indexInit, "\n")

        index = indexInit % self['bl']; indrowcol = indexInit / self['bl']; numButtons = len(self._buttonList)
          
          # Shift buttons up one position.
        for i in range(numButtons - 1, indexInit - 1, -1):
            widget = self._buttonList[i][1]
            pos = i * 2 + 3
            if horizontal:
                widget.grid(column = pos, row = 0)
            else:
                widget.grid(column = 0, row = pos)
        #print("\nindrowcol: ", indrowcol, "\n")
        # Display the new button.
        if horizontal:
            button.grid(column = index * 2 + 1, row = int(indrowcol), sticky = 'ew',padx = self['padx'], pady = self['pady'])
            self._buttonBoxFrame.grid_columnconfigure(numButtons * 2 + 2, weight = 1)
        else:
            button.grid(column = indrowcol, row = index * 2 + 1, sticky = 'ew', padx = self['padx'], pady = self['pady'])
            self._buttonBoxFrame.grid_rowconfigure(numButtons * 2 + 2, weight = 1)
        self._buttonList.insert(index, (componentName, button))

        return button

    def add(self, componentName, **kw):
        return self.insert(*(componentName, len(self._buttonList)), **kw)

    def delete(self, index):
        index = self.index(index)
        (name, widget) = self._buttonList[index]
        widget.grid_forget()
        self.destroycomponent(name)

        numButtons = len(self._buttonList)

        # Shift buttons down one position.
        horizontal = self['orient'] == 'horizontal'
        for i in range(index + 1, numButtons):
            widget = self._buttonList[i][1]
            pos = i * 2 - 1
            if horizontal:
                widget.grid(column = pos, row = 0)
            else:
                widget.grid(column = 0, row = pos)

        if horizontal:
            self._buttonBoxFrame.grid_columnconfigure(numButtons * 2 - 1,
                minsize = 0)
            self._buttonBoxFrame.grid_columnconfigure(numButtons * 2, weight = 0)
        else:
            self._buttonBoxFrame.grid_rowconfigure(numButtons * 2, weight = 0)
        del self._buttonList[index]

    def setdefault(self, index):
        # Turn off the default ring around the current default button.
        if self._defaultButton is not None:
            button = self._buttonList[self._defaultButton][1]
            button.configure(default = 'normal')
            self._defaultButton = None

        # Turn on the default ring around the new default button.
        if index is not None:
            index = self.index(index)
            self._defaultButton = index
            button = self._buttonList[index][1]
            button.configure(default = 'active')

    def invoke(self, index = Pmw.DEFAULT, noFlash = 0):
        # Invoke the callback associated with the *index* button.  If
        # *noFlash* is not set, flash the button to indicate to the
        # user that something happened.

        button = self._buttonList[self.index(index)][1]
        if not noFlash:
            state = button.cget('state')
            relief = button.cget('relief')
            button.configure(state = 'active', relief = 'sunken')
            self.update_idletasks()
            self.after(100)
            button.configure(state = state, relief = relief)
        return button.invoke()

    def button(self, buttonIndex):
        return self._buttonList[self.index(buttonIndex)][1]

    def alignbuttons(self, when = 'later'):
        if when == 'later':
            if not self._timerId:
                self._timerId = self.after_idle(self.alignbuttons, 'now')
            return
        self.update_idletasks()
        self._timerId = None

        # Determine the width of the maximum length button.
        max = 0
        horizontal = (self['orient'] == 'horizontal')
        for index in range(len(self._buttonList)):
            gridIndex = index * 2 + 1
            if horizontal:
                width = self._buttonBoxFrame.grid_bbox(gridIndex, 0)[2]
            else:
                width = self._buttonBoxFrame.grid_bbox(0, gridIndex)[2]
            if width > max:
                max = width

        # Set the width of all the buttons to be the same.
        if len(self._buttonList)>self['bl']:
            colmax=self['bl']
        else:
            colmax=len(self._buttonList)   
        if horizontal:
            for index in range(colmax):
                self._buttonBoxFrame.grid_columnconfigure(index * 2 + 1,
                minsize = max)
        else:
            self._buttonBoxFrame.grid_columnconfigure(0, minsize = max)


######################################################################
### File: PmwSelectionDialog.py
# Not Based on iwidgets version.


class SelectionDialog(Dialog):
    # Dialog window with selection list.
    
    # Dialog window displaying a list and requesting the user to
    # select one.

    def __init__(self, parent = None, **kw):
        # Define the megawidget options.
        
        optiondefs = (
            ('borderx',     10,    Pmw.INITOPT),
            ('bordery',     10,    Pmw.INITOPT),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        Dialog.__init__(self, parent)

        # Create the components.
        interior = self.interior()
        aliases = (
            ('listbox', 'scrolledlist_listbox'),
            ('label', 'scrolledlist_label'),
        )
        self._list = self.createcomponent('scrolledlist',
            aliases, None,
            Pmw.ScrolledListBox, (interior,),
            dblclickcommand = self.invoke)
        self._list.pack(side='top', expand='true', fill='both',
            padx = self['borderx'], pady = self['bordery'])

        if 'activatecommand' not in kw:
            # Whenever this dialog is activated, set the focus to the
            # ScrolledListBox's listbox widget.
            listbox = self.component('listbox')
            self.configure(activatecommand = listbox.focus_set)

        # Check keywords and initialise options.
        self.initialiseoptions()

        # Need to explicitly forward this to override the stupid
        # (grid_)size method inherited from Tkinter.Toplevel.Grid.
    def size(self):
        return self.component('listbox').size()

    # Need to explicitly forward this to override the stupid
    # (grid_)bbox method inherited from Tkinter.Toplevel.Grid.
    def bbox(self, index):
        return self.component('listbox').size(index)


######################################################################
### File: PmwSelectionDialog.py
# Not Based on iwidgets version.


class SelectionBonusDialog(Dialog):
    # Dialog window with selection list.

    # Dialog window displaying a list and requesting the user to
    # select one.

    def __init__(self, parent=None, **kw):
        # Define the megawidget options.

        optiondefs = (
            ('borderx', 10, Pmw.INITOPT),
            ('bordery', 10, Pmw.INITOPT),
        )
        self.defineoptions(kw, optiondefs)

        # Initialise the base class (after defining the options).
        Dialog.__init__(self, parent)

        # Create the components.
        interior = self.interior()
        aliases = (
            ('listbox', 'scrolledlist_listbox'),
            ('label', 'scrolledlist_label'),
        )
        self._list = self.createcomponent('scrolledlist',
                                          aliases, None,
                                          Pmw.ScrolledListBox, (interior,),
                                          dblclickcommand=self.invoke)
        self._list.pack(side='top', expand='true', fill='both',
                        padx=self['borderx'], pady=self['bordery'])
        self._radio = self.createcomponent('radioselect',
                                           aliases, None,
                                           Pmw.RadioSelect, (interior,))
        self._radio.pack(side='top', expand='true', fill='both',
                        padx=self['borderx'], pady=self['bordery'])

        if 'activatecommand' not in kw:
            # Whenever this dialog is activated, set the focus to the
            # ScrolledListBox's listbox widget.
            listbox = self.component('listbox')
            self.configure(activatecommand=listbox.focus_set)

        # Check keywords and initialise options.
        self.initialiseoptions()

    # Need to explicitly forward this to override the stupid
    # (grid_)size method inherited from Tkinter.Toplevel.Grid.
    def size(self):
        return self.component('listbox').size()

    # Need to explicitly forward this to override the stupid
    # (grid_)bbox method inherited from Tkinter.Toplevel.Grid.
    def bbox(self, index):
        return self.component('listbox').size(index)


#Pmw.forwardmethods(SelectionDialog, SelectionBonusDialog, Pmw.ScrolledListBox, '_list')

