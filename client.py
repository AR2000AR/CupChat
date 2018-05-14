#CupChat Client app##########
#By Gwenaël Egron           #
#Rewriten by Rémi Audrezet  #
#############################
#IMPORTATIONS DES LIBRAIRIES======================
from tkinter import *
from tkinter.messagebox import *
from tkinter.simpledialog import *
from time import sleep
import threading,sys,os
#IMPORTATION DES MODULES==========================
from RSA import *
from tools import *
from socket import *
from logger import *
from socketTools import *
from configuration import *
from ScrollText import *
#Definition des variables globals=================
global wrong,id_status,fen,client,config,stop,fen_o,police_size
id_status=False  #variable de verification de connection
stop=False
wrong=0
#DEFINITION DES CLASSES============================
class def_gif(Label):
        def __init__(self, master, filename, speed): #définit speed
                self.speed = speed
                #speed: le delay en milliseconde entre chaques images
                self.frames = [] # liste permettant de stocker les images du gif
                i = 0
                while True:
                    try:
                        p = PhotoImage(file=filename, format="gif - {}".format(i))
                        #prend les images du gif
                    except TclError:
                        break #la boucle s'arrête
                    self.frames.append(p) #on stock dans la liste les images
                    i += 1
                super().__init__(master, image=self.frames[0])
                self.frame = 0
                self.num_frames = i
                self.after(self.speed, self._animate) #fait attendre (vitesse) et appelle la fonction animate

        def _animate(self):
            self.frame = (self.frame + 1) % self.num_frames
            # permet de faire une sorte de boucle allant de 1 à nombre max d'image
            self['image'] = self.frames[self.frame] #intégre l'image dans les options
            self.after(self.speed, self._animate) #fait attendre (vitesse) et appelle la fonction animate
#=================================================
class thread_message(threading.Thread):
    def __init__(self,cadre_history,client,login,theme):
        threading.Thread.__init__(self)
        self.stop=False
        self.frame=cadre_history
        self.client=client
        self.login=login
        self.i=0
        self.frame.tag_add('right',END,END)
        self.frame.tag_config('right',justify=RIGHT)
        self.frame.tag_add('left',END,END)
        self.frame.tag_config('left',justify=LEFT)
        self.frame.tag_add('login',END,END)
        self.frame.tag_config('login',underline=1)
        self.frame.tag_config('login',font=("Corbel",config.configDic["POLICE"]+1,"bold"))
        self.frame.tag_config('login',foreground=theme[2])
        self.frame.configure(state=DISABLED)
        
    def run(self):
            
        while self.stop==False:
            try:
                msg=reciveMsg(client,2048,theType=bytes)
            except:
                self.stop=True

            if self.stop==True:
                break
            if msg != b'':
                    msg=str(config.rsa.decrypt(msg))[2:-1]
                    a=msg.split(";")
                    if a[0]=="<|MESSAGE|>":
                        a=msg.split("<|MESSAGE|>")
                        del a[0]
                        for line in a:
                            content=line.split(";")
                            del content[0]
                            self.frame.configure(state=NORMAL)
                            if content[0]==self.login:
                                    self.frame.insert(END,"Vous :"+"\n",['right','login'])
                                    del content[0]
                                    self.frame.insert(END,fusion(content,';')+"\n"+"\n",['right'])

                            else:
                                    self.frame.insert(END,content[0]+" :"+"\n",['left','login'])
                                    del content[0]
                                    self.frame.insert(END,fusion(content,';')+"\n"+"\n",['left'])
                            self.frame.configure(state=DISABLED)
                            self.frame.yview(MOVETO,1)
                            self.frame.update_idletasks()
                    else:
                        pass
             
