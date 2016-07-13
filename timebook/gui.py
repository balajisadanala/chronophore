from timebook import timebook
import tkinter
from tkinter import ttk, N, S, E, W

t = timebook.Timesheet()

test_list = ["Jon Snow", "Tyrion Lannister", "Sandor Clegane", "Syrio Forel"]

def sign_in_out():
    uid = ent_id.get()
    timebook.sign(t, uid)
    t.save_sheet()

# root window
root = tkinter.Tk()
content = ttk.Frame(root, padding=(5,5,10,10))

# widgets
frm_signedin = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)
lbl_signedin = ttk.Label(content, text="Currently Signed In:")
lbl_signedin_list = ttk.Label(frm_signedin, text=('\n'.join(test_list)))
lbl_welcome = ttk.Label(content, text="Welcome to the STEM Learning Center!")
lbl_id = ttk.Label(content, text="Enter Student ID")
user_id = tkinter.StringVar()
ent_id = ttk.Entry(content, textvariable=user_id)
btn_sign = ttk.Button(content, text="Sign In/Out", command=sign_in_out)

# assemble grid
content.grid(column=0, row=0, sticky=(N, S, E, W))
lbl_signedin.grid(column=0, row=0, pady=0, sticky=(W))
frm_signedin.grid(column=0, row=1, columnspan=1, rowspan=3, sticky=(N, S, E, W))
lbl_signedin_list.grid(column=0, row=0, columnspan=1, rowspan=3)
lbl_welcome.grid(column=2, row=1, columnspan=1)
lbl_id.grid(column=2, row=2, columnspan=1, sticky=(N))
# TODO(amin): add select all shortcuts to this entry
ent_id.grid(column=2, row=2, columnspan=1, sticky=(E, W))
btn_sign.grid(column=2, row=2, columnspan=1, sticky=(S))

# resize weights
root.columnconfigure(0, minsize=400, weight=1)
root.rowconfigure(0, minsize=200, weight=1)
content.columnconfigure(0, weight=1)
content.columnconfigure(1, weight=3)
content.columnconfigure(2, weight=3)
content.columnconfigure(3, weight=3)
content.rowconfigure(0, weight=0)
content.rowconfigure(1, weight=3)
content.rowconfigure(2, minsize=100, weight=1)
content.rowconfigure(3, weight=3)

root.mainloop()
