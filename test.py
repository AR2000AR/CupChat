try:
    from Tkinter import *
except:
    from tkinter import *
b=""
def c(a):
    b=e.get()
    print(b)
    

fen = Tk()
e = Entry(fen)
e.bind('<Return>',c)
e.pack()
fen.mainLoop()
