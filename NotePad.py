import tkinter as tk
from tkinter import filedialog

#integrated NotePad in the Travel frame
class NotePad:
    def __init__(self, note_root):
        self.note_root = note_root

        self.note_frame = tk.Frame(self.note_root)
        self.note_frame.pack_forget()

        self.text_scroll = tk.Scrollbar(self.note_frame)
        self.text_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.my_text = tk.Text(self.note_frame, width=50, height=25, undo=True, yscrollcommand=self.text_scroll.set)
        self.my_text.pack_forget()

        self.note_root.lift()
        self.note_root.attributes('-topmost', True)

        self.note_root.deiconify()
        self.note_frame.pack(pady=5)
        self.my_text.pack()

        # Create menu

        self.note_menu = tk.Menu(self.note_root)
        self.note_root.config(menu=self.note_menu)

        # Add File Menu

        self.file_menu = tk.Menu(self.note_menu, tearoff=False)
        self.note_menu.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Save As", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.note_root.destroy)

        self.text_scroll.config(command=self.my_text.yview)

    #save as option
    def save_as_file(self):

        text_file = filedialog.asksaveasfilename(defaultextension=".*", title="Save File", filetypes=(
        ("Text Files", "*.txt"), ("HTML Files", "*.html"), ("All Files", "*.*")))

        if text_file:
            name = text_file
            self.note_root.title(f'{name} - NotePad!')

            text_file = open(text_file, 'w')
            text_file.write(self.my_text.get(1.0, tk.END))
            text_file.close()


