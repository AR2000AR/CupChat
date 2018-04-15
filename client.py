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
from socket import *
from tools import *
from logger import *
from socketTools import *
from configuration import *
from VerticalScrolledFrame import *
#Definition des variables globals=================
global wrong,id_status,fen,client,config
id_status=False
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
        theme=["#60636d",'#edf0f9','Data/Client/image/cup-jour.gif',"Data/Client/image/roue.jpg"]
    elif config.configDic["THEME"]==1:
        theme=["white","black",'Data/Client/image/cup-jour.gif',"Data/Client/image/roue.jpg"]

    return config,theme

def clean_end():
    global fen,client,reception_msg,config
    config.log.write("EXIT","Interception de la fermeture de la fenetre" )
    try:
        client.close()
    except:
        pass
    try:
        reception_msg.stop=True
    except:
        pass
    sleep(1)
    fen.destroy()

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
    global wrong,config,fen

    def disable():
        bouton_valider.configure(state=DISABLED)
        bouton_créer.configure(state=DISABLED)
        bouton_quit.configure(state=DISABLED)
    
    def id_create():
        global wrong,config
        wrong=auth(True)
    def id_connect(bob=""):
        global wrong
        wrong=auth(False)

    def identification(new):
        global wrong,id_status
        #recevoir la confirmation du serveur
        msg=reciveMsg(client,2048,theType=str)
        msg=msg.split(";")
        if new==True:
            if msg[1]=="DONE":
                
                log.write("",' compte créer avec succée')
                showinfo('CupChat Connection','votre compte à été créer !')
                id_status=False
            
            elif msg[1]=="EXIST":
                log.write("",'compte deja existant')
                showwarning('CupChat Connection','Désolé ce compte exite déja')
                wrong=1
                id_status=False
        else:
            if msg[1]=="<|ACCEPTED|>":
                log.write("",'conection reussi !')
                id_status=True
                
            elif msg[1]=="<|REJECTED|>":
                log.write("","Erreur de mot de passe, ou de pseudo")
                wrong=2
                id_status=False
            else :
                log.write("","probléme avec le serveur")

        def auth(new):
            global wrong
            wrong=0
            disable()
            login=frame_login.get()
            password=frame_password.get()
            
            if not login or not password :
                wrong=3
                id_status=False
            
            if new==True:
                client.send(bytes('<|ACCOUNT|>;<|CREATE|>;'+frame_login.get()+";"+frame_password.get(),"UTF-8"))
                fen.destroy()
                password=""
                identification(new)    
            elif new==False:
                client.send(bytes('<|ACCOUNT|>;<|AUTH|>;'+frame_login.get()+";"+frame_password.get(),"UTF-8"))    
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
    fen = build_fen("Connection",theme)
    fen.minsize(width=650, height=550)
    tmp=Label(fen,text="Connection")
    tmp.pack()
    fen.focus_force()
    fen.update_idletasks()
    try:   
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
                log.write("ERREUR",'la connexion a échouée avec le serveur')
                fen.mainloop()
                return False
        else:
            return False
            
    #Si la connection a réusie=============================================================================
    tmp.pack_forget()
    #titre principal page d'accueil et logo
    logo= PhotoImage(file=theme[2])
    titre= Label(fen, text="CupChat", bg=theme[0],fg=theme[1],font=('Helvetica','80','bold'),image=logo, compound =LEFT)
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
    frame_login.pack()
    espace= Frame(fa, bg=theme, height=40)
    espace.pack()
    #le "mot de passe" en dessous
    titre_password= Label(fa, text="Mot de passe :",bg=theme[0],fg=theme[1],font=('MV-Boli'),justify=LEFT, width= 30 )
    titre_password.pack()
    fa2= Frame(fa, bg="#4b4e56", pady=2, padx=2)
    fa2.pack()
    value = StringVar().set("")
    frame_password = Entry(fa2, textvariable=value,show="*",width=30,font=('MV-Boli'),relief=FLAT)
    frale_password.bind("<Return>",id_connect)
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
    #bouton pour se connecter
    bouton_valider = Button(frame_espace1,text="Connection",command=id_connect, relief=FLAT, width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
    bouton_valider.pack()
    bouton_valider.bind('<Enter>',enter )
    bouton_valider.bind('<Leave>',leave )
    #bouton pour créer un compte 
    bouton_créer = Button(frame_espace2,text="Inscription",command=id_create,relief=FLAT,width=20,bg="#525a8e",fg=theme[1],font="40",pady=8,activebackground="#57609b",bd=0)
    bouton_créer.pack()
    bouton_créer.bind('<Enter>',enter1 )
    bouton_créer.bind('<Leave>',leave1 )
    #bouton pour quitter
    bouton_quit = Button(fen, text="Quitter",command=fen.destroy,relief=FLAT,bg=theme[0],activebackground=theme[0],bd=0, font="40")
    bouton_quit.pack()
    bouton_quit.place(anchor=SE,relx=1.0, rely=1.0)

    fen.mainloop()
    return client
#-------------------------------------------------
def chat_screen(theme):
    global fen,config,client,reception_msg

    def send_message(bob=''):
        if len(send.get())>0:
            client.send(bytes('<|MESSAGE|>;'+login+';'+send.get(),"UTF-8"))
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
        roue= PhotoImage(file="roue.gif")
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
    cadre_history= VerticalScrolledFrame(cadre_principal, bg=theme[0])
    cadre_history.pack(side=BOTTOM,fill='both',expand=1)
    reception_msg = thread_message(cadre_history)
    reception_msg.start()
    #envoie d'une demande d'historique au serveur
    client.send(bytes('<|HISTORIQUE|>',"UTF-8"))
    fen.mainloop()
#CLASSES==========================================
class thread_message(threading.Thread):
    def __init__(self,cadre_history):
        self.stop=False
        self.frame=cadre_history

    def run(self):
        while self.stop==False:
            try:
                msg=reciveMsg(client,2048,theType=str)
                a=msg.split(";")
                if self.stop==True:
                    break
                elif a[0]=="<|MESSAGE|>":
                  a=msg.split("<|MESSAGE|>")
                  del a[0]
                  for line in a:
                    content=line.split(";")
                    del content[0]             
                    if content[1]==login:
                        Label(self.frame,text=content[1]+": "+content[2], justify='right').pack()
                    else:
                        Label(fself.frame,text=content[1]+": "+content[2]).pack()
            except:
                self.stop=True
#PROGRAMME PRINCIPAL==============================
config,theme = init()
while id_status==False:
    client=login_screen(theme)
    if client == False:
        clean_end()
        break

if client != False:
    chat_screen(theme)
