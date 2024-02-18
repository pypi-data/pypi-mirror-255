from tkinter import filedialog as _filedialog
import tkinter as _tk
from typing import Callable as _Callable
from simpleworkspace import assets as _assets
from enum import Enum as _Enum

class _TK_BaseDialog():
    __DEBUG__ = False
    _style_colors_background = "#e8edf0"
    _style_colors_foreground = "black"
    _style_colors_button_foreground = _style_colors_foreground
    _style_colors_button_background = "#dcdcdc"
    _style_fonts_helvetica_9 = "Helvetica 9"
    _style_fonts_helvetica_10 = "Helvetica 10"
    _style_fonts_paragraph = _style_fonts_helvetica_10
    _style_fonts_button = _style_fonts_helvetica_9

    def __init__(self):
        self._state_AppDestroyed = False
        self.settings_Window_TopMost = False
        self.settings_Window_Title:str = None
        self.settings_Window_Icon:str = None
        '''Specifies path to an image that will be used in window + taskbar icon'''
        self.root = _tk.Tk()

    def _Application_Mapper(self):
        if self.settings_Window_TopMost:
            self.root.wm_attributes("-topmost", 1)
        if self.settings_Window_Title:
            self.root.title(self.settings_Window_Title)
        if self.settings_Window_Icon:
            icon = _tk.PhotoImage(file=self.settings_Window_Icon, master=self.root)
            self.root.iconphoto(False, icon)
        self.root.configure(background=self._style_colors_background)

        def OnDestroyed_Window(event:_tk.Event):
            self._state_AppDestroyed = True
        self.root.bind("<Destroy>", OnDestroyed_Window)  # it might get destroyed by tk itself when closing from taskbar etc
        
        # add default behavior of invoking focused button with the enter key aswell (spacebar is already configured by default)
        self.root.bind_class("Button", "<Key-Return>", lambda event: event.widget.invoke())

    def _Application_Run(self):
        self._Application_Mapper()
        self._CenterWindow()
        if(self.__DEBUG__):
            self.__InitDebugMode__()
        self.root.mainloop()

    def _CenterWindow(self):
        self.root.withdraw() # Remain invisible while we figure out the geometry
        self.root.update_idletasks() # Actualize geometry information

        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"+{x}+{y}")

        self.root.deiconify() # Become visible at the desired location

    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        if not self._state_AppDestroyed:
            self.root.destroy()

    def __InitDebugMode__(self):
        queue = [self.root]
        while(len(queue) > 0):
            widget = queue.pop(0)
            widget.configure(highlightthickness=1, highlightbackground='blue')
            queue.extend(widget.winfo_children())

    def _AddEventHandler_OnLoad(self, widget: _tk.Widget, callback: _Callable[[_tk.Event], None]):
        def WrappedCallback(*args):
            callback(*args)
            widget.unbind('<Map>', eventId)

        eventId = widget.bind('<Map>', WrappedCallback, add='+')

