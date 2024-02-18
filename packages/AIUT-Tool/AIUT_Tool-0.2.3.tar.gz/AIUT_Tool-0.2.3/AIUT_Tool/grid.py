# from tkinter import *
# import os
# from tkinter import ttk
# import tkinter as tk
# from tkinter import filedialog
# from PIL import ImageTk, Image





# class Automation:
#     def __init__(self,root):
#         self.root=root
#         self.root.title("AIUTGen")
#         self.root.geometry("1020x500")
#         self.filetreeview = ttk.Treeview(self.root, show='tree')
#         self.filetreeview.place(x=7,y=180,width=180)
#         self.filetreeview.bind("<ButtonRelease-1>", self.on_treeview_select) 
#         btnload = ttk.Button(self.root, command=self.open_file_dialog, text="Select Source", width=20,compound=tk.LEFT)
#         btnload.place(x=40, y=120)
#         global lblFunction
#         lblFunction=ttk.Label(self.root,text="Source Code",foreground="blue")
#         lblFunction.place(x=200,y=190)
        
#         self.function=Text(self.root,font=("MS Sans Serif",10),width=55,height=15)
#         self.function.place(x=200, y=210)

#         file_img = """
# iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAABGdB
# TUEAALGPC/xhBQAAAAlwSFlzAAAScwAAEnMBjCK5BwAAAalJREFU
# OE99kUtLAmEUhg38Af6a6he06SJIF8FFREVtqkVEkBB2IcJIRDAk
# 80KrNq3CWihuuuh4GVIwM9BSa0bHUXGc8X7p1Bc6jtLLxzAwz3Pm
# nPMNcaWySCR6CYVoOgMvzWaz3W63Wq1GowFPsVg8PDIqkUjg019A
# gEOSJHAowEHAhDidzmAwGI3FEPZTXSDwafiJ3W5nWRbH8TSVGSAI
# aBDi8TiGYT6fz2QyCwU+Dc0ADanX67XfWK3W/4QOjYRqtWqxWIQC
# mhKh/NpAVyoVs/GcclwzabI7NF/odILocrnsPFwvGRcS6uUeob8T
# RDOxMGuYz2vkfsdtVxhIg1AqMqnTRUYrD+iU2Vy+R+jvBMpTN+aC
# Zi6umo2+RXouDmgkFJ4fyLNNNvUFdJFM0kfTuQOpfk9ZZLmuQBBE
# Z4Np/VrtapVSKwqf7wmlLLc/iR9vGAyGnrWCgC4ImmZpKqVbKeoV
# xK4sq5pI7kgjAfzCZBIK/PWX8jRxspRVjVPbY8FLLcdxfQKZ8vlx
# j9eLebxuzOPGMO/j/YdyJro1dWezPblc4defieF8A+ZBma193+p6
# AAAAAElFTkSuQmCC
# """
#         dir_img = """
# iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAABGdB
# TUEAALGPC/xhBQAAAAlwSFlzAAAScgAAEnIBXmVb4wAAAihJREFU
# OE990vtv0kAcAPDh4wd/8w/yp5n4i4kkmizoBMKcRIfG7YepWSSZ
# MSTGSXQao8wtjIw5ZkJEJ4+O0CGvoWhSCmw0sFJaHoU+GEJbyDax
# EwMjQS+Xy30v97m7791JOF4Y+FMOBEJsj508PXD8lERyoj3Yp4ig
# XclNRSlyg0F0TFxLRbXFyAMqaarkQrXabmfO4eqdoBRWtgQnujGM
# +DRVbIYnTU3Wvrf7hcubGRToTOsFvK3V/JZyy6KeCXL7CZc3CEVj
# k7bTO85/A+FDgwr6rKNIQEtu6XnC0Ch/+j+wCSXXulke994vxh/X
# sNkGaaXTfXfYVLbEIwk2gbQBpstxz0QOmq6mdXxxmUr1A8Wg4i8o
# rLoWh2C3hvhxr5KcqhMLVMrRJ4eCX97irL/qFh6fdxkvQoAaj4yz
# iTv17KsyYu8D8t7hg+q7fXahjr50GaWQawT7OkbDN3/u6JIflQxb
# qXN8zzsQniv7tGGv9Czx/tz64gXIqcTCagoaqWxpcO/dKBzL4oTI
# uu+QBYaaBX2DeBgyDoJmKQzIMyEVE5Wz8HXMO7W29tnnD8TiiS5A
# HbIGPi1kJn3zZzdWLh2CoIKGZHRUlXJPzs29XVoy40SuC6p0lgyo
# +PS4e/aM8835GHALDWvY2LVybAxcVs881XtAUEyjC8SEGPx7bfu2
# 4/mgzfwiEgSz4dcJixRxjq5YVtEM1r6oHiDGuP9RwHS1TOaP/tCj
# /d+VL1STn8NNZQAAAABJRU5ErkJggg==
# """
#         global file_image,dir_image
#         file_image= PhotoImage(data=file_img)
#         dir_image = PhotoImage(data=dir_img)
#         # file_image = Image.open(f"java.png")
#         # dir_image = Image.open(f"folder_icon.png")
#         # file_image = file_image.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
#         # dir_image = dir_image.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
#     def on_treeview_select(self, event):
#         print("inside on_treeview_select")
#         item = self.filetreeview.selection()[0]
#         item_text = self.filetreeview.item(item, "text")
#         item_path = os.path.join(self.get_folder_path(item), item_text)
#         print(item_path)
#         if os.path.isfile(item_path):
#             with open(item_path, 'r') as file:
#                 content = file.read()
#                 self.function.delete("1.0", "end")
#                 self.function.insert("end", content)

