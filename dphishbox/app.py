# -*- coding: utf-8 -*-
"""DPhishBox module"""

try:
    import tkinter as tk
except ImportError:
    import Tkinter as tk

import threading

from validators import url

from .provider import OpenPhish, PhishTank


class DPhishBox(tk.Frame):
    """
    DPhishBox application class.

    A small Tkinter GUI application to validate URLs against
    phishing black-lists.

    Components:
    1. Entry - field for input
        features:
        * Right-click - auto paste from clipborad (DPhishBox.paste_from_cb)
        * Del-key - reset entry (DPhishBox.reset_input)
        * Enter-key - handle input (see DPhishBox.input_handler)
    2. Status - application status indicator

    Buttons:
    3. Check - handle input (see DPhishBox.input_handler)
    4. Reset - reset entry (DPhishBox.reset_input
    5. Update - run provider update (see DPhishBox.update_data)

    example:
        With customization:
            from .provider import OpenPhish, PhishTank # (see provider.Provider)
            gui = tk.Tk()
            providers = [YourProvider()]
            app = DPhishBox(gui, providers=providers)
            app.pack()
            gui.mainloop()

        or simply,
            from dphishbox import app
            app.start_app()
    """

    def __init__(self, parent, providers=None, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        if providers:
            self.providers = providers
        else:
            self.providers = []

        self.config(bg='SkyBlue1', padx=5, pady=5)

        self.url_input = tk.Entry(self,
                                  bg='white',
                                  bd=0,
                                  width=50,
                                  font=('Arial', 14))
        self.url_input.bind("<Return>", self.input_handler)
        self.url_input.bind("<Delete>", self.reset_input)
        self.url_input.bind("<Button-3>", self.paste_from_cb)
        self.url_input.pack(fill=tk.X, padx=2, pady=2)

        self.status = tk.Label(self,
                               bg='SkyBlue1',
                               text='Ready',
                               font=('Arial', 12))
        self.status.pack(side=tk.LEFT, padx=2, fill=tk.X)

        self.update = tk.Button(self,
                                bd=0,
                                bg='DeepSkyBlue4',
                                fg='white',
                                text='Update',
                                font=('Arial', 9),
                                command=self.update_data)
        self.update.pack(side=tk.RIGHT, padx=2)

        self.reset = tk.Button(self,
                               bd=0,
                               bg='DeepSkyBlue4',
                               fg='white',
                               text='Clear',
                               font=('Arial', 9),
                               command=self.reset_input)
        self.reset.pack(side=tk.RIGHT, padx=2)

        self.check = tk.Button(self,
                               bg='DeepSkyBlue4',
                               fg='white',
                               text='Check',
                               font=('Arial', 9),
                               command=self.input_handler)
        self.check.pack(side=tk.RIGHT, padx=2)

        self.after(0, self.init_data)

    def init_data(self):
        """Perform provider data init"""

        self.status.config(text='Loading providers')
        self.disable_widgets()

        def _providers_load():
            task_errors = []
            for provider in self.providers:
                self.status.config(text='Loading provider {}'.format(provider.name))
                provider.load()
                task_errors.extend(provider.flush_errors())
            if task_errors:
                self.reset_input(msg='; '.join(e for e in task_errors))
            else:
                self.reset_input()
            self.enable_widgets()

        threading.Thread(target=_providers_load).start()

    def update_data(self):
        """Perform provider data update"""

        self.status.config(text='Updating providers')
        self.disable_widgets()

        def _providers_update():
            task_errors = []
            for provider in self.providers:
                self.status.config(text='Updating provider {}'.format(provider.name))
                provider.update()
                task_errors.extend(provider.flush_errors())
            if task_errors:
                self.reset_input(msg='; '.join(e for e in task_errors))
            else:
                self.reset_input()
            self.enable_widgets()

        threading.Thread(target=_providers_update).start()

    def disable_widgets(self):
        for child in self.winfo_children():
            child.config(state='disabled')

    def enable_widgets(self):
        for child in self.winfo_children():
            child.config(state='normal')

    def paste_from_cb(self, key=None):
        """Paste from clipboard on entry right-click"""

        self.reset_input()
        self.url_input.insert(0, self.clipboard_get())

    def reset_input(self, key=None, msg='Ready'):
        """Default entry appearance

        Possible status message
        """

        self.url_input.config(state='normal')
        self.url_input.delete(0, 'end')
        self.url_input.config(bg='white')
        self.status.config(text=msg)

    def input_handler(self, key=None):
        """User input handler

        Input is validated as URL. if the input is valid it's matched
        against provider/s data.

        Indications:
        entry color | status         | meaning
        ---------------------------------------------------------------
           yellow   | Invalid URL    | input is not a valid url
           red      | Phishing Alert | URL was found in provider/s data
           green    | Looks Clean    | URL was NOT found in data
        """

        input = self.url_input.get()
        if not url(input):
            self.url_input.config(bg='yellow')
            self.status.config(text='Invalid URL')
            return
        for provider in self.providers:
            if provider.has_url(input):
                self.url_input.config(bg='orange red')
                self.status.config(text='Phishing Alert')
                break
        else:
            self.url_input.config(bg='spring green')
            self.status.config(text='Looks Clean')


def start_app():
    """App initiation"""

    gui = tk.Tk()
    gui.title('DPhishBox')
    gui.geometry("-10-80")
    # providers = [OpenPhish(), PhishTank()]
    # PhishTank provider download method not
    # optimized for python2. (see provider.PhishTank)
    providers = [OpenPhish()]
    app = DPhishBox(gui, providers=providers)
    app.pack()
    gui.mainloop()