class _TK_BaseMessageBox(_TK_BaseDialog):
    def __init__(self):
        super().__init__()
        self.settings_Message:str = None
        self.settings_Window_Title = "Information"
        self.settings_Window_Icon = _assets.Icons_InfoCircle_PNG

        self.settings_Message_MaxLinesUntilScroll = 7
        self._style_Header_Expand = True
        self._style_Footer_Expand = False

    def _Application_Mapper(self):
        super()._Application_Mapper()

        frame_header = _tk.Frame(self.root, bg=self._style_colors_background)
        self._FrameHeader_Mapper(frame_header)
        if(self._style_Header_Expand):
            frame_header.pack(fill=_tk.BOTH, expand=True, padx=10)
        else:
            frame_header.pack(fill=_tk.X, padx=10)

        frame_belowMessage = _tk.Frame(self.root, bg=self._style_colors_background)
        self._FrameFooter_Mapper(frame_belowMessage)
        if(self._style_Footer_Expand):
            frame_belowMessage.pack(side=_tk.BOTTOM, fill=_tk.BOTH, expand=True, padx=10)
        else:
            frame_belowMessage.pack(side=_tk.BOTTOM, fill=_tk.X, padx=10)

    def _FrameHeader_Mapper(self, frame: _tk.Frame):
        if not self.settings_Message: #if empty message skip rendering
            return
        
        textbox_frame = _tk.Frame(frame, bg=self._style_colors_background) #to later support scrollbar
        textbox = _tk.Text(
            textbox_frame,
            borderwidth=0,
            height=4,
            width=60,
            wrap=_tk.WORD,
            bg=self._style_colors_background,
            fg=self._style_colors_foreground,
            font=self._style_fonts_paragraph,
        )
    
        def OnLoad_Textbox(event: _tk.Event):
            widget: _tk.Text = event.widget

            widget.tag_configure("center", justify="center")
            widget.insert(_tk.INSERT, self.settings_Message, "center")

            displayLines = widget.count("1.0", "end", "displaylines")[0]
            if displayLines > self.settings_Message_MaxLinesUntilScroll:
                displayLines = self.settings_Message_MaxLinesUntilScroll
                scrollbar = _tk.Scrollbar(widget.master)
                scrollbar.pack(side=_tk.RIGHT, fill=_tk.Y)
                widget.configure(yscrollcommand=scrollbar.set)

            widget.configure(height=displayLines, state=_tk.DISABLED)
            return

        self._AddEventHandler_OnLoad(textbox, OnLoad_Textbox)
        textbox.pack(side=_tk.LEFT, fill=_tk.BOTH, expand=True)
        textbox_frame.pack(fill=_tk.BOTH, expand=True, pady=10)

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        ok_button = _tk.Button(
            frame,
            text="OK",
            font=self._style_fonts_button,
            bg=self._style_colors_button_background,
            fg=self._style_colors_button_foreground,
            padx=35,
            pady=2,
            command=self.root.destroy,
        )
        ok_button.pack(side=_tk.BOTTOM, pady=(5, 10))
        self._AddEventHandler_OnLoad(ok_button, lambda event: event.widget.focus())

    @classmethod
    def Show(cls, message: str, windowTitle: str = None, windowTopMost:bool=None):
        with cls() as app:
            app.settings_Message = message
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            app._Application_Run()

class MessageBox(_TK_BaseMessageBox):
    class TypeEnum(_Enum):
        Information = 2
        Warning = 3
        Error = 4

        def GetIconPath(self):
            if(self == self.Information):
                return _assets.Icons_InfoCircle_PNG
            elif(self == self.Warning):
                return _assets.Icons_WarningCircle_PNG
            elif(self == self.Error):
                return _assets.Icons_ErrorCircle_PNG
            return None
        
    @classmethod
    def Show(cls, message: str, messageType:'MessageBox.TypeEnum' = None, windowTitle: str = None, windowTopMost:bool=None):
        with cls() as app:
            app.settings_Message = message
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            if(messageType is not None):
                app.settings_Window_Title = messageType.name
                app.settings_Window_Icon = messageType.GetIconPath()
            app._Application_Run()

class RichMessageBox(MessageBox):
    def __init__(self):
        super().__init__()
        self._style_Header_Expand = False
        self._style_Footer_Expand = True #make the large text box rescalable instead with the window
        self.settings_RichText:str = None

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        super()._FrameFooter_Mapper(frame) #add ok button
        if not self.settings_RichText: #if empty rich message skip rendering
            return
        
        textbox_frame = _tk.Frame(frame, bg=self._style_colors_background) #to support scrollbar
        xScrollbar = _tk.Scrollbar(textbox_frame, orient=_tk.HORIZONTAL) 
        yScrollbar = _tk.Scrollbar(textbox_frame, orient=_tk.VERTICAL)
        textbox = _tk.Text(
            textbox_frame,
            font=self._style_fonts_paragraph,
            xscrollcommand=xScrollbar.set,
            yscrollcommand=yScrollbar.set,
            wrap=_tk.NONE
        )
    
        def OnLoad_Textbox(event: _tk.Event):
            widget: _tk.Text = event.widget
            widget.insert(_tk.INSERT, self.settings_RichText)
            widget.configure(state=_tk.DISABLED)

        self._AddEventHandler_OnLoad(textbox, OnLoad_Textbox)
        xScrollbar.pack(side=_tk.BOTTOM, fill=_tk.X)
        yScrollbar.pack(side=_tk.RIGHT, fill=_tk.Y)
        textbox.pack(side=_tk.LEFT, fill=_tk.BOTH, expand=True)
        textbox_frame.pack(fill=_tk.BOTH, expand=True, pady=5)
    

    @classmethod
    def Show(cls, text:str, description: str = None, messageType:'MessageBox.TypeEnum' = None, windowTitle: str = None, windowTopMost:bool=None):
        '''
        a large message box with scrollbars and wordwrapping turned off.

        :param description: A small description at header section
        :param text: A large and rich textbox at footer section
        '''
        with cls() as app:
            app.settings_Message = description
            app.settings_RichText = text
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            if(messageType is not None):
                app.settings_Window_Title = messageType.name
                app.settings_Window_Icon = messageType.GetIconPath()
            app._Application_Run()

