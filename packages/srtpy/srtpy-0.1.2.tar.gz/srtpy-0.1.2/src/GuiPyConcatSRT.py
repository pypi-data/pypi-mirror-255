# -*- coding: utf-8 -*-
"""
GUI PyConcatSrt
"""


import tkinter as tk
from tkinter import ttk, Tk
from tkinter import filedialog, messagebox

import webbrowser

from src.SrtPyMain import SrtPy


class Repo(object):
    repo = 'https://github.com/kurotom/PyConcatSrt.git'


class Colors(object):
    """
    Set colors for frame background, background and foreground.
    """
    frame_bg = 'white'
    fg = 'black'
    bg = 'white'


class CustomLabel(ttk.Label):
    """
    Custom Label
    """
    def __init__(
                    self,
                    frame: ttk.Frame,
                    text: str,
                    justify: str,
                    anchor: str = None,
                    *args,
                    **kwargs
                ):
        kwargs['foreground'] = Colors.fg
        kwargs['background'] = Colors.bg
        if anchor is not None:
            kwargs['anchor'] = 'center'
        else:
            kwargs['anchor'] = 'w'
        kwargs['text'] = text
        kwargs['justify'] = justify
        super().__init__(frame, *args, **kwargs)


class InnerFrame(ttk.Frame):
    """
    Custom Frame
    """
    def __init__(
                    self,
                    parent: ttk.Frame,
                    name: str,
                    color: str = None,
                    border: bool = None,
                    *args,
                    **kwargs
                ):
        style1 = ttk.Style()
        if color is not None:
            style1.configure('frame_help.TFrame', background=color)
        else:
            style1.configure('frame_help.TFrame', background=Colors.bg)
        kwargs['style'] = 'frame_help.TFrame'

        kwargs['name'] = name
        kwargs['relief'] = ''
        if border is not None:
            kwargs['relief'] = 'solid'
            kwargs['borderwidth'] = 1
        super().__init__(parent, *args, **kwargs)


class Gui(object):

    filename = 'final.srt'

    def __init__(self, main: Tk, debug: bool = False) -> None:
        """
        Constructor
        """
        self.debug = debug
        self.main = main
        self.control = SrtPy()

        self.main.geometry('300x300')

        self.main.title('PyConcatSrt')

        self.frame = InnerFrame(self.main, name='frame_main', border=None)

        self.label_entry = CustomLabel(self.main, text='Name', justify=None)

        s = ttk.Style()
        s.configure('entry_filename.TEntry', padding='10 1 0 0')
        self.entry_filename = ttk.Entry(
                                    self.main,
                                    name='entry_filename',
                                    style='entry_filename.TEntry',
                                    font=("Calibri", 13, "italic")
                                )
        self.entry_filename.insert(0, Gui.filename)

        s1 = ttk.Style()
        s1.configure(
            'check_back.TCheckbutton',
            background='white',
            activebackground='white'
        )
        self.commitedOperation = tk.BooleanVar()
        self.commitedOperation.set(True)
        self.checkLog = ttk.Checkbutton(
                                self.frame,
                                name='check_log',
                                cursor='hand2',
                                text='Errors log',
                                style='check_back.TCheckbutton',
                                variable=self.commitedOperation
                            )

        self.button = ttk.Button(
                            self.frame,
                            command=self.convert_start,
                            text='Convert'
                        )

        self.frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.label_entry.place(x=15, y=50, relwidth=1, height=30)
        self.entry_filename.place(x=80, y=50, width=200, height=30)

        self.checkLog.place(x=200, y=90)

        self.button.place(x=100, y=190, width=100, height=30)

        self.menu_bar = MenuBar(self.main, self.control)

        self.main.bind('<Control-o>', self.menu_bar.openfile)
        self.main.bind('<Control-d>', self.menu_bar.opendir)
        self.main.bind('<Control-s>', self.convert_start)
        self.main.bind('<Escape>', self.menu_bar.close_destroy)

    def convert_start(self, event=None):
        """
        Event button and bind start converter files SRT
        """
        if self.menu_bar.files is not None or self.menu_bar.dir is not None:
            file_name = self.entry_filename.get()
            data = self.control.read(paths=self.menu_bar.files)
            data_formatted = self.control.convertData(data)
            finish = self.control.to_write(
                            filename=file_name,
                            data=data_formatted
                        )
            if finish:
                messagebox.showinfo(
                    title='Operation finished',
                    message='The operation has been completed successfully.'
                )
            if self.commitedOperation.get():
                self.control.write_log()
        else:
            messagebox.showinfo(
                title='Select Files/Directory',
                message='You must first select file/s or directory.'
            )