#     def get_folder_path(self, item):
#         # Helper method to get the folder path of an item in the treeview
#         print("inside get_folder_path")
#         parent = self.filetreeview.parent(item)
#         if parent == '':
#             return ""
#         else:
#             return os.path.join(self.get_folder_path(parent), self.filetreeview.item(parent, "text"))

#     def open_file_dialog(self):
#         src_folder_path = None
#         src_folder_path = filedialog.askdirectory(title="Select the Source Code Location")
#         start_path = os.path.expanduser(src_folder_path)
#         start_dir_entries = os.listdir(start_path)
#         parent_iid = self.filetreeview.insert(parent='',
#                              index='0',
#                              text=src_folder_path,
#                              open=True,
#                              image=dir_image)
#         self.new_folder(parent_path=start_path,
#            directory_entries=start_dir_entries,
#            parent_iid=parent_iid,
#            f_image=file_image,
#            d_image=dir_image)
#         print(src_folder_path)
#     def new_folder(self,parent_path, directory_entries,
#                parent_iid, f_image, d_image):
#          for name in directory_entries:
#             item_path = parent_path+os.sep+name
#             if os.path.isdir(item_path):
#                 subdir_iid = self.filetreeview.insert(parent=parent_iid,index='end',
#                                          text=name,
#                                          image=d_image)
#                 try:
#                     subdir_entries = os.listdir(item_path)
#                     self.new_folder(parent_path=item_path,
#                            directory_entries=subdir_entries,
#                            parent_iid=subdir_iid,
#                            f_image=f_image,
#                            d_image=d_image)
#                 except PermissionError:
#                     pass
#             else:
#                 self.filetreeview.insert(parent=parent_iid,
#                             index='end',
#                             text=name,
#                             image=f_image)
#             print(item_path)
           


# if __name__=="__main__":
#     root=Tk()
#     obj=Automation(root)
#     root.mainloop()





from tkinter import *
import os
from tkinter import ttk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

class Automation:
    def __init__(self, root):
        self.root = root
        self.root.title("AIUTGen")
        self.root.geometry("1020x500")

        self.filetreeview = ttk.Treeview(self.root, show='tree')
        self.filetreeview.place(x=7, y=180, width=180)
        self.filetreeview.bind("<ButtonRelease-1>", self.on_treeview_select) 

        btnload = ttk.Button(self.root, command=self.open_file_dialog, text="Select Source", width=20, compound=tk.LEFT)
        btnload.place(x=40, y=120)

        global lblFunction
        lblFunction = ttk.Label(self.root, text="Source Code", foreground="blue")
        lblFunction.place(x=200, y=190)

        self.function = Text(self.root, font=("MS Sans Serif", 10), width=55, height=15)
        self.function.place(x=200, y=210)

        self.file_image = Image.open("java.png")  # Change the image file name
        self.dir_image = Image.open("folder_icon.png")  # Change the image file name

        self.file_image = self.file_image.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
        self.dir_image = self.dir_image.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)

        self.file_image = ImageTk.PhotoImage(self.file_image)
        self.dir_image = ImageTk.PhotoImage(self.dir_image)
        self.image_dict = {
            ".java": "java.png",
            ".cs": "cs.png",
            ".py": "py.png",
            ".dir": "folder_icon.png",
            # Add more file extensions and corresponding image paths as needed
        }
        self.load_images()
    def load_images(self):
        for ext, path in self.image_dict.items():
            image = Image.open(path)
            image = image.resize((18, 18), Image.ANTIALIAS if hasattr(Image, 'ANTIALIAS') else Image.BICUBIC)
            self.image_dict[ext] = ImageTk.PhotoImage(image)
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
        return self.image_dict.get(file_extension, self.image_dict[".dir"])


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

    def get_folder_path(self, item):
        # Helper method to get the folder path of an item in the treeview
        print("inside get_folder_path")
        parent = self.filetreeview.parent(item)
        if parent == '':
            return ""
        else:
            return os.path.join(self.get_folder_path(parent), self.filetreeview.item(parent, "text"))

    def open_file_dialog(self):
        src_folder_path = None
        src_folder_path = filedialog.askdirectory(title="Select the Source Code Location")
        start_path = os.path.expanduser(src_folder_path)
        start_dir_entries = os.listdir(start_path)
        parent_iid = self.filetreeview.insert(parent='',
                             index='0',
                             text=src_folder_path,
                             open=True,
                             image=self.dir_image)
        self.new_folder(parent_path=start_path,
           directory_entries=start_dir_entries,
           parent_iid=parent_iid,
           f_image=self.file_image,
           d_image=self.dir_image)
        print(src_folder_path)

    # def new_folder(self, parent_path, directory_entries, parent_iid, f_image, d_image):
    #      for name in directory_entries:
    #         item_path = os.path.join(parent_path, name)
    #         if os.path.isdir(item_path):
    #             subdir_iid = self.filetreeview.insert(parent=parent_iid, index='end',
    #                                      text=name,
    #                                      image=d_image)
    #             try:
    #                 subdir_entries = os.listdir(item_path)
    #                 self.new_folder(parent_path=item_path,
    #                        directory_entries=subdir_entries,
    #                        parent_iid=subdir_iid,
    #                        f_image=f_image,
    #                        d_image=d_image)
    #             except PermissionError:
    #                 pass
    #         else:
    #             self.filetreeview.insert(parent=parent_iid,
    #                         index='end',
    #                         text=name,
    #                         image=f_image)
    #         print(item_path)

