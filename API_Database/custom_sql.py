"""
==== Description ====
This class is used to acquire information to add register_entrys to the
database.

"""
from __future__ import annotations
from Main import MainMenu
import tkinter
from tkinter import *
from tkinter import messagebox
from Database import db_connector


class CustomSQL:
    """
    A class that represents the add register_entrys window

    ===Attributes===

    window: container for all objects
    options: list containing all the options

    """

    def __init__(self) -> None:
        self.window = tkinter.Tk()
        self.window.geometry("700x500")
        self.window.rowconfigure(0, weight=1)
        self.window.grid_columnconfigure(0, weight=1)
        self.window.title("Custom SQL query writer")
        self.window.bind("<Escape>", lambda event: self.back())
        # Creating the main frame
        self.main_frame = Frame(self.window)
        # Creating bottom_frame
        self.bottom_frame = Frame(self.window)

        self.show_main_window()

    def create_main_frame(self) -> None:
        # Creating bank name label
        label = Label(self.main_frame, text="Query: ")
        label.grid(column=1, row=1)

        entry = Text(self.main_frame, width=50, height=30)
        entry.focus()
        entry.grid(column=1, row=2)

        # Creating create button
        create_button = Button(self.bottom_frame, text="Create",
                               command=lambda: self.create
                               (entry.get("1.0", END)))
        create_button.bind("<Return>", lambda event: self.create(entry.get("1.0", END)))

        create_button.grid(column=0, row=0, ipadx=20)

        # Creating back button
        back_button = Button(self.bottom_frame, text="<<Back",
                             command=lambda: self.back())
        back_button.grid(column=2, row=0, padx=90, ipadx=20)

        self.main_frame.grid(column=0, row=0)
        self.bottom_frame.grid(column=0, row=1)

    def show_main_window(self) -> None:
        self.create_main_frame()
        self.window.mainloop()

    def back(self):
        self.window.destroy()
        MainMenu.execute()

    def create(self, entry: str):
        entry = entry.split("\n")

        for query in entry:
            if query != "":
                db_connector.add_stack(query)

        tkinter.messagebox.showinfo(title="Complete", message="Queries added to the stack please Update Online Database")


def execute():
    new_window = CustomSQL()
    new_window.show_main_window()