class MenuBar(Gui):
    """
    Class of Menu
    """

    def __init__(self, frame, controller):
        """
        Constructor
        """
        self.controller = controller
        self.frame = frame
        self.menu = None
        self.files = None
        self.dir = None
        self.current = []
        self.drawMenu()

    def drawMenu(self):
        """
        Build menu items.
        """
        file_label = 'Open files'
        dir_label = 'Open directory'

        self.menu = tk.Menu()
        self.frame.config(menu=self.menu)

        openFiles = tk.Menu(self.menu, tearoff=0)
        openFiles.add_command(label=file_label, command=self.openfile)
        openFiles.add_command(label=dir_label, command=self.opendir)
        openFiles.add_separator()

        helpMenu = tk.Menu(self.menu, tearoff=0)
        helpMenu.add_command(label='Combo keys', command=self.showHelp)
        helpMenu.add_separator()
        helpMenu.add_command(label='About', command=self.showAbout)

        self.menu.add_cascade(label='File', menu=openFiles)
        self.menu.add_cascade(label='Help', menu=helpMenu)

    def openfile(self, event=None):
        """
        Event to open SRT files.
        """
        self.files = filedialog.askopenfiles(
                    filetypes=[("Files SRT", "*.srt")]
                )

    def opendir(self, event=None):
        """
        Event to open directory with SRT files.
        """
        self.dir = filedialog.askdirectory()

    def showHelp(self):
        """
        Show framework help.
        """
        if self.current != []:
            self.close_destroy()
            self.current = []

        frame = InnerFrame(self.frame, name='frame_help', border=True)
        cancel = tk.Button(
                        text='Accept',
                        command=self.close_destroy,
                        relief='solid',
                        bg='white'
                    )

        self.current.append(frame)
        self.current.append(cancel)

        frame.place(x=0, y=0, relwidth=1, height=180)
        cancel.place(x=100, y=159, width=100, height=20)

        keys_binds = [
            ['Open files', 'Ctrl + O'],
            ['Open dir', 'Ctrl + D'],
            ['Start', 'Ctrl + S'],
            ['Close help', 'Escape'],
            ['Quit', 'Control + q'],
        ]

        y_pos = 5
        for item in keys_binds:
            a1 = CustomLabel(
                        text=item[0],
                        frame=frame,
                        justify='left',
                        anchor=None
                    )
            a2 = CustomLabel(
                        text=item[1],
                        frame=frame,
                        justify='left',
                        anchor=None
                    )
            a1.place(x=10, y=y_pos, width=80, heigh=20)
            a2.place(x=90, y=y_pos, width=80, heigh=20)
            y_pos += 30

    def showAbout(self):
        """
        Displays a frame about the application.
        """
        def msg():
            msg = 'PyConcatSrt is a tool to merge SRT files into one, '
            msg += 'respecting times with the correct format, logging errors.'
            return msg

        if self.current != []:
            self.close_destroy()
            self.current = []

        frame = InnerFrame(self.frame, name='frame_about', border=True)

        cancel = tk.Button(
                        text='Accept',
                        command=self.close_destroy,
                        relief='solid',
                        bg='white'
                    )
        self.current.append(frame)
        self.current.append(cancel)

        ltext = tk.Text(master=frame, wrap='word', cursor=None)
        ltext.insert('0.0', msg())
        ltext.config(state="disabled")
        ltext.config(highlightthickness=0, border=0)

        linkRepo = CustomLabel(
                        text="Project repository - Kurotom",
                        frame=frame,
                        justify='center',
                        font=('Arial', 13, 'bold'),
                        cursor='hand2',
                        anchor='center'
                    )

        self.label_show_link = CustomLabel(
                        text=Repo.repo,
                        frame=frame,
                        justify='center',
                        font=('Arial', 10, 'bold'),
                        anchor='center'
                    )

        linkRepo.bind('<Button-1>', self.link_repo)
        linkRepo.bind('<Enter>', self.show_link)
        linkRepo.bind('<Leave>', self.destroy_show_link)

        frame.place(x=0, y=0, relwidth=1, height=180)
        ltext.place(x=10, y=0, width=290, height=80)
        linkRepo.place(x=0, y=90, relwidth=1, height=30)
        cancel.place(x=100, y=159, width=100, height=20)

    def close_destroy(self, event=None):
        """
        Destroy the "help" and "about" frames.
        """
        if self.current is not []:
            for item in self.current:
                item.destroy()
            self.current = []

    def link_repo(self, event=None):
        """
        Open the link repository in your web browser.
        """
        webbrowser.open(Repo.repo)

    def show_link(self, event=None):
        """
        Displays a link in a label below the link repository.
        """
        self.label_show_link.place(x=0, y=120, relwidth=1, height=20)

    def destroy_show_link(self, event=None):
        """
        Hide the link repository.
        """
        self.label_show_link.place(x=0, y=0, width=0, height=0)


def main():
    """
    Constructs gui main app, and bind exit event.
    """
    root = Tk()
    gui = Gui(root)
    root.bind('<Control-q>', lambda x: root.destroy())
    root.mainloop()


if __name__ == '__main__':
    main()