#DEFINITION DES FONCTIONS=========================
def init():
    if os.path.exists("Data/Client/config.cfg") and os.path.isfile("Data/Client/config.cfg"):
        pass
    else:
        try:
            os.makedirs("Data")
        except FileExistsError:
            pass
        try:
            os.makedirs("Data/Client")
        except FileExistsError:
            pass

    config = Config("Data/Client/config.cfg")
    log = Log("Data/Client/log.txt",config.configDic["LOG"],mode=LOG_REPLACE)
    config.setLog(log)
    setdefaulttimeout(2)

    if config.configDic["THEME"]==0:
        theme=["#60636d",'#edf0f9','#3d436d','Data/Client/image/cup-nuit.gif',"Data/Client/image/roue.gif","Data/Client/image/gif-jour.gif"]
    elif config.configDic["THEME"]==1:
        theme=["white","black",'#57609b','Data/Client/image/cup-jour.gif',"Data/Client/image/roue.gif","Data/Client/image/gif-jour.gif"]

    #Prépare le chiffrement
    config.rsa = Crypto()

    return config,theme

def fusion(liste,sep):
    tmp=liste[0]
    del liste[0]
    try:
        for item in liste:
            tmp=tmp+sep+item
    except:
        pass
    return tmp

def clean_end():
    global fen,client,reception_msg,config,stop
    config.log.write("EXIT","Interception de la fermeture de la fenetre" )
    try:
        client.close()
    except:
        pass
    try:
        reception_msg.stop=True
    except:
        pass
    fen.destroy()
    stop=True

def build_fen(titre,theme):
    fen= Tk()
    fen.title(" CupChat "+titre,)
    fen['bg']=theme[0]

    #change l'icone
    try:
        if sys.platform=='win32':
            fen.iconbitmap('Data/Client/image/icone.ico')
        elif sys.platform=='linux2':
            fen.iconbitmap('Data/Client/image/icone.xbm')
    except:
        pass

    fen.protocol("WM_DELETE_WINDOW", clean_end)
    return fen

