import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import *

class TextEditor:
    def __init__(self, master):
        self.master = master
        self.master.title("Textor")
        self.master.geometry("800x600")
        self.master.iconbitmap(r".\notepad.ico") 
        
        self.master.protocol("WM_DELETE_WINDOW", self.on_close)

        self.file_path = None
        
        self.text = tk.Text(self.master, bd=2, relief=tk.SOLID)
        self.text.pack(expand=True, fill='both', padx=5, pady=5)
        
        self.status_bar = Label(self.master, text="Ln 1, Col 1", bd=1, relief=SUNKEN, anchor=E)
        self.status_bar.pack(side=BOTTOM, fill=X)

        self.master.bind("<KeyRelease>", self.update_cursor_position)
        self.master.bind("<ButtonRelease-1>", self.update_cursor_position)
        # Create a menu bar with a nice color
        self.menu_bar = tk.Menu(self.master, bg="#4d4d4d", fg="white", activebackground="#333333")
        self.master.config(menu=self.menu_bar)
        
        # Create file menu
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False, bg="#4d4d4d", fg="white")
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="New", command=self.new_file, accelerator="Ctrl+N")
        self.file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        self.file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.master.quit, accelerator="Ctrl+Q")
        
        # Create edit menu
        self.edit_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.menu_bar.add_cascade(label="Edit", menu=self.edit_menu)
        self.edit_menu.add_command(label="Copy", command=self.copy_text, accelerator="Ctrl+C")
        self.edit_menu.add_command(label="Cut", command=self.cut_text, accelerator="Ctrl+X")
        self.edit_menu.add_command(label="Paste", command=self.paste_text, accelerator="Ctrl+V")
        self.edit_menu.add_separator()
        self.edit_menu.add_command(label="Undo", command=self.text.edit_undo, accelerator="Ctrl+Z")
        self.edit_menu.add_command(label="Redo", command=self.text.edit_redo, accelerator="Ctrl+Y")
        
        # Bind keyboard shortcuts to menu items
        self.master.bind('<Control-n>', lambda e: self.new_file())
        self.master.bind('<Control-o>', lambda e: self.open_file())
        self.master.bind('<Control-s>', lambda e: self.save_file())
        self.master.bind('<Control-q>', lambda e: self.on_close())
        self.master.bind('<Control-c>', lambda e: self.copy_text())
        self.master.bind('<Control-x>', lambda e: self.cut_text())
        self.master.bind('<Control-v>', lambda e: self.paste_text())
        self.master.bind('<Control-z>', lambda e: self.undo())
        self.master.bind('<Control-y>', lambda e: self.redo())
        
        # Create a dictionary to map file types to extensions
        self.file_types = {
            'Text files': ('Text Files', '.txt'),
            'Python files': ('Python Files', '.py'),
            'All files': ('Other', '.*')
        }
        
        # Create the text area and scrollbar
        self.text = Text(self.text, wrap=WORD, undo=True)
        self.text.pack(side=LEFT, fill=BOTH, expand=True)

        self.scrollbar = Scrollbar(self.text, command=self.text.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        
        self.text.config(yscrollcommand=self.scrollbar.set)


    # Create undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []
        
        # Set the maximum undo limit to 1000
        self.text['undo'] = True
        self.text['maxundo'] = 1000
    
        def on_scroll(*args):
            self.line_numbers.yview_moveto(args[0])
            self.text.yview_moveto(args[0])

        self.scrollbar.config(command=on_scroll)
        self.text.bind('<MouseWheel>', lambda event: on_scroll('scroll', event.delta, 'units'))
        
        
        # Bind keyboard shortcuts for zooming in and out
        self.text.bind("<Control-plus>", self.zoom_in)
        self.text.bind("<Control-minus>", self.zoom_out)
        # Bind mouse wheel scrolling for zooming in and out
        self.text.bind("<MouseWheel>", self.zoom)

        # Set the initial font size and zoom level
        self.font_size = 12
        self.zoom_level = 0
        self.text.config(font=('TkDefaultFont', self.font_size))

    def zoom_in(self, event):
        # Increase the font size and zoom level
        self.font_size += 1
        self.zoom_level += 1
        self.text.config(font=('TkDefaultFont', self.font_size))

    def zoom_out(self, event):
        # Decrease the font size and zoom level
        if self.font_size > 1:
            self.font_size -= 1
            self.zoom_level -= 1
            self.text.config(font=('TkDefaultFont', self.font_size))
            
    def zoom(self, event):
        # Zoom in or out based on the direction of the mouse wheel scrolling
        if event.delta > 0:
            self.zoom_in(event)
        else:
            self.zoom_out(event)
            
    def new_file(self):
        self.text.delete('1.0', 'end')
        
    def open_file(self):
        if self.check_file_saved():
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            if file_path:
                self.file_path = file_path
                self.text.delete(1.0, END)
                with open(file_path, "r") as file:
                    self.text.insert(END, file.read())
            
    def save_file(self):
        if self.file_path is None:
            return self.save_file_as()
        else:
            try:
                with open(self.file_path, "w") as file:
                    file.write(self.text.get(1.0, END))
                self.text.edit_modified(False)
                return True
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving the file:\n{str(e)}")
                return False
            
    def copy_text(self):
        self.text.clipboard_clear()
        self.text.clipboard_append(self.text.selection_get())
        
    def cut_text(self):
        # Check if there is a selected text range
        if self.text.tag_ranges("sel"):
            self.copy_text()
            self.master.delete('sel.first', 'sel.last')
        
    def paste_text(self):
        # Check if there is a selected text range
        if self.master.tag_ranges("sel"):
            # Clear the current selection
            self.master.delete("sel.first", "sel.last")

        # Insert the clipboard content
        clipboard_text = self.master.clipboard_get()
        self.text.insert("insert", clipboard_text)

    def undo(self):
        if self.undo_stack:
            # Get the last change from the undo stack
            last_change = self.undo_stack.pop()
            # Add the current text to the redo stack
            self.redo_stack.append(self.text.get('1.0', 'end'))
            # Restore the text to the previous state
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', last_change)
            
    def redo(self):
        if self.redo_stack:
            # Get the last change from the redo stack
            last_change = self.redo_stack.pop()
            # Add the current text to the undo stack
            self.undo_stack.append(self.text.get('1.0', 'end'))
            # Restore the text to the next state
            self.text.delete('1.0', 'end')
            self.text.insert('1.0', last_change)
    
    def on_close(self):
        if self.check_file_saved():
            self.master.destroy()

  
    def check_file_saved(self):
        if self.is_text_modified():
            answer = messagebox.askyesnocancel("Unsaved Changes", "Do you want to save the file?")
            if answer is None:  # Cancel button clicked
                return False
            elif answer:  # Yes button clicked
                return self.save_file()
        return True
    
    def is_text_modified(self):
        return self.text.edit_modified()
    
    
    def save_file_as(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            self.file_path = file_path
            return self.save_file()
        return False
    
    def update_cursor_position(self, event=None):
        cursor_pos = self.text.index(INSERT)
        line, column = cursor_pos.split('.')
        line = int(line)
        column = int(column)
        self.status_bar.config(text=f"Ln {line}, Col {column}")
    

if __name__ == '__main__':
    root = tk.Tk()
    TextEditor(root)
    root.mainloop()
