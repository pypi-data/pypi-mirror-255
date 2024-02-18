#!/usr/bin/env python
# coding: utf-8

# In[12]:
import csv
import sys
import os
import tkinter as tk
from tkinter import *
from tkinter import ttk, Toplevel, Label, Menu, PhotoImage
from tkinter import messagebox
from tkinter import filedialog
from PIL import ImageTk, Image
import multiprocessing
from AIUT_Tool import sub
import datetime
from tkinter import PhotoImage
from AIUT_Tool import AIUT_Core_Java as AIUT_Java
from AIUT_Tool import AIUT_Core_CSharp as AIUT_CSharp


# In[1]:
#lblKey,txtKey,lblFunction,txtFunction,lblLocation,txtLocation = None,None,None,None,None,None


class AboutScreen:
    def __init__(self, root,main_screen):
        self.root = root
        self.main_screen = main_screen
        self.about_window = Toplevel(self.root)
        self.about_window.title("About")
        self.about_window.geometry("320x230")
        self.about_window.resizable(False, False)  # To make the window non-resizable
        self.center_window()

        image_path = "about1.png"  # Replace with the path to your image
        image = Image.open(f"about1.png")
        photo = ImageTk.PhotoImage(image)

        lbl_image = Label(self.about_window, image=photo)
        lbl_image.image = photo
        lbl_image.place(x=1,y=1)

        btn_close = Button(self.about_window, text="Close", command=self.close_about_screen)
        btn_close.place(x=272, y=204)
        self.about_window.update_idletasks()
        self.center_window()

    def center_window(self):
        window_width = self.about_window.winfo_reqwidth()
        window_height = self.about_window.winfo_reqheight()

        screen_width = self.about_window.winfo_screenwidth()
        screen_height = self.about_window.winfo_screenheight()

        x_coordinate = int((screen_width - window_width) / 2)
        y_coordinate = int((screen_height - window_height) / 2)

        self.about_window.geometry("+{}+{}".format(x_coordinate, y_coordinate))

    def close_about_screen(self):
        self.main_screen.attributes('-disabled', False)
        self.about_window.destroy()

