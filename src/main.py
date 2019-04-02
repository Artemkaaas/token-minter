import tkinter as tk

from tkinter import filedialog
from tkinter import messagebox

from src.indy_helpers import *
from src.utils import INITIAL_DIR, load_plugin, load_config

LARGE_FONT = ('Verdana', 12)
MEDIUM_FONT = ('Verdana', 10)
SMALL_FONT = ('Verdana', 10)

TOP_LABEL = {'font': LARGE_FONT, 'pady': 20}


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title('Minter')
        self.geometry('300x300')

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_columnconfigure(0, weight=1)

        self.config = load_config()
        self.steps = {}
        self._show_frame(container, StartPage)

    def step(self, container):
        self._show_frame(container, self.action_steps.pop(0))

    def _build_frame(self, container, page):
        frame = page(container, self)
        frame.grid(row=0, column=0, sticky='nsew')
        return frame

    def _show_frame(self, container, page):
        frame = self._build_frame(container, page)
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)

        controller.context = {}

        tk.Label(self, text='What do you want?', cnf=TOP_LABEL).pack()

        tk.Button(self, text='Build Transaction', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller, 'BUILD')).pack(pady=20)

        tk.Button(self, text='Sign Transaction', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller, 'SIGN')).pack(pady=20)

        tk.Button(self, text='Send Transaction', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller, 'SEND')).pack(pady=20)

    def _on_click(self, container, controller, action):
        controller.action_steps = self.steps()[action]
        controller.step(container)

    def steps(self):
        return {
            'BUILD': [OpenWalletPage, BuildTransactionPage, SelectOutputFilePage, StartPage],
            'SIGN': [OpenWalletPage, SelectDidPage, SignTransactionFilePage, SelectOutputFilePage, StartPage],
            'SEND': [SendTransactionPage, StartPage],
        }


class OpenWalletPage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Open Wallet', cnf=TOP_LABEL).pack()

        tk.Label(self, text='Name', font=MEDIUM_FONT).pack(pady=(20, 2))
        self.name = tk.Entry(self)
        self.name.pack()

        tk.Label(self, text='Key', font=MEDIUM_FONT).pack(pady=(20, 2))
        self.key = tk.Entry(self)
        self.key.pack()

        tk.Button(self, text='Open', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=20)

    def _on_click(self, container, controller):
        try:
            container.master.context['wallet_handle'] = open_wallet(self.name.get(), self.key.get())
        except Exception as e:
            return messagebox.showerror("Cannot open Wallet", e)

        controller.step(container)


class SelectDidPage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Select DID', cnf=TOP_LABEL).pack()

        self.listbox = tk.Listbox(self, height=8, width=24, font=MEDIUM_FONT)
        self.listbox.pack()

        [self.listbox.insert(tk.END, did_info['did'])
         for did_info in get_stored_dids(container.master.context['wallet_handle'])]

        tk.Button(self, text='Select', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=20)

    def _on_click(self, container, controller):
        if not self.listbox.get(tk.ACTIVE):
            return messagebox.showerror("Error", "Select DID to sign")

        container.master.context['did'] = self.listbox.get(tk.ACTIVE)
        controller.step(container)


class SignTransactionFilePage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Sign Transaction', cnf=TOP_LABEL).pack()

        self.input_filename = tk.StringVar()
        tk.Button(self, text='Select Transaction file', font=MEDIUM_FONT,
                  command=lambda: self._select_input_file()).pack(pady=(20, 5))
        tk.Message(self, textvariable=self.input_filename, font=MEDIUM_FONT, width=260).pack()

        tk.Button(self, text='Sign', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=30)

    def _select_input_file(self):
        self.input_filename.set(
            filedialog.askopenfilename(initialdir=INITIAL_DIR, title="Select Transaction file"))

    def _on_click(self, container, controller):
        try:
            with open(self.input_filename.get(), "r") as input_filename:
                transaction = input_filename.read()
                container.master.context['transaction'] = sign_transaction(container.master.context['wallet_handle'],
                                                                           container.master.context['did'],
                                                                           transaction)
            close_wallet(container.master.context['wallet_handle'])
        except Exception as e:
            return messagebox.showerror("Error", e)

        controller.step(container)


class SelectOutputFilePage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Save Transaction', cnf=TOP_LABEL).pack()

        self.output_filename = tk.StringVar()
        tk.Button(self, text='Select Output file', font=MEDIUM_FONT,
                  command=lambda: self._select_output_file()).pack(pady=(20, 5))
        tk.Message(self, textvariable=self.output_filename, font=MEDIUM_FONT, width=260).pack()

        tk.Button(self, text='Save', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=30)

    def _select_output_file(self):
        self.output_filename.set(filedialog.asksaveasfilename(initialdir=INITIAL_DIR, title="Select Output File"))

    def _on_click(self, container, controller):
        try:
            with open(self.output_filename.get(), 'w+') as file:
                file.write(container.master.context['transaction'])

            messagebox.showinfo("Success", "Transaction has been saved")
        except Exception as e:
            return messagebox.showerror("Error", e)

        controller.step(container)


class BuildTransactionPage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Build Transaction', cnf=TOP_LABEL).pack()

        tk.Label(self, text='Payment Address', font=MEDIUM_FONT).pack(pady=(20, 2))
        self.payment_address = tk.Entry(self)
        self.payment_address.pack()

        self.amount = tk.IntVar(value=container.master.config['tokens_amount'])

        tk.Label(self, text='Amount', font=MEDIUM_FONT).pack(pady=(20, 2))
        tk.Entry(self, textvariable=self.amount).pack()

        tk.Button(self, text='Build', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=20)

    def _on_click(self, container, controller):
        try:
            load_plugin()
            (container.master.context['transaction'], _) = \
                build_mint_transaction(container.master.context['wallet_handle'],
                                       self.payment_address.get(), self.amount.get())
            close_wallet(container.master.context['wallet_handle'])
        except Exception as e:
            return messagebox.showerror("Cannot build Transaction", e)

        controller.step(container)


class SendTransactionPage(tk.Frame):
    def __init__(self, container, controller):
        tk.Frame.__init__(self, container)
        tk.Label(self, text='Send Transaction to Ledger', cnf=TOP_LABEL).pack()

        self.input_filename = tk.StringVar()
        tk.Button(self, text='Select Transaction file', font=MEDIUM_FONT,
                  command=lambda: self._select_input_file()).pack(pady=(20, 5))
        tk.Message(self, textvariable=self.input_filename, font=MEDIUM_FONT, width=260).pack()

        tk.Button(self, text='Send', font=MEDIUM_FONT,
                  command=lambda: self._on_click(container, controller)).pack(pady=30)

    def _select_input_file(self):
        self.input_filename.set(filedialog.askopenfilename(initialdir=INITIAL_DIR, title="Select Transaction file"))

    def _on_click(self, container, controller):
        try:
            if not 'pool_handle' in container.master.context:
                container.master.context['pool_handle'] = open_pool(container.master.config)

            with open(self.input_filename.get(), "r") as input_filename:
                self.transaction = input_filename.read()

            send_transaction(container.master.context['pool_handle'], self.transaction)

            close_pool(container.master.context['pool_handle'])

            messagebox.showinfo("Success", "Transaction has been sent")
        except Exception as e:
            return messagebox.showerror("Error", e)

        controller.step(container)


if __name__ == '__main__':
    app = MainWindow()
    app.mainloop()
