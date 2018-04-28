from tkinter import *
#=================================================
class ScrollText(Text):
    def __init__(self,master,**kargs):
        self._frame = Frame(master)
        self._yScroll = Scrollbar(self._frame,orient=VERTICAL)
        Text.__init__(self,self._frame,**kargs,yscrollcommand=self._yScroll.set)
        self._yScroll["command"]=self.yview
        self.grid(row=0,column=0,sticky=N+S+E+W)
        self._yScroll.grid(row=0,column=1,sticky=N+S)
        self._frame.grid_rowconfigure(0, weight=1)
        self._frame.grid_columnconfigure(0, weight=1)
        self.grid = self._frame.grid
        self.pack = self._frame.pack

if __name__ == "__main__":
    theme=["#60636d",'#edf0f9','Data/Client/image/cup-nuit.gif',"Data/Client/image/roue.gif"]
    fen=Tk()
    T=ScrollText(fen,pady=10,padx=10,wrap=WORD,bd=0,bg=theme[0],fg=theme[1],font=("Corbel",13,"bold"))
    T.pack(fill='both',expand=1)
    
    login='noqui'
    content=['gnoqui','fcfgchgyvgyytggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg']
    content1=['goqui','fcfgcgyhdfhfdhhsdtsvgyytggggggggggggggggggggggggggggggggg']

    #definition des tags
    T.tag_add('right',END,END)
    T.tag_config('right',justify=RIGHT)
    T.tag_add('left',END,END)
    T.tag_config('left',justify=LEFT)
    T.tag_add('login',END,END)
    T.tag_config('login',underline=1)
    T.tag_config('login',font=("Corbel",13,"bold"))

    T.insert(END,"You :"+"\n",['right','login'])
    T.insert(END,content[1]+"\n",['right'])

    T.insert(END,content1[0]+" :"+"\n",['left','login'])
    T.insert(END,content1[1]+"\n",['left'])
    T.configure(state='disabled')
