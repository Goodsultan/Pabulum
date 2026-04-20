import tkinter as tk
from tkinter import ttk


def SimpleDialog(title='Enter Input', message=None, input_class=str, initial_value=''):
    # Toplevel
    top = tk.Toplevel()
    top.title(title)
    top.attributes('-topmost', True)
    # top.resizable(False, False)

    # Message
    if message:
        message = ttk.Label(top, text=message)
        message.pack(expand=False, fill=tk.X, side=tk.TOP)

    initial_value = str(initial_value)
    final_value = None
    if '\n' in initial_value or len(initial_value) > 30:
        # Text
        def on_entry_return():
            nonlocal final_value
            # Prevent tkinter from inserting an additional newline
            final_value = entry.get("1.0", 'end-1c')
            top.destroy()

        entry = tk.Text(top, wrap="word")
        entry.pack(expand=True, fill=tk.BOTH, side=tk.TOP)

        entry.insert(tk.END, initial_value)
        entry.focus()
        entry.focus_set()

        btn = tk.Button(top, text='Enter', command=on_entry_return)
        btn.pack(expand=False, fill=tk.X, side=tk.BOTTOM)

        top.wait_window()
    else:
        # Entry
        def on_entry_return(e):
            nonlocal final_value
            final_value = entry_text_variable.get()
            top.destroy()

        entry_text_variable = tk.StringVar(value=initial_value)
        entry = ttk.Entry(top, textvariable=entry_text_variable)
        entry.pack(expand=True, fill=tk.X, side=tk.TOP)
        entry.focus()
        entry.focus_set()
        entry.select_range(0, tk.END)
        entry.config(width=60)
        entry.bind('<Return>', on_entry_return)

        top.wait_window()

    return input_class(final_value)