if __name__ == "__main__":
    root = Tk()
    obj = Automation(root)
    root.mainloop()



# from tkinter import *
# import os
# from tkinter import ttk
# import tkinter as tk
# from tkinter import filedialog
# from PIL import Image, ImageTk

# class Automation:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("AIUTGen")
#         self.root.geometry("1020x500")

#         self.filetreeview = ttk.Treeview(self.root, show='tree')
#         self.filetreeview.place(x=7, y=180, width=180)
#         self.filetreeview.bind("<ButtonRelease-1>", self.on_treeview_select)

#         btnload = ttk.Button(self.root, command=self.open_file_dialog, text="Select Source", width=20, compound=tk.LEFT)
#         btnload.place(x=40, y=120)

#         global lblFunction
#         lblFunction = ttk.Label(self.root, text="Source Code", foreground="blue")
#         lblFunction.place(x=200, y=190)

#         self.function = Text(self.root, font=("MS Sans Serif", 10), width=55, height=15)
#         self.function.place(x=200, y=210)

#         self.image_dict = {
#             ".java": "java.png",
#             ".cs": "cs.png",
#             ".py": "py.png",
#             ".dir": "folder_icon.png",
#             # Add more file extensions and corresponding image paths as needed
#         }

#         # Initialize image variables
#         self.file_image = self.get_file_image(".java")  # Choose an initial file extension
#         self.dir_image = self.get_file_image(".dir")

#         self.load_images()

#     def load_images(self):
#         for ext in self.image_dict:
#             self.image_dict[ext] = self.get_file_image(ext)

#     def new_folder(self, parent_path, directory_entries, parent_iid, d_image):
#         for name in directory_entries:
#             item_path = os.path.join(parent_path, name)
#             if os.path.isdir(item_path):
#                 subdir_iid = self.filetreeview.insert(parent=parent_iid, index='end',
#                                          text=name,
#                                          image=d_image)
#                 try:
#                     subdir_entries = os.listdir(item_path)
#                     self.new_folder(parent_path=item_path,
#                            directory_entries=subdir_entries,
#                            parent_iid=subdir_iid,
#                            d_image=d_image)
#                 except PermissionError:
#                     pass
#             else:
#                 file_extension = os.path.splitext(name)[1].lower()
#                 file_image = self.get_file_image(file_extension)
#                 self.filetreeview.insert(parent=parent_iid,
#                             index='end',
#                             text=name,
#                             image=file_image)

#     def get_file_image(self, file_extension):
#         # Helper method to get the image based on the file extension
#         image_path = self.image_dict.get(file_extension, self.image_dict[".dir"])
#         return ImageTk.PhotoImage(Image.open(image_path))

#     def on_treeview_select(self, event):
#         print("inside on_treeview_select")
#         item = self.filetreeview.selection()[0]
#         item_text = self.filetreeview.item(item, "text")
#         item_path = os.path.join(self.get_folder_path(item), item_text)
#         print(item_path)
#         if os.path.isfile(item_path):
#             with open(item_path, 'r') as file:
#                 content = file.read()
#                 self.function.delete("1.0", "end")
#                 self.function.insert("end", content)

#     def get_folder_path(self, item):
#         # Helper method to get the folder path of an item in the treeview
#         print("inside get_folder_path")
#         parent = self.filetreeview.parent(item)
#         if parent == '':
#             return ""
#         else:
#             return os.path.join(self.get_folder_path(parent), self.filetreeview.item(parent, "text"))

#     def open_file_dialog(self):
#         src_folder_path = None
#         src_folder_path = filedialog.askdirectory(title="Select the Source Code Location")
#         start_path = os.path.expanduser(src_folder_path)
#         start_dir_entries = os.listdir(start_path)
#         parent_iid = self.filetreeview.insert(parent='',
#                              index='0',
#                              text=src_folder_path,
#                              open=True,
#                              image=self.dir_image)
#         self.new_folder(parent_path=start_path,
#            directory_entries=start_dir_entries,
#            parent_iid=parent_iid,
#            d_image=self.dir_image)
#         print(src_folder_path)

# if __name__ == "__main__":
#     root = Tk()
#     obj = Automation(root)
#     root.mainloop()
