import tkinter
from tkinter import ttk, N, S, E, W

root = tkinter.Tk()
content = ttk.Frame(root, padding=(5,5,10,10))
frm_signedin = ttk.Frame(content, borderwidth=5, relief="sunken", width=200, height=100)

test_list = ["Jon Snow", "Tyrion Lannister", "Sandor Clegane", "Syrio Forel"]
# widgets
lbl_signedin = ttk.Label(content, text="Currently Signed In:")
lbl_signedin_list = ttk.Label(frm_signedin, text=('\n'.join(test_list)))
lbl_welcome = ttk.Label(content, text="Welcome to the STEM Learning Center!")
lbl_name = ttk.Label(content, text="Enter Student ID")
ent_name = ttk.Entry(content)
btn_sign = ttk.Button(content, text="Sign In/Out")

# assemble grid
content.grid(column=0, row=0, sticky=(N, S, E, W))
lbl_signedin.grid(column=0, row=0, pady=0, sticky=(W))
frm_signedin.grid(column=0, row=1, columnspan=1, rowspan=3, sticky=(N, S, E, W))
lbl_signedin_list.grid(column=0, row=0, columnspan=1, rowspan=3)
lbl_welcome.grid(column=2, row=1, columnspan=1)
lbl_name.grid(column=2, row=2, columnspan=1, sticky=(N))
ent_name.grid(column=2, row=2, columnspan=1, sticky=(E, W))
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
