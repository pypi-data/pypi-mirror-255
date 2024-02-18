#!/usr/bin/env python
# coding: utf-8

# In[12]:
import sys
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
import AIUT_Core_Java as AIUT_Java
import AIUT_Core_CSharp as AIUT_CSharp
import AIUT_Core_Python as AIUT_Python
from PIL import ImageTk, Image
import multiprocessing
import sub
import time
# In[1]:


lblKey, txtKey, lblFunction, txtFunction, lblLocation, txtLocation = None, None, None, None, None, None

class Automation:
    def __init__(self, root):
        # messagebox.showinfo("Welcome","Please Enter only the required Java CLASSES for the program.\nDo not enter more than 1 Java Program.\n Ensure you have your program in the src directory.\n Each class should be in a different .java file\nLocation has to be written from the root directory not cwd.\nUse '\\' to separate the directories.\nThe location refers to the location of the generated unit test cases.\nDo not enclose the location in quotations.\nYour last directory should be 'test\\' ")

        width = 900
        height = 540
        self.root = root
        self.root.title("AIUTGen")

        screen_width = root.winfo_screenwidth()  # Width of the screen
        screen_height = root.winfo_screenheight()  # Height of the screen

        # Calculate Starting X and Y coordinates for Window
        x = (screen_width / 2) - (width / 2)
        y = (screen_height / 2) - (height / 2)

        self.root.geometry('%dx%d+%d+%d' % (width, height, x, y))

        # ----X-----
        # global lblKey,txtKey,lblFunction,lblLocation,txtLocation
        global lblFunction, txtKey, txtLocation, src_file_path, btngencc, lblTest, txtCode, progressbar
        global btnload, btnsubmit,btngencc
        self.api_key = StringVar()
        self.function = StringVar()
        self.location = StringVar()
        self.code = StringVar()
        self.opt_TF = None
        self.img = ImageTk.PhotoImage(Image.open(f"AIUT4.png"))

        lbltitle = Label(self.root, text="Artificial Intelligence Based Unit Test Case Generator (AIUTGen)", fg="blue",
                         font=("Sans Serif", 16, "bold"), padx=6, pady=42)
        lbltitle.place(x=210, y=7)

        DataFrame = Frame(root)
        DataFrame.place(x=0, y=75, width=900, height=500)

        # frame = Frame(DataFrame, width=200, height=70)
        # frame.pack()
        # frame.place(anchor='center', relx=0.3, rely=0.2)

        lblimage = Label(self.root, image=self.img)
        lblimage.place(x=7, y=7)

        lblFunction = ttk.Label(DataFrame, text="Source Code")
        lblFunction.place(x=200, y=60)

        self.function = Text(DataFrame, font=("MS Sans Serif", 10), width=40, height=22)
        self.function.place(x=200, y=80)

        test_framework = ["Select Test Framework", "JUnit(Java)", "NUnit(C#)", "MSTest(C#)", "UnitTest(Python)"]
        self.n = StringVar(DataFrame)
        self.n.set(test_framework[0])

        opt_test_framework = ttk.OptionMenu(DataFrame, self.n, *test_framework, command=self.callback)
        opt_test_framework.place(x=40, y=90)

        self.btnload = ttk.Button(DataFrame, command=self.open_file_dialog, text="Select Source File", width=20)
        self.btnload.place(x=40, y=120)
        self.btnload.config(state="disabled")

        self.btnsubmit = ttk.Button(DataFrame, command=self.submit, text="Generate Test Cases", width=20)
        self.btnsubmit.place(x=40, y=150)
        self.btnsubmit.config(state="disabled")

        self.btngencc = ttk.Button(DataFrame, command=self.generate_code_coverage, text="Get Code Coverage", width=20)
        self.btngencc.place(x=40, y=180)
        self.btngencc.config(state="disabled")

        btnclear = ttk.Button(DataFrame, command=self.clear, text="Clear", width=20)
        btnclear.place(x=40, y=210)

        btnexit = ttk.Button(DataFrame, command=self.close_app, text="Exit", width=20)
        btnexit.place(x=40, y=240)

        lblTest = ttk.Label(DataFrame, text="Generated Test Cases")
        self.code = Text(DataFrame, font=("MS Sans Serif", 10), width=50, height=22)

        lblTest.place(x=500, y=60)
        self.code.place(x=500, y=80)

        self.progressbar = ttk.Progressbar(DataFrame, mode="indeterminate")
        #progressbar.place(x=40, y=350, width=130)

        # self.DataFrameRight=Frame(root)
        # self.DataFrameRight.place(x=520,y=110,width=500,height = 600)

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

    def process_file(self, file_path):
        # Implement your file processing logic here
        # For demonstration, let's just display the contents of the selected file
        try:
            with open(file_path, 'r') as file:
                file_contents = file.read()
                self.function.delete("1.0", "end")
                self.function.insert("end", file_contents)
            self.src_file_path = file_path
        except Exception as e:
            pass

    def open_file_dialog(self):
        if (self.opt_TF)!=None:
            if (self.opt_TF)=="JUnit":
                file_path = filedialog.askopenfilename(title="Select a File",
                                                   filetypes=[("Java files", "*.java"), ("All files", "*.*")])
            elif (self.opt_TF)=="NUnit" or (self.opt_TF)=="MSTest":
                file_path = filedialog.askopenfilename(title="Select a File",
                                                   filetypes=[("CSharp files", "*.cs"), ("All files", "*.*")])
            elif (self.opt_TF)=="UnitTest":
                messagebox.showerror("Error", "Python to be integrated!")
                return
                file_path = filedialog.askopenfilename(title="Select a File",
                                                   filetypes=[("Python files", "*.py"), ("All files", "*.*")])
            self.process_file(file_path)
            self.btnsubmit.config(state="enabled")
        else:
            messagebox.showerror("Error", "Please Select Test Framework!")
            return

    def submit(self):
        global lblFunction, txtFunction, txtKey, txtLocation, code_base_location
        self.code.delete("1.0", "end")
        if self.function == "":
            messagebox.showerror("Error", "Enter a valid java program")
        else:
            print("IN SUBMIT")
            messagebox.showinfo("Success!", "Generating Test Cases. Please wait for sometime")
            print(self.function.get("1.0", END))
            if (self.opt_TF) == "JUnit":
                self.progressbar.place(x=40, y=350, width=130)
                #self.progressbar.start()
                code = AIUT_Java.generate_unit_cases(self.src_file_path)
                #self.progressbar.stop()
            elif (self.opt_TF) == "NUnit" or (self.opt_TF) == "MSTest":
                self.progressbar.place(x=40, y=350, width=130)
                #self.progressbar.start()
                #code = AIUT_CSharp.generate_unit_cases(self.src_file_path, self.opt_TF)
                #self.progressbar.stop()
                code = self.queue_loop(self.src_file_path, self.opt_TF)
                print(code)
            # if code != False:
            #     self.btngencc.config(state="enabled")
            #     # print(code)
            #     # print(code[0][0])
            #     # print(code[0][1])
            #     # print(code[2])
            #     # print(code[1].code_base_location)
            #     code_base_location = code[1]
            #     # lblTest=ttk.Label(self.DataFrameRight,text="Generated Test Cases")
            #     # lblTest.grid(row=1,column=0)
            #
            #     # self.code=Text(self.DataFrameRight,font=("MS Sans Serif",10),width=50,height=22)
            #     # self.code.grid(row=2,column = 0)
            #
            #     # lblTest.place(x=500,y=60)
            #     # self.code.place(x=500,y=80)
            #
            #     objFile = open(code[0][0], "r+")
            #     gen_code = objFile.read()
            #
            #     maxlen = len(gen_code)
            #     charac = 0
            #     while charac != maxlen:
            #         if gen_code[charac] == '\n':
            #             self.code.insert("end", "\n")
            #         else:
            #             self.code.insert("end", gen_code[charac])
            #         charac += 1
            # else:
            #     messagebox.showinfo("Error!", "Error Generating Test Cases. Please retry!")

    def clear(self):
        global lblKey, txtKey, lblFunction, txtFunction, txtLocation
        self.function.delete("1.0", "end")
        self.code.delete("1.0", "end")
        self.btngencc.config(state="disabled")
        self.btnsubmit.config(state="disabled")
        self.btnload.config(state="disabled")

    def generate_code_coverage(self):
        if (self.opt_TF) == "JUnit":
            AIUT_Java.execute_test_cases(code_base_location)
        elif (self.opt_TF) == "NUnit(C#)":
            AIUT_CSharp.AIUT_Java.execute_test_cases(code_base_location)

    # def loop(self, a, b):
    #     # Will just sleep for 3 seconds.. simulates whatever processing you do.
    #     #time.sleep(3)
    #     code = AIUT_CSharp.generate_unit_cases(a, b)
    #     return

    def check_status(self, p):
        """ p is the multiprocessing.Process object """
        if p.is_alive():  # Then the process is still running
            print("Process Running!")
            root.after(200, lambda p=p: self.check_status(p))  # After 200 ms, it will check the status again.
        else:
            print("Process Completed!")
            self.progressbar.stop()
            return "Done"

    def queue_loop(self,a,b):
        p = multiprocessing.Process(target=sub.loop,
                                    args=(a, b))
        # You can pass args and kwargs to the target function like that
        # Note that the process isn't started yet. You call p.start() to activate it.
        p.start()
        self.progressbar.start()
        result = self.check_status(p)  # This is the next function we'll define.
        return result


    def close_app(self):
        sys.exit()


if __name__ == "__main__":
    root = Tk()
    obj = Automation(root)
    root.mainloop()
