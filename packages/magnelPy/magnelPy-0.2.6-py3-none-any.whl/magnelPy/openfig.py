from tkinter import filedialog
from tkinter import *
import pickle
import matplotlib.pyplot as plt
import os

cwd=os.getcwd()
print(cwd)


root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = cwd,title = "Select file")

fig_handle = pickle.load(open(root.filename,'rb'))
print(fig_handle)
print('blabalba')
print(type(fig_handle))
plt.show()