class Automation:
    def __init__(self,root):

        width = 1030
        height = 560

        self.root=root
        self.root.title("AIUTGen")
        # self.root.attributes("-type","dialog")
        # self.root.ogverrideredirect(1)

        screen_width = root.winfo_screenwidth()  # Width of the screen
        screen_height = root.winfo_screenheight()  # Height of the screen
        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))
        # self.root.withdraw()

        global lblFunction, lblFunction1, txtKey, txtLocation, src_file_path, lblTest, txtCode, progressbar, lblimage,lblimage2
        global btnload,btnsubmit,btngencc, CSV_FILE_PATH,TEST_RUN_LOG_PATH,FILE_PROCESSING_LOG

        def show_message(message):
            messagebox.showinfo("Message", message)

        self.menubar = tk.Menu(self.root)
        # File menu
        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.file_menu.add_command(label="Define Source",command=self.source_file,accelerator="Ctrl+N")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit",command=self.close_app, accelerator="Ctrl+Q")
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        
        # self.root.bind_all("<Control-n>", lambda event: self.source_file(event))

        self.root.bind("<Control-n>", lambda event: self.source_file())
        self.root.bind("<Control-q>", lambda event: self.close_app())
        # Test menu
        self.test_menu = tk.Menu(self.menubar, tearoff=0)
        self.test_menu.add_command(label="Generate Test Cases",command=self.submit, accelerator="Ctrl+G" )
        self.test_menu.add_command(label="Get Code Coverage", command=self.generate_code_coverage,accelerator="Ctrl+C")
        self.test_menu.add_command(label="Test Generation Summary", command=lambda: show_message("This feature to be provided!"),accelerator="Ctrl+T")
        self.menubar.add_cascade(label="Test", menu=self.test_menu)
        self.test_menu.entryconfigure("Generate Test Cases",state= "disabled")
        self.test_menu.entryconfigure("Get Code Coverage",state= "disabled")
        self.root.bind("<Control-g>", lambda event: self.submit())        
        self.root.bind("<Control-c>", lambda event: self.generate_code_coverage())
        self.root.bind("<Control-t>",lambda event: show_message("This feature to be provided!") )
                    
        
        # self.test_menu.entryconfigure("Test Generation Summary",state= "disabled")

        # System menu
        self.system_menu = tk.Menu(self.menubar, tearoff=0)
        self.system_menu.add_command(label="Settings", command=lambda: show_message("This feature to be provided!"),accelerator="Ctrl+X")
        self.menubar.add_cascade(label="System", menu=self.system_menu)
        self.root.bind("<Control-x>",lambda event: show_message("This feature to be provided!") )
        
        

        self.help_menu= tk.Menu(self.menubar, tearoff=0)
        self.help_menu.add_command(label="License", command=lambda: show_message("This feature to be provided!"),accelerator="Ctrl+Y")
        self.help_menu.add_command(label="About", command=self.show_about_popup,accelerator="Ctrl+Z")
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        
        self.root.bind("<Control-y>",lambda event: show_message("This feature to be provided!") )
        self.root.bind("<Control-z>",lambda event:self.show_about_popup() )
        

        # Configure the root window with the menu
        self.root.config(menu=self.menubar)
        self.api_key = StringVar()
        self.function = StringVar()
        self.function1 = StringVar()
        self.location = StringVar()
        self.code = None
        self.opt_TF = None

        self.img = ImageTk.PhotoImage(Image.open(f"AIUT_Tool\logo.png"))
        self.img2 = ImageTk.PhotoImage(Image.open(f"AIUT_Tool\initial1.png"))
        # self.img1 = ImageTk.PhotoImage(Image.open(f"3.png"))

        lbltitle=ttk.Label(self.root, text="Artificial Intelligence Based Unit Test Case Generator (AIUTGen)",foreground="blue",font=("Sans Serif",16,"bold"))
        lbltitle.place(x=210, y=50)

        self.DataFrame=Frame(root)
        self.firstframe = Frame(root)
        self.DataFrame.forget()
        self.firstframe.place(x=0,y=10,width=1050,height = 500)
        # self.DataFrame.place(x=0,y=75,width=1050,height = 500)
        
        # self.file_listbox = tk.Listbox(self.DataFrame)
        

        lblimage=Label(self.root,image=self.img)
        # lblimage.place(x=7, y=7)
        lblimage2 = Label(self.firstframe,image=self.img2)
        lblimage2.place(x=300,y=100)
        # lblimage1=Label(self.root,image=self.img1)
        # lblimage1.place(x=11, y=170)

        lblFunction=ttk.Label(self.DataFrame,text="Source Code",foreground="blue")
        lblFunction.place(x=200,y=190)
        
        self.function=Text(self.DataFrame,font=("MS Sans Serif",10),width=55,height=15)
        self.function.place(x=200, y=210)

        lblFunction1=ttk.Label(self.DataFrame,text="Generated Test Case",foreground="blue")
        lblFunction1.place(x=620,y=190)
        
        self.function1=Text(self.DataFrame,font=("MS Sans Serif",10),width=55,height=15)
        self.function1.place(x=620, y=210)

        lblFunction2=ttk.Label(self.DataFrame,text="Test Cases Details & Metrics",foreground="blue")
        lblFunction2.place(x=200,y=60)

        style = ttk.Style()
        style.configure("Custom.Vertical.TScrollbar", width=10)
        # self.filetree = ttk.Treeview(self.DataFrame,height=5,columns=("File","Path"),show="headings")
        # self.filetree.column("File",width=150)
        # self.filetree.column("Path",width=0,minwidth=0)
        # # self.filetree.heading("File",text="File Names")
        # self.filetree.heading("Path",text="File Path")
        
        # self.filetree.bind("<ButtonRelease-1>",self.on_tree_select)
        # self.filetree.place(x=40,y=150)
        

        
        # self.parent_iid = self.filetreeview.insert(parent='',
        #                      index='0',
        #                      text='Documents',
        #                      open=True,
        #                      image=dir_image)




        self.tree = ttk.Treeview(self.DataFrame, height=4)
        self.yscrollbar = ttk.Scrollbar(self.DataFrame,orient="vertical",command=self.tree.yview,style="Custom.Vertical.TScrollbar")
        self.yscrollbar.place(x=1000,y=70,height=120)
        self.tree.configure(yscrollcommand=self.yscrollbar.set)

        self.tree["columns"] = ("Snippet1", "Snippet2", "Snippet3", "Snippet4", "Snippet5","Snippet6","Snippet7","Snippet8","Snippet9", "Snippet10")
        self.tree.column("#0", width=40, minwidth=30)
        self.tree.column("Snippet1", width=100)
        self.tree.column("Snippet2", width=0, minwidth=0)
        self.tree.column("Snippet3", width=100)
        self.tree.column("Snippet4", width=0, minwidth=0)
        self.tree.column("Snippet5", width=100)
        self.tree.column("Snippet6", width=100)
        self.tree.column("Snippet7", width=100)
        self.tree.column("Snippet8", width=80)
        self.tree.column("Snippet9", width=110)
        self.tree.column("Snippet10", width=70)

        self.tree.heading("#0", text="SNo")
        self.tree.heading("Snippet1", text="SourceFile")
        self.tree.heading("Snippet2", text="")
        self.tree.heading("Snippet3", text="TestCaseFile")
        self.tree.heading("Snippet4", text="")
        self.tree.heading("Snippet5", text="TokensSent")
        self.tree.heading("Snippet6", text="TokensReceived")
        self.tree.heading("Snippet7", text="TotalTokens")
        self.tree.heading("Snippet8", text="Cost(USD)")
        self.tree.heading("Snippet9", text="Status")
        self.tree.heading("Snippet10", text="Time(Sec)")

        self.tree.bind("<ButtonRelease-1>", self.on_tree_click)
        style = ttk.Style()
        self.tree.place(x=200, y=80)

        test_framework = ["Select Test Framework", "JUnit(Java)", "NUnit(C#)", "MSTest(C#)", "UnitTest(Python)"]
        self.n = StringVar(self.DataFrame)
        self.n.set(test_framework[0])

        opt_test_framework = ttk.OptionMenu(self.DataFrame, self.n, *test_framework, command=self.callback)
        opt_test_framework.place(x=40, y=90)

        self.btnload = ttk.Button(self.DataFrame, command=self.open_file_dialog, text="Select Source", width=20,compound=tk.LEFT)
        self.btnload.place(x=40, y=120)
        self.btnload.config(state="disabled")

        self.btnsubmit = ttk.Button(self.DataFrame, command=self.submit, text="Generate Test Cases", width=20)
        # self.btnsubmit.place(x=40, y=150)
        self.btnsubmit.config(state="disabled")

        self.btngencc = ttk.Button(self.DataFrame, command=self.generate_code_coverage, text="Get Code Coverage", width=20)
        # self.btngencc.place(x=40, y=180)
        self.btngencc.config(state="disabled")

        self.btnclear=ttk.Button(self.DataFrame,command=self.clear,text="Clear",width=24)
        self.btnclear.place(x=40, y=150)
        self.btnclear.config(state="disabled")
        folder_icon = Image.open("AIUT_Tool/folder_icon.png")  # Replace "folder_icon.png" with your folder image file
        folder_icon = folder_icon.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        folder_icon = ImageTk.PhotoImage(folder_icon)
        self.btnload.config(image=folder_icon, compound=tk.LEFT)
        self.btnload.image = folder_icon
        

        # btnexit=ttk.Button(self.DataFrame,command=self.close_app,text="Exit",width=20)
        # btnexit.place(x=40, y=240)

        self.progressbar = ttk.Progressbar(self.DataFrame, mode="indeterminate")

    # This Method maintains the selection of Test Framework from the DropDown
    
        # scrollbar_source_x = ttk.Scrollbar(self.DataFrame, orient="horizontal", command=self.function.xview)
        scrollbar_source_y = ttk.Scrollbar(self.DataFrame, orient="vertical", command=self.function.yview)
       
        self.function.config(yscrollcommand=scrollbar_source_y.set)

        # scrollbar_source_x.place(x=200, y=437, width=590)
        scrollbar_source_y.place(x=600, y=210, height=250)
        # scrollbar_source_y_1.place(x=180, y=174, height=150)

        # Create horizontal and vertical scrollbars for Test Case text box
        # scrollbar_test_x = ttk.Scrollbar(self.DataFrame, orient="horizontal", command=self.function1.xview)
        scrollbar_test_y = ttk.Scrollbar(self.DataFrame, orient="vertical", command=self.function1.yview)
        
        self.function1.config(yscrollcommand=scrollbar_test_y.set)

        # scrollbar_test_x.place(x=600, y=437, width=590)
        scrollbar_test_y.place(x=1000, y=210, height=250)

        self.filetreeview = ttk.Treeview(self.DataFrame, show='tree')
        # self.filetreeview.place(x=7,y=180,width=180,height=130)
        self.filetreeview.bind("<ButtonRelease-1>", self.on_treeview_select) 
        self.filetreeview.bind("<Button-3>", self.show_context_menu)
        self.scrollbar_source_y_1 = ttk.Scrollbar(self.DataFrame, orient="vertical", command=self.filetreeview.yview)
        

        # global file_image,dir_image
        # file_image= PhotoImage(data=file_img)
        # dir_image = PhotoImage(data=dir_img)
        self.image_dict = {
            ".java": "AIUT_Tool\java1.png",
            ".cs": "AIUT_Tool\cs.png",
            ".py": "AIUT_Tool\py.png",
            ".dir": "AIUT_Tool/folder_icon.png",
            # Add more file extensions and corresponding image paths as needed
        }
        self.load_images()
    
    def load_images(self):
        self.image_dict = {ext: Image.open(path).resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC) for ext, path in self.image_dict.items()}
        self.image_dict = {ext: ImageTk.PhotoImage(image) for ext, image in self.image_dict.items()}

        # Load folder icon separately
        folder_icon_path = "AIUT_Tool/folder_icon.png"
        self.dir_image = Image.open(folder_icon_path).resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        self.dir_image = ImageTk.PhotoImage(self.dir_image)
    def new_folder(self, parent_path, directory_entries, parent_iid, d_image):
        for name in directory_entries:
            item_path = os.path.join(parent_path, name)
            if os.path.isdir(item_path):
                subdir_iid = self.filetreeview.insert(parent=parent_iid, index='end',
                                         text=name,
                                         image=d_image)
                try:
                    subdir_entries = os.listdir(item_path)
                    self.new_folder(parent_path=item_path,
                           directory_entries=subdir_entries,
                           parent_iid=subdir_iid,
                           d_image=d_image)
                except PermissionError:
                    pass
            else:
                file_extension = os.path.splitext(name)[1].lower()
                file_image = self.get_file_image(file_extension)
                self.filetreeview.insert(parent=parent_iid,
                            index='end',
                            text=name,
                            image=file_image)

    def get_file_image(self, file_extension):
        # Helper method to get the image based on the file extension
        return self.image_dict.get(file_extension, self.dir_image)

    def on_treeview_select(self, event):
        print("inside on_treeview_select")
        item = self.filetreeview.selection()[0]
        item_text = self.filetreeview.item(item, "text")
        item_path = os.path.join(self.get_folder_path(item), item_text)
        print(item_path)
        if os.path.isfile(item_path):
            with open(item_path, 'r') as file:
                content = file.read()
                self.function.delete("1.0", "end")
                self.function.insert("end", content)
        self.btnclear.config(state="enabled")

    def get_folder_path(self, item):
        # Helper method to get the folder path of an item in the treeview
        print("inside get_folder_path")
        parent = self.filetreeview.parent(item)
        if parent == '':
            return ""
        else:
            return os.path.join(self.get_folder_path(parent), self.filetreeview.item(parent, "text"))
    def show_message(message):
            messagebox.showinfo("Message", message)

    
    def show_context_menu(self, event):
        # Display context menu when right-clicking on an item in the treeview
        item = self.filetreeview.selection()[0]
        item_text = self.filetreeview.item(item, "text")
        item_path = os.path.join(self.get_folder_path(item), item_text)

        menu = Menu(self.DataFrame, tearoff=0)
        menu.add_command(label="Generate Test Case", command= lambda:  messagebox.showinfo("message",message="This feature to be provided!"))
        menu.post(event.x_root, event.y_root)

    def generate_test_case_handler(self, file_path):

        # Placeholder for the actual test case generation code
        print(f"Generate Test Case for: {file_path}")
    def show_about_popup(self):
    #    self.btngencc.config(state="disabled")
    #    self.btnsubmit.config(state="disabled")
    #    self.btnload.config(state="disabled")
    #    self.btnclear.config(state="disabled")
    #    self.test_menu.entryconfigure("Generate Test Cases",state= "disabled")
    #    self.test_menu.entryconfigure("Test Generation Summary",state="disabled")
    #    self.file_menu.entryconfigure("Define Source",state="disabled")
    #    self.file_menu.entryconfigure("Exit",state="disabled")
    #    self.system_menu.entryconfigure("Settings",state="disabled")
    #    self.help_menu.entryconfigure("License",state="disabled")
       self.root.attributes('-disabled', True)
       
       about_screen = AboutScreen(self.root,self.root)
    


    
    def callback(self, selection):
        print(self.n.get())
        sel_opt = self.n.get()
        self.opt_TF = self.n.get()
        if sel_opt == "JUnit(Java)":
            self.opt_TF = "JUnit"
        elif sel_opt == "NUnit(C#)":
            self.opt_TF = "NUnit"
        elif sel_opt == "MSTest(C#)":
            self.opt_TF = "MSTest"
        elif sel_opt == "UnitTest(Python)":
            self.opt_TF = "UnitTest"
        print(self.opt_TF)
        self.btnload.config(state="enabled")

    # This Method populates the Treeview
    def populate_treeview(self, tree, data):
        #skip_indices = [1, 3]
        start_idx = tree.get_children()
        if len(start_idx)<=0:
            start_idx=1
        else:
            start_idx = int(start_idx[-1])+1

        for i, row in enumerate(data[0:], start=start_idx):
            values = [value for j, value in enumerate(row)]
            tree.insert("", tk.END, iid=i, text=str(i), values=values)
        
    def load_files(self,directory_path):
        self.filetree.delete(*self.filetree.get_children())
        for root,dirs, files in os.walk(directory_path):
            for file in files:
                file_path = os.path.join(root,file)
                relative_path = os.path.relpath(file_path,directory_path)
                self.filetree.insert("","end",values=(file,relative_path),tags=(file_path,))

    def on_treeview_scroll(self, *args):
        self.tree.yview(*args)

    def on_tree_click(self, event):

        if len(self.tree.get_children()) > 0:
            item = self.tree.selection()[0]
            snippet1 = self.tree.item(item, "values")[1]
            snippet3 = self.tree.item(item, "values")[3]
            selected_file_name = os.path.basename(snippet1)
            updated_label_text = f"Source Code: {selected_file_name}"
            lblFunction.config(text=updated_label_text)

            selected_file_name = os.path.basename(snippet3)
            updated_label_text = f"Test Case: {selected_file_name}"
            lblFunction1.config(text=updated_label_text)

            self.function.delete("1.0", "end")
            self.function.insert("end", self.process_file(snippet1))

            self.function1.delete("1.0", "end")
            self.function1.insert("end", self.process_file(snippet3))
            self.btnclear.config(state="enabled")
            

           
    def on_tree_select(self,event):
        if len(self.filetree.get_children()) > 0:
            item = self.filetree.selection()[0]
            file_path = self.filetree.item(item,"tags")[0]
            with open(file_path,'r') as file:
                code = file.read()
                self.function.delete("1.0","end")
                self.function.insert("end",code)
            self.btnclear.config(state="enabled")
    def file_click(self,event):
        # if len(self.file_listbox.get_children()) > 0:
        #     item = self.file_listbox.selection()[0]
        #     snippet1 = self.file_listbox.item(item, "values")[0]
           

            self.function.delete("1.0", "end")
            self.function.insert("end", self.process_file(event))
            self.btnclear.config(state="enabled")


    ##########################################
    # This method Reads the CSV file and
    # returns the data to fill in Grid
    #########################################
    def read_csv(self, file_path):
        with open(file_path, newline="") as file:
            csv_reader = csv.reader(file)
            data = list(csv_reader)
        return data

    def check_file(self, file_name):
        return True

    def process_file(self, file_path):
        # Implement your file processing logic here
        # For demonstration, let's just display the contents of the selected file
        file_contents = None
        if self.check_file(file_path):
            with open(file_path, 'r') as file:
                file_contents = file.read()
        return file_contents

    def source_file(self):
        self.firstframe.place_forget()
        lblimage.place(x=7, y=7)
        self.DataFrame.place(x=0,y=75,width=1050,height = 500)

        # self.file_listbox.delete(0,tk.END)

    def open_file_dialog(self):
        self.filetreeview.place(x=7,y=180,width=170,height=130)
        self.scrollbar_source_y_1.place(x=180, y=174, height=150)
        # self.DataFrame.pack_forget()
        # self.DataFrame.place(x=0,y=75,width=1050,height = 500)
        # self.file_listbox.delete(0,tk.END)
        # self.root.deconify()
        #self.populate_treeview(self.tree, self.read_csv(CSV_FILE_PATH))
        self.src_folder_path = None
        if (self.opt_TF)==None:
            messagebox.showinfo("Information", "Please Select The Test Framework!")
            return
        elif (self.opt_TF)=="JUnit":
            messagebox.showinfo("Information", "Please Select The Java Source Code Location!")
        elif (self.opt_TF)=="NUnit" or (self.opt_TF)=="MSTest":
            messagebox.showinfo("Information", "Please Select The C# Source Code Location!")
        elif (self.opt_TF)=="UnitTest":
            messagebox.showinfo("Information", "Please Select The Python Source Code Location!")

        self.src_folder_path = filedialog.askdirectory(title="Select the Source Code Location")
        
        if (self.src_folder_path)!=None and len(self.src_folder_path)>1:
            self.btnsubmit.config(state="enabled")
            self.test_menu.entryconfigure("Generate Test Cases",state= "normal")
        start_path = os.path.expanduser(self.src_folder_path)
        start_dir_entries = os.listdir(start_path)
        parent_iid = self.filetreeview.insert(parent='',
                             index='0',
                             text=self.src_folder_path,
                             open=True,
                             image=self.dir_image)
        self.new_folder(parent_path=start_path,
           directory_entries=start_dir_entries,
           parent_iid=parent_iid,
           d_image=self.dir_image)
        print(self.src_folder_path)

    def submit(self):
        now = datetime.datetime.now()
        timestamp = now.strftime("%Y%m%d%H%M%S")
        result_path = sub.get_test_gen_result_path(self.opt_TF, timestamp)
        self.CSV_FILE_PATH = result_path[0]
        self.TEST_RUN_LOG_PATH = result_path[1]
        self.FILE_PROCESSING_LOG = result_path[2]
        print(self.CSV_FILE_PATH)
        print("SUBMIT")
        #if os.path.exists(CSV_FILE_PATH):
        #    os.remove(CSV_FILE_PATH)

        messagebox.showinfo("Information!", "Generating Test Cases. Please wait for sometime")
        self.progressbar.place(x=7, y=320, width=180)
        self.queue_loop(self.src_folder_path, self.opt_TF)

    def clear(self):
        global lblKey, txtKey, lblFunction, lblFunction1, txtFunction, txtLocation

        for item in self.tree.get_children():
            self.tree.delete(item)

        self.function.delete("1.0", "end")
        self.function1.delete("1.0", "end")
        self.btngencc.config(state="disabled")
        self.btnsubmit.config(state="disabled")
        self.btnload.config(state="disabled")
        self.btnclear.config(state="disabled")
        self.test_menu.entryconfigure("Generate Test Cases",state= "disabled")
        for item in self.filetreeview.get_children():
            self.filetreeview.delete(item)

    def generate_code_coverage(self):
        result = ""
        if (self.opt_TF) == "JUnit":
            result = AIUT_Java.execute_test_cases(self.opt_TF)
        elif (self.opt_TF)=="NUnit" or (self.opt_TF)=="MSTest":
            result = AIUT_CSharp.execute_test_cases("mstest")
        if result[0] == True:
            messagebox.showinfo("Success!", "Test Executed and Report Generated, Please refer the log for detailed information!")
            print("Test Executed :" + result[1])
        else:
            messagebox.showerror("Information", "Error During Test Execution, Please refer the log!")
            print("Error during Test Execution :" + result[1])

        sub.create_file(self.TEST_RUN_LOG_PATH, result[1])

    def check_status(self, p):
        """ p is the multiprocessing.Process object """
        if p.is_alive():  # Then the process is still running
            root.after(200, lambda p=p: self.check_status(p))  # After 200 ms, it will check the status again.
        else:
            print("Process Completed!")
            self.progressbar.stop()
            self.progressbar.place(x=0, y=0, width=0)
            self.btngencc.config(state="enabled")
            self.test_menu.entryconfigure("Generate Test Cases",state= "normal")
            self.test_menu.entryconfigure("Get Code Coverage",state= "normal")
            # self.test_menu.entryconfigure("Test Generation Summary",state= "normal")
            self.btnsubmit.config(state="enabled")
            self.btnload.config(state="enabled")
            self.populate_treeview(self.tree, self.read_csv(self.CSV_FILE_PATH))
            #os.remove(CSV_FILE_PATH)
            return 1

    def queue_loop(self,a,b):
        print("CSV File Path "+self.CSV_FILE_PATH)
        p = multiprocessing.Process(target=sub.loop,
                                    args=(a, b, self.CSV_FILE_PATH, self.FILE_PROCESSING_LOG))
        # You can pass args and kwargs to the target function like that
        # Note that the process isn't started yet. You call p.start() to activate it.
        p.start()
        self.progressbar.start()
        self.btngencc.config(state="disabled")
        self.btnsubmit.config(state="disabled")
        self.btnload.config(state="disabled")
        self.test_menu.entryconfigure("Generate Test Cases",state= "disabled")
        self.test_menu.entryconfigure("Get Code Coverage",state= "disabled")
       
        result = self.check_status(p)  # This is the next function we'll define
        return result

    def close_app(self):
        #sys.exit('Closing the AIUT Application')
        os._exit(0)
def main():
    # Your main application logic here
    root=Tk()
    obj=Automation(root)
    root.mainloop()
    
    print("Hello from AIUT!")
if __name__=="__main__":
    main()
    root=Tk()
    obj=Automation(root)
    

    

    root.mainloop()