def login_screen(theme):
    global wrong,config,fen,login

    def disable():
        try:
                bouton_valider.configure(state=DISABLED)
                bouton_créer.configure(state=DISABLED)
                bouton_quit.configure(state=DISABLED)
        except NameError:
                pass

    def id_create():
        global wrong,config
        auth(True)
    def id_connect(bob=""):
        global wrong
        auth(False)
    def id_connect_memo(bob=""):
        global wrong
        auth("Memo")

    def identification(new):
        global wrong,id_status
        #recevoir la confirmation du serveur
        msg=reciveMsg(client,1024,theType=bytes)
        if msg != b'':
                msg=str(config.rsa.decrypt(msg))[2:-1]
                msg=msg.split(";")
                if new==True:
                    if msg[1]=="DONE":

                        config.log.write("INFO",' compte créer avec succée')
                        showinfo('CupChat Connection','votre compte à été créer !')
                        id_status=False

                    elif msg[1]=="EXIST":
                        config.log.write("ERREUR",'compte deja existant')
                        showwarning('CupChat Connection','Désolé ce compte exite déja')
                        wrong=1
                        id_status=False
                else:
                    if msg[1]=="<|ACCEPTED|>":
                        config.log.write("INFO",'connection reussi !')
                        id_status=True

                    elif msg[1]=="<|REJECTED|>":
                        config.log.write("ERREUR","Erreur de mot de passe, ou de pseudo")
                        wrong=2
                        id_status=False
                    else :
                        config.log.write("ERREUR","probléme avec le serveur")

    def auth(new):
        global wrong,login
        wrong=0
        disable()
        if new=="Memo" and wrong==0:
            login=config.configDic["LOGIN"]
            password=config.configDic["PASSWORD"]
        else:
            login=frame_login.get()
            password=frame_password.get()

        try:
            if Var.get()==1:
                config.setConf("str","LOGIN",login)
                config.setConf("str","PASSWORD",password)
        except NameError:
                pass

        config.log.write("INFO","Tentative d'identification...")
        if not login or not password :
            wrong=3
            id_status=False
            fen.destroy()
        else:
            if new==True:
                client.send(config.rsa.encrypt(bytes('<|ACCOUNT|>;<|CREATE|>;'+login+";"+password,"UTF-8")))
                fen.destroy()
                password=""
                identification(new)
            elif new==False:
                client.send(config.rsa.encrypt(bytes('<|ACCOUNT|>;<|AUTH|>;'+login+";"+password,"UTF-8")))
                fen.destroy()
                password=""
                identification(new)
            elif new=="Memo" and wrong==0:
                client.send(config.rsa.encrypt(bytes('<|ACCOUNT|>;<|AUTH|>;'+login+";"+password,"UTF-8")))
                fen.destroy()
                password=""
                identification(False)

    #effet visuel
    def hover_v(event):
        bouton_valider.configure(bg="#57609b")
    def hover_c(event):
        bouton_créer.configure(bg="#57609b")
    def leave_v(event):
        bouton_valider.configure(bg="#525a8e")
    def leave_c(event):
        bouton_créer.configure(bg="#525a8e")
    #======================================================================================================
    fen = build_fen("Connection",theme)
    fen.minsize(width=650, height=550)
    gif = def_gif(fen, filename=theme[5], speed=40)
    gif.pack()
    fen.focus_force()
    fen.update_idletasks()
    try:
        config.log.write("INFO",'Tentative de connexion au serveur...')
        client = clientConnect(config.configDic["SERVEUR"],config.configDic["PORT"],config.log)
    except:
        retry=askyesno("CupChat Connection","Impossible de se connécter à "+config.configDic["SERVEUR"]+"\nUtiliser une autre addresse ?")
        if retry == True:
            try:
                client = clientConnect(askstring("CupChat Connection","IP"),askintegrer("CupChat Connection","Port"))
            except:
                fen.minsize(width=300, height=325)
                titre_erreur= Label(fen, text="Probléme de connexion avec le serveur",bg=theme[0],fg='Red', font=("MV-Boli","bold"),justify=CENTER )
                titre_erreur.pack()
                titre_erreur.place(anchor=N ,relx=0.5, rely=0.1)
                bouton_quit = Button(fen, text="Quitter",command=clean_end,relief=FLAT,bg=theme[0],activebackground=theme[0],bd=0,font="40")
                bouton_quit.pack()
                bouton_quit.place(anchor=SE,relx=1.0, rely=1.0)
                config.log.write("ERREUR",'la connexion a échouée avec le serveur')
                fen.mainloop()
                return False
        else:
            config.log.write("ERREUR",'la connexion a échouée avec le serveur')
            return False

    try:
        while True:
                msg = reciveMsg(client,1024,theType=str)
                msg=msg.split(";")
                if msg[0] == "<|CONNECTION|>":
                    config.rsa.setPublicKey(msg[1])
                    client.send(b'<|CONNECTION|>;'+config.rsa.getPublicKey())
                    break
    except:
        config.log.write("ERREUR",'l\'échange de clef n\'a pas été fait')
        return False

    #Si la connection a réusie=============================================================================
    gif.pack_forget()
    #titre principal page d'accueil et logo

    if wrong==0 and not config.configDic["LOGIN"]=="False" and not config.configDic["PASSWORD"]=="False":
        id_connect_memo()
        return client,login
    else:
        logo= PhotoImage(file=theme[3])
        titre= Label(fen, text="CupChat", bg=theme[0],fg=theme[1],font=('Helvetica','80','bold'),image=logo, compound =LEFT)
        titre.place(anchor=N ,relx=0.5, rely=0.1)
        #frame contenant la partie de l'identification
        fa= Frame(fen, bg=theme[0])
        fa.pack()
        fa.place(anchor=N ,relx=0.5, rely=0.4)
        #partie "identification"
        titre_login= Label(fa, text="Identifiant :",bg=theme[0],fg=theme[1],font=("MV-Boli"),justify=LEFT,width= 30)
        titre_login.pack()
        fa3= Frame(fa, bg="#4b4e56", pady=2, padx=2)
        fa3.pack()
        value = StringVar().set("")
        frame_login = Entry(fa3, textvariable=value,width=30,font=("MV-Boli"),relief=FLAT)
        frame_login.focus_force()
        frame_login.pack()
        espace= Frame(fa, bg=theme[0], height=40)
        espace.pack()
        #le "mot de passe" en dessous
        titre_password= Label(fa, text="Mot de passe :",bg=theme[0],fg=theme[1],font=('MV-Boli'),justify=LEFT, width= 30 )
        titre_password.pack()
        fa2= Frame(fa, bg="#4b4e56", pady=2, padx=2)
        fa2.pack()
        value = StringVar().set("")
        frame_password = Entry(fa2, textvariable=value,show="*",width=30,font=('MV-Boli'),relief=FLAT)
        frame_password.bind("<Return>",id_connect)
        frame_password.pack()
        #en cas d'ereur de connexion affiche un message rouge
        if wrong==1:
            titre_erreur= Label(fa,text="Désolé ce compte exite déja",bg=theme[0],fg='Red',font=("MV-Boli,bold"),justify=CENTER,width= 30)
        if wrong==2:
            titre_erreur= Label(fa,text="vous vous êtes trompé de mot de passe\nou de pseudo",bg=theme[0],fg='Red',font=("MV-Boli,bold"),justify=CENTER,width= 30)
        if wrong==3:
            titre_erreur= Label(fa,text="remplissez les deux champs",bg=theme[0],fg='Red',font=("MV-Boli,bold"),justify=CENTER,width= 30)
        if wrong!=0:
            titre_erreur.pack()
        #frame des boutons de connection et de création de compte
        fbouton= Frame(fa, bg=theme[0], pady=30)
        fbouton.pack()
        fbouton_espace= Frame(fbouton, bg=theme[0], pady=20)
        fbouton_espace.pack()
        #frames pour espacer entre les boutons espace entre les boutons
        frame_espace2=Frame(fbouton, pady=5, bg=theme[0])
        frame_espace2.pack()
        frame_espace1=Frame(fbouton, pady=5, bg=theme[0])
        frame_espace1.pack()
        frame_espace3=Frame(fbouton, pady=5, bg=theme[0])
        frame_espace3.pack()
        #bouton pour se connecter
        bouton_valider = Button(frame_espace1,text="Connection",command=id_connect, relief=FLAT, width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
        bouton_valider.pack()
        bouton_valider.bind('<Enter>',hover_v)
        bouton_valider.bind('<Leave>',leave_v)
        #case à cocher pour memoriser
        Var = IntVar()
        memo  = Checkbutton(frame_espace2, text='Se souvenir de moi',variable=Var,bg=theme[0],activebackground=theme[0])
        memo.pack()
        #bouton pour créer un compte
        bouton_créer = Button(frame_espace3,text="Inscription",command=id_create,relief=FLAT,width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
        bouton_créer.pack()
        bouton_créer.bind('<Enter>',hover_c)
        bouton_créer.bind('<Leave>',leave_c)
        #bouton pour quitter
        bouton_quit = Button(fen, text="Quitter",command=clean_end,relief=FLAT,bg=theme[0],activebackground=theme[0],bd=0, font="40")
        bouton_quit.pack()
        bouton_quit.place(anchor=SE,relx=1.0, rely=1.0)
        fen.mainloop()
        return client,login
#-------------------------------------------------
def chat_screen(theme,login):
    global fen,config,client,reception_msg,fen_o

    def send_message(bob=''):
        global client,login
        if len(send.get())>0:
            client.send(config.rsa.encrypt(bytes('<|MESSAGE|>;'+login+';'+send.get(),"UTF-8")))
            send.delete(0,END)#Efface le contenu du widget Entry

    #page des options==
    def fen_option(bob=''):
        #init
        global val,fen_o,config,reception_msg,val2,fen
        fen_o= Toplevel(fen)
        fen_o.title(" CupChat "+"Option")
        fen_o['bg']=theme[0]
        fen_o.minsize(width=300, height=300)
        fen_o.resizable(False,False)
        fen_o.focus_force()
        try:
            if sys.platform=='win32':
                fen_o.iconbitmap('Data/Client/image/roue.ico')
            elif sys.platform=='linux2':
                fen_o.iconbitmap('Data/Client/image/roue.ico')
        except:
            pass

        def gogogo():
            global fen_o,fen,val2
            #relance la fenetre principale
            fen_o.destroy()
            fen.mainloop()

        def save_option():
            global fen_o,val,fen,reception_msg
            config.setConf("int","THEME",val.get())
            if config.configDic["THEME"]==0:
                theme=["#60636d",'#edf0f9','#3d436d','Data/Client/image/cup-nuit.gif',"Data/Client/image/roue.gif"]
            elif config.configDic["THEME"]==1:
                theme=["white","black",'#57609b','Data/Client/image/cup-jour.gif',"Data/Client/image/roue.gif"]
            config.setConf("int","POLICE",val2.get())
            fen_o.destroy()
            fen.destroy()
            try:
                reception_msg.stop=True
            except:
                pass
            #rappel l'appli pour la mettre à jour
            chat_screen(theme,login)
        def restart():
            global fen_o,fen,stop,id_status,wrong
            clean_end()
            id_status=False
            stop=False
            wrong=0
            config.setConf("str","LOGIN","False")
            config.setConf("str","PASSWORD","False")

        def police(bob=''):
            global val2
            titre_test.configure(font=("MV-Boli",val2.get(),"bold"))
        #effet visuel
        def hover_s(event):
            bouton_save.configure(bg="#57609b")
        def leave_s(event):
            bouton_save.configure(bg="#525a8e")
        def hover_a(event):
            bouton_annuler.configure(bg="#57609b")
        def leave_a(event):
            bouton_annuler.configure(bg="#525a8e")
        def hover_d(event):
            bouton_deconnect.configure(bg="#8e1212")
        def leave_d(event):
            bouton_deconnect.configure(bg="#840f0f")

        frame_o=Frame(fen_o,bg=theme[0])
        frame_o.pack(anchor=NW,fill=BOTH,expand=1,pady=5,padx=5)
        #option switch jour nuit
        frame_theme1=Label(frame_o,fg=theme[1],font=("MV-Boli","11","bold"),text="Théme : ",bg=theme[0])
        frame_theme1.pack(anchor=NW)
        frame_theme=Frame(frame_o,bg=theme[0],pady=5,padx=5)
        frame_theme.pack(anchor=NW,fill=X)
        val = IntVar()
        val.set(config.configDic["THEME"])
        n = Radiobutton(frame_theme,width=10, variable=val,pady=3,offrelief=FLAT, text="Nuit",selectcolor="#2e3459",font=("","13","bold"), value=0,indicatoron=0,bg="#2e3459",fg='#edf0f9',relief=FLAT)
        n.pack(side=LEFT,expand=1)
        j = Radiobutton(frame_theme,width=10, variable=val,pady=3,offrelief=FLAT, text="Jour",selectcolor="#57609b",font=("","13","bold"), value=1,indicatoron=0,bg="#57609b",fg='#edf0f9',relief=FLAT)
        j.pack(side=LEFT,expand=1)
        #option taille du texte
        frame_barre=Frame(frame_o,bg=theme[0],pady=20)
        frame_barre.pack(fill=X)
        titre_barre=Label(frame_barre,fg=theme[1],font=("MV-Boli",'11',"bold"),text="Taille de la police :",bg=theme[0])
        titre_barre.pack(anchor=NW)
        val2 = IntVar()
        barre=Scale(frame_barre,bd=0,variable=val2,activebackground=theme[0],relief=FLAT, orient='horizontal',highlightthickness=0,from_=10, to=19,resolution=1, tickinterval=2,bg=theme[0],fg=theme[1],font=("MV-Boli","12","bold"),command=police )
        barre.pack(fill=X)
        frame_test=Frame(frame_o,bg=theme[0])
        frame_test.pack()
        titre_test=Label(frame_test,fg=theme[1],font=("MV-Boli",config.configDic["POLICE"],"bold"),text="Test",bg=theme[0])
        titre_test.pack(anchor=W)

        frame_bouton_option=Frame(frame_o,bg=theme[0])
        frame_bouton_option.place(anchor=SE,relx=1.0, rely=1.0)
        #bouton pour enregistrer
        bouton_save = Button(frame_bouton_option,text="Save",command=save_option, relief=FLAT,bg="#525a8e",fg='white',font="40",activebackground="#57609b",bd=0)
        bouton_save.pack(side=RIGHT)
        bouton_save.bind('<Enter>',hover_s)
        bouton_save.bind('<Leave>',leave_s)
        #bouton pour annuler
        frame_bouton1_option=Frame(frame_bouton_option,padx=4,bg=theme[0])
        frame_bouton1_option.pack(side=RIGHT,expand=1)
        bouton_annuler = Button(frame_bouton1_option, text="Annuler",command=gogogo, relief=FLAT,bg="#525a8e",fg='white',font="40",activebackground="#57609b",bd=0)
        bouton_annuler.pack()
        bouton_annuler.bind('<Enter>',hover_a)
        bouton_annuler.bind('<Leave>',leave_a)
        #bouton deconnexion
        frame_bouton2_option=Frame(frame_bouton_option,padx=4,bg=theme[0])
        frame_bouton2_option.pack()
        bouton_deconnect = Button(frame_bouton2_option, text="Deconnexion", relief=FLAT,bg="#840f0f",fg='white',font="40",activebackground="#8e1212",bd=0,command=restart)
        bouton_deconnect.pack()
        bouton_deconnect.bind('<Enter>',hover_d)
        bouton_deconnect.bind('<Leave>',leave_d)
        fen_o.mainloop()

    #appli principale=====
    fen=build_fen("",theme)
    fen.minsize(width=600, height=500)
    #panneau latéral
    paneau_lateral= Frame(fen, bg="#3e4047",width=70)
    paneau_lateral.pack(fill=Y,side=LEFT)
    #espace pour le nom du serveur
    paneau_serv= Frame(paneau_lateral,bg="#3e4047",width=70)
    paneau_serv.pack(fill=Y,side=LEFT)
    # bouton des option
    roue= PhotoImage(file=theme[4])
    cadre_option= Frame(paneau_lateral, bg="#3e4047")
    cadre_option.pack(side=BOTTOM,fill=X)
    boutton_option= Button(cadre_option, bg="#3e4047",text="option",fg=theme[1],font=("MV-Boli","11","bold"),pady=6,padx=7,image=roue,relief=FLAT,activebackground="#3e4047",bd=0,command=fen_option)
    boutton_option.pack(side=RIGHT)
    #cadre des messages
    cadre_principal= Frame(fen, bg="pink",width=500)
    cadre_principal.pack(expand=1, fill=BOTH,side=LEFT)
    #envoi des message
    value = StringVar().set("")
    #cadre de l'envoie des message
    cadre_message= Frame(cadre_principal, bg=theme[0],pady=12,padx=12)
    cadre_message.pack(side=BOTTOM,fill=X)
    cadre_message1= Frame(cadre_principal, bg=theme[0],pady=12,padx=12)
    cadre_message1.pack(side=BOTTOM,fill=X)
    bouton_envoyer= Button(cadre_message1, bg="#747987",text="Envoyer",fg=theme[1],font=("MV-Boli","11","bold"),pady=6,padx=7,command=send_message, relief=FLAT,activebackground="#747987", bd=0)#,image=fléche
    bouton_envoyer.pack(side=RIGHT)
    send = Entry(cadre_message1, textvariable=value,relief=FLAT,font=("MV-Boli","15"),bg='#747987', width=30)
    send.pack(side=RIGHT,fill=BOTH,expand=1)
    #envoi des message
    send.bind('<Return>', send_message)
    #cadre de l'historique
    cadre_history= ScrollText(cadre_principal,pady=10,padx=10,wrap=WORD,bd=0,bg=theme[0],fg='#b6bac4',font=("Corbel",config.configDic["POLICE"],"bold"))
    cadre_history.pack(side=BOTTOM,fill=BOTH,expand=1)
    reception_msg = thread_message(cadre_history,client,login,theme)
    reception_msg.start()
    #envoie d'une demande d'historique au serveur
    client.send(config.rsa.encrypt(bytes('<|HISTORIQUE|>',"UTF-8")))
    fen.mainloop()
    
#PROGRAMME PRINCIPAL==============================
config,theme = init()
while stop == False:
    while id_status==False and stop == False:
        #créer une boucle tant que le client n'arrive pas à se connecter
        client,login=login_screen(theme)
        if client == False:
            clean_end()
            break

    if client != False and stop == False:
        chat_screen(theme,login)
