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
from VerticalScrolledFrame import *
#Definition des variables globals=================
global wrong,id_status,fen,client,config,stop
id_status=False  #variable de verification de connection
stop=False
wrong=0
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
        
        with open("Data/Client/config.cfg","w") as f:
            f.write("bool;LOG;True\nint;PORT;51648\nstr;SERVEUR;172.18.144.187\n#0 : Night 1 : Day\nint;THEME;0")
            f.close()
    config = Config("Data/Client/config.cfg")
    log = Log("Data/Client/log.txt",config.configDic["LOG"],mode=LOG_REPLACE)
    config.setLog(log)
    setdefaulttimeout(2)

    if config.configDic["THEME"]==0:
        theme=["#60636d",'#edf0f9','Data/Client/image/cup-nuit.gif',"Data/Client/image/roue.jpg"]
    elif config.configDic["THEME"]==1:
        theme=["white","black",'Data/Client/image/cup-jour.gif',"Data/Client/image/roue.jpg"]

    #Prépare le chiffrement
    config.rsa = Crypto()

    return config,theme

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
        bouton_valider.configure(state=DISABLED)
        bouton_créer.configure(state=DISABLED)
        bouton_quit.configure(state=DISABLED)
    
    def id_create():
        global wrong,config
        auth(True)
    def id_connect(bob=""):
        global wrong
        auth(False)

    def identification(new):
        global wrong,id_status
        #recevoir la confirmation du serveur
        msg=reciveMsg(client,2048,theType=str)
        msg=config.rsa.decrypt(msg)
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
                config.log.write("INFO",'conection reussi !')
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
        login=frame_login.get()
        password=frame_password.get()

        config.log.write("INFO","Tentative d'identification...")
        if not login or not password :
            wrong=3
            id_status=False
            fen.destroy()
        else:
            if new==True:
                client.send(bytes(str(config.rsa.encrypt('<|ACCOUNT|>;<|CREATE|>;'+frame_login.get()+";"+frame_password.get())),"UTF-8"))
                fen.destroy()
                password=""
                identification(new)    
            elif new==False:
                client.send(bytes(str(config.rsa.encrypt('<|ACCOUNT|>;<|AUTH|>;'+frame_login.get()+";"+frame_password.get())),"UTF-8"))    
                fen.destroy()
                password=""
                identification(new)
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

    fen = build_fen("Connection",theme)
    fen.minsize(width=650, height=550)
    gif = def_gif(fen, filename='Data/Client/image/gif-nuit.gif', speed=40)
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
                bouton_quit = Button(fen, text="Quitter",command=fen.destroy,relief=FLAT,bg=theme[0],activebackground=theme[0],bd=0,font="40")
                bouton_quit.pack()
                bouton_quit.place(anchor=SE,relx=1.0, rely=1.0)
                config.log.write("ERREUR",'la connexion a échouée avec le serveur')
                fen.mainloop()
                return False
        else:
            config.log.write("ERREUR",'la connexion a échouée avec le serveur')
            return False
        
    client.send(b'<|CONNECTION|>;'+bytes(config.rsa.getPublicKey(),"UTF-8"))
    try:
        msg = reciveMsg(client,1024,theType=str)
        msg=msg.split(";")
        if msg[0] == "<|CONNECTION|>":
            config.rsa.setPublicKey(msg[1])
    except:
        config.log.write("ERREUR",'le serveur à mit trop de temps à répondre')
        return False
         
    #Si la connection a réusie=============================================================================
    tmp.pack_forget()
    #titre principal page d'accueil et logo
    try:
        logo= PhotoImage(file=theme[2])
        titre= Label(fen, text="CupChat", bg=theme[0],fg=theme[1],font=('Helvetica','80','bold'),image=logo, compound =LEFT)
    except:
        titre= Label(fen, text="CupChat", bg=theme[0],fg=theme[1],font=('Helvetica','80','bold'))
    titre.pack()
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
    frame_espace1=Frame(fbouton, pady=5, bg=theme[0])
    frame_espace1.pack()
    frame_espace2=Frame(fbouton, pady=5, bg=theme[0])
    frame_espace2.pack()
    #bouton pour se connecter
    bouton_valider = Button(frame_espace1,text="Connection",command=id_connect, relief=FLAT, width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
    bouton_valider.pack()
    bouton_valider.bind('<Enter>',hover_v)
    bouton_valider.bind('<Leave>',leave_v)
    #bouton pour créer un compte 
    bouton_créer = Button(frame_espace2,text="Inscription",command=id_create,relief=FLAT,width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
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
    global fen,config,client,reception_msg

    def send_message(bob=''):
        global client
        if len(send.get())>0:
            client.send(bytes(str(config.rsa.encrypt('<|MESSAGE|>;'+login+';'+send.get())),"UTF-8"))
            send.delete(0,END)#Efface le contenu du widget Entry
    
    fen=build_fen("",theme)
    fen.minsize(width=600, height=500) 
    #panneau latéral  
    paneau_lateral= Frame(fen, bg="#3e4047",width=70)
    paneau_lateral.pack(fill='y',side=LEFT)
    #espace pour le nom du serveur
    paneau_serv= Frame(paneau_lateral,bg="#3e4047",width=70)
    paneau_serv.pack(fill='y',side=LEFT) 
    # bouton des option
    try:
        #tente de mettre l'image
        roue= PhotoImage(file=theme[3])
        cadre_roue= Frame(paneau_lateral, bg="#3e4047")
        cadre_roue.pack(side=BOTTOM,fill='x')
        cadre_roue1= Label(cadre_roue, bg="#3e4047",text="option",fg=theme[1],font=("MV-Boli","11","bold"),pady=6,padx=7,image=roue)
        cadre_roue1.pack(side=RIGHT)
    except:
        cadre_roue= Frame(paneau_lateral, bg="#3e4047")
        cadre_roue.pack(side=BOTTOM,fill='x')
        cadre_roue1= Label(cadre_roue,bg="#3e4047",text="option",fg=theme[1],font=("MV-Boli","11","bold"),pady=6,padx=7)
        cadre_roue1.pack(side=RIGHT)
    #cadre des messages 
    cadre_principal= Frame(fen, bg="pink",width=500)
    cadre_principal.pack(expand=1, fill='both',side=LEFT)
    #envoi des message
    value = StringVar().set("")        
    #cadre de l'envoie des message
    cadre_message= Frame(cadre_principal, bg=theme[0],pady=12,padx=12)
    cadre_message.pack(side=BOTTOM,fill='x' )
    cadre_message1= Frame(cadre_principal, bg=theme[0],pady=12,padx=12) 
    cadre_message1.pack(side=BOTTOM,fill='x' )
    bouton_envoyer= Button(cadre_message1, bg="#747987",text="Envoyer",fg=theme[1],font=("MV-Boli","11","bold"),pady=6,padx=7,command=send_message, relief=FLAT,activebackground="#747987", bd=0)#,image=fléche    
    bouton_envoyer.pack(side=RIGHT)
    send = Entry(cadre_message1, textvariable=value,relief=FLAT,font=("MV-Boli","15"),bg='#747987', width=30)  
    send.pack(side=RIGHT,fill='both',expand=1)
    #envoi des message
    send.bind('<Return>', send_message)
    #cadre de l'historique
    cadre_history= VerticalScrolledFrame(cadre_principal, bg=theme[1])
    cadre_history.pack(side=BOTTOM,fill='both',expand=1)
    reception_msg = thread_message(cadre_history,client,login,theme)
    reception_msg.start()
    #envoie d'une demande d'historique au serveur
    client.send(bytes(str(config.rsa.encrypt('<|HISTORIQUE|>',"UTF-8"))))
    fen.mainloop()
#CLASSES==========================================
class thread_message(threading.Thread):
    def __init__(self,cadre_history,client,login,theme):
        threading.Thread.__init__(self)
        self.stop=False
        self.frame=cadre_history
        self.frame.inner.configure(bg='red')
        self.frame.canvas.configure(bg=theme[1])
        self.client=client
        self.login=login
        self.i=0
        print(login)

    def run(self):
        while self.stop==False:
            try:
                msg=reciveMsg(client,2048,theType=str)
            except:
                self.stop=True
                
            if self.stop==True:
                break
            msg=config.rsa.decrypt(msg)
            a=msg.split(";")
            if a[0]=="<|MESSAGE|>":
                a=msg.split("<|MESSAGE|>")
                del a[0]
                for line in a:
                    print(line)
                    content=line.split(";")
                    del content[0]
                    print(content)
                    if content[0]==self.login:
                        Label(self.frame,text="You : "+content[1], justify='right',font=("Corbel","9","bold")).grid(row=self.i,column=0,sticky=E)
                    else:
                        Label(self.frame,text=content[0]+" : "+content[1],font=("Corbel","9","bold")).grid(row=self.i,column=0,sticky=W)
                    self.frame.update_idletasks()
                    self.i = self.i+1
#PROGRAMME PRINCIPAL==============================
config,theme = init()
while id_status==False and stop == False:
    #créer une boucle tant que le client n'arrive pas à se connecter
    client,login=login_screen(theme)
    if client == False:
        clean_end()
        break

if client != False and stop == False:
    chat_screen(theme,login)