class ConfirmationBox(_TK_BaseMessageBox):
    def __init__(self):
        super().__init__()
        self.settings_Window_Title = "Confirmation Dialog"
        self.settings_Window_Icon = _assets.Icons_QuestionCircle_PNG
        self.dialogResult = False
        """defaults to false, is only true if yes button is pressed"""

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        def OnClick_AnswerBtn(answer: bool):
            self.dialogResult = answer
            self.root.destroy()

        yes_button = _tk.Button(
            frame,
            text="Yes",
            font=self._style_fonts_button,
            bg=self._style_colors_button_background,
            fg=self._style_colors_button_foreground,
            padx=35,
            pady=2,
            command=lambda: OnClick_AnswerBtn(True),
        )
        no_button = _tk.Button(
            frame,
            text="No",
            font=self._style_fonts_button,
            bg=self._style_colors_button_background,
            fg=self._style_colors_button_foreground,
            padx=35,
            pady=2,
            command=lambda: OnClick_AnswerBtn(False),
        )

        no_button.pack(side=_tk.LEFT, anchor=_tk.SE, expand=True, pady=(5, 10), padx=5)
        yes_button.pack(side=_tk.RIGHT, anchor=_tk.SW, expand=True, pady=(5, 10), padx=5)

    @classmethod
    def Show(cls, message: str, windowTitle: str = None, windowTopMost:bool=None):
        '''Displays a messagebox containing a question with a yes or no button'''
        with cls() as app:
            app.settings_Message = message
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            app._Application_Run()
            return app.dialogResult

class InputBox(_TK_BaseMessageBox):
    def __init__(self):
        super().__init__()
        self.settings_Window_Title = "Input Dialog"
        self.settings_Window_Icon = _assets.Icons_QuestionCircle_PNG
        self.settings_InitialValue = ''
        self.dialogResult: None | str = None

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        textBox = _tk.Entry(
            frame,
            font=self._style_fonts_paragraph
        )

        def OnLoad_Textbox(event: _tk.Event):
            widget:_tk.Text = event.widget
            if self.settings_InitialValue:
                widget.insert(_tk.INSERT, self.settings_InitialValue)
            widget.focus()
        
        def OnClick_BtnOk():
            self.dialogResult = textBox.get()
            self.root.destroy()

        btn_ok = _tk.Button(
            frame,
            text="OK",
            font=self._style_fonts_helvetica_9,
            bg=self._style_colors_button_background,
            fg=self._style_colors_button_foreground,
            padx=35,
            pady=2,
            command=OnClick_BtnOk
        )

        textBox.pack(side=_tk.LEFT, anchor=_tk.S, fill=_tk.X, expand=True, pady=(5, 14))
        btn_ok.pack(side=_tk.RIGHT, anchor=_tk.S, pady=(5, 10), padx=(5,0))
        self._AddEventHandler_OnLoad(textBox, OnLoad_Textbox)
        textBox.bind("<Return>", lambda event: btn_ok.invoke())

    @classmethod
    def Show(cls, message: str, initialValue:str = None, windowTitle: str = None, windowTopMost:bool=None):
        '''
        Asks user for a string input
        :param initalValue: A preentered default input text visible to user when prompt is displayed
        :returns: the input string, if window is closed then None
        '''
        with cls() as app:
            app.settings_Message = message
            app.settings_InitialValue = initialValue
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            app._Application_Run()
            return app.dialogResult

class RichInputBox(InputBox):
    '''A large multiline input box with scrollbars'''
    def __init__(self):
        super().__init__()
        self._style_Header_Expand = False
        self._style_Footer_Expand = True #make the large input box rescalable instead with the window

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        textbox_frame = _tk.Frame(frame, bg=self._style_colors_background) #to support scrollbar
        xScrollbar = _tk.Scrollbar(textbox_frame, orient=_tk.HORIZONTAL) 
        yScrollbar = _tk.Scrollbar(textbox_frame, orient=_tk.VERTICAL)
        textBox = _tk.Text(
            textbox_frame,
            font=self._style_fonts_paragraph,
            xscrollcommand=xScrollbar.set,
            yscrollcommand=yScrollbar.set,
            wrap=_tk.NONE
        )

        xScrollbar.pack(side=_tk.BOTTOM, fill=_tk.X)
        yScrollbar.pack(side=_tk.RIGHT, fill=_tk.Y)
        textBox.pack(side=_tk.LEFT, fill=_tk.BOTH, expand=True)
        textbox_frame.pack(fill=_tk.BOTH, expand=True, pady=5)

        def OnLoad_Textbox(event: _tk.Event):
            widget:_tk.Text = event.widget
            if self.settings_InitialValue:
                widget.insert(_tk.INSERT, self.settings_InitialValue)
            widget.focus()

        def OnClick_BtnOk():
            self.dialogResult = textBox.get("1.0",'end-1c')
            self.root.destroy()

        btn_ok = _tk.Button(
            frame,
            text="OK",
            font=self._style_fonts_helvetica_9,
            bg=self._style_colors_button_background,
            fg=self._style_colors_button_foreground,
            padx=35,
            pady=2,
            command=OnClick_BtnOk,
        )

        btn_ok.pack(side=_tk.BOTTOM,pady=(5, 10), padx=(5,0))
        self._AddEventHandler_OnLoad(textBox, OnLoad_Textbox)

class ButtonBox(_TK_BaseMessageBox):
    def __init__(self, buttons: list[str]):
        super().__init__()
        self.settings_Buttons = buttons

        self.settings_Window_Title = "Menu"
        self.settings_Window_Icon = None

        self.style_Grid_MaxItemsPerRow = 4
        self._style_Header_Expand = False
        self._style_Footer_Expand = True #make the button panel rescalable instead with the window

        self.dialogResult = None

    def _FrameFooter_Mapper(self, frame: _tk.Frame):
        subFrame = _tk.Frame(frame, bg=self._style_colors_background)
        subFrame.rowconfigure(0, weight=1)
        row, col = 0, 0
        for btnName in self.settings_Buttons:
            def OnClick_Btn(btnName=btnName): #capture current instance of btnOptions
                self.dialogResult = btnName
                self.root.destroy()
            btn = _tk.Button(
                subFrame,
                text=btnName,
                font=self._style_fonts_button,
                bg=self._style_colors_button_background,
                fg=self._style_colors_button_foreground,
                padx=25,
                pady=10,
                command=OnClick_Btn
            )
            btn.grid(row=row, column=col, pady=5, padx=5)
            
            subFrame.columnconfigure(col, weight=1)
            col += 1
            if(col % self.style_Grid_MaxItemsPerRow == 0):
                col = 0
                row += 1
                subFrame.rowconfigure(row, weight=1)
        subFrame.pack(fill=_tk.BOTH,expand=True, pady=10)

    @classmethod
    def Show(cls, buttons: list[str], message: str = None, windowTitle: str = None, windowTopMost:bool=None):
        '''
        Shows a box with freely specified buttons
        :param buttons: list of button names
        :returns: the name of the button that was pressed, None if window closed
        '''
        with cls(buttons) as app:
            app.settings_Message = message
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(windowTitle is not None):
                app.settings_Window_Title = windowTitle
            app._Application_Run()
            return app.dialogResult
        
#only reason to use parent as custom tkdialog is to add icon to taskbar and being able to set topmost attribute
class FileDialog:
    @staticmethod
    def Show(multiple=False, initialDir:str=None, windowTitle:str=None, windowTopMost:bool=None):
        with _TK_BaseDialog() as app:
            app.root.attributes('-alpha', 0.0)  #makes the root windows invisible if it were to be reopened
            app.root.iconify()                  #minimizes the root windows
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            if(multiple):
                res = tuple(_filedialog.askopenfilenames(initialdir=initialDir, title=windowTitle, parent=app.root))
            else:
                res = _filedialog.askopenfilename(initialdir=initialDir, title=windowTitle, parent=app.root)
            return res if res != '' else None

class DirectoryDialog:
    @staticmethod
    def Show(initialDir:str=None, windowTitle:str=None, windowTopMost:bool=None):
        with _TK_BaseDialog() as app:
            app.root.attributes('-alpha', 0.0)  #makes the root windows invisible if it were to be reopened
            app.root.iconify()                  #minimizes the root windows
            if(windowTopMost is not None):
                app.settings_Window_TopMost = windowTopMost
            res = _filedialog.askdirectory(initialdir=initialDir, title=windowTitle, parent=app.root)
            return res if res != '' else None
