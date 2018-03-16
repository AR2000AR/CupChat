from socketTools import *
from tkinter import *
from tkinter.messagebox import *
from socket import *
from tools import *

#test
test=True

#theme
option_theme=0

#taille de la fenêtre
taille='900x700'   #######quand il modifie la taille, la mémoriser avec event

#nuit
if option_theme==0:
    theme="#60636d"
    ecriture="white"
    logo1="logo-tchat-nuit.ppm"
    gif1='gif-nuit.gif'
#jour
if option_theme==1:
    theme="white"
    ecriture="black"
    logo1='logo-tchat-jour.jpg'
    gif1='gif-jour.gif'

#compte enregistré ?
create= False
#compte_enregistré()

#variable d'erreur de connection
wrong=0

def identification(auth,new):
    
##  class def_gif(Label):
##      
##        def __init__(self, master, filename, speed): #définit speed 
##                self.speed = speed
##                #speed: le delay en milliseconde entre chaques images cette fonction est là pour definir speed
##        
##                self.frames = [] # liste permettant de stocker les images du gif
##                i = 0
##                while True:
##                    try:
##                        p = PhotoImage(file=filename, format="gif - {}".format(i))
##                        #prend les images que comprend le gif
##                
##                    except TclError:
##                        break #la boucle s'arrête
##                    self.frames.append(p) #on stock dans la liste les images du gif
##                    i += 1
##
##                
##                super().__init__(master, image=self.frames[0])
##                self.frame = 0
##                self.num_frames = i
##                self.after(self.speed, self._animate) #fait attendre (vitesse) et appelle la fonction animate
##                
##            def _animate(self):
##                self.frame = (self.frame + 1) % self.num_frames
##                # permet de faire une sorte de boucle allant de 1 à nombre max d'image
##        
##                self['image'] = self.frames[self.frame] #intégre l'image dans les options
##                self.after(self.speed, self._animate) #fait attendre (vitesse) et appelle la fonction animate
## 
##        #if __name__ == "__main__": #verifie que la fenetre est bien la fenetre principale et pas une librairie
    
##    gif = def_gif(app, filename=gif1, speed=40)
##    gif.pack()
    #definition de la fenetre Tkinter
    app = Tk()
    app.title("tinytchat",)
    app['bg']=theme
    app.geometry(taille)
    app.minsize(width=600, height=500)
    
    label_connect= Label(app, text="CONNECTION EN COURS ...", bg=theme,fg=ecriture, font="MV-Boli,80,bold" )
    label_connect.pack()
    label_connect.place(anchor=N ,relx=0.5, rely=0.4)
    
    app.mainloop()
    

    if test==True:
            app.destroy()
            appli()
            
    if test==False:
        #recevoir la confirmation du serveur
        connect_accept=reciveMsg()
        if new==1:
            if connect_accept.find('DONE')>-1:
                print(' compte créer avec succée') #######log
                showinfo('votre compte à été créer !')
                app.destroy()
                appli()
            
            if connect_accept.find('EXIST')>-1:
                print('copmpte deja existant')#######log
                print('Désolé ce compte exite déja')
                wrong=1
                app.destroy()
                accueil()

        elif auth==1:
            if connect_accept.find('<|ACCEPTED|>')>-1:
                print('conection reussi !') #######log
                app.destroy()
                appli()

            
            if connect_accept.find('<|REJECTED|>')>-1:
                print("Erreur de mot de passe, ou de pseudo") #######log
                wrong= 2
                app.destroy()
                accueil()

        else :
            print("il y a un probléme avec le serveur, en attendant jouer avec cattou") ######### cattou ?


#----------------------------------

def accueil():
    
    app = Tk()
    app.title("tinytchat",)
    app['bg']=theme
    app.minsize(width=600, height=500)


    if test==False:
        client = clientConnect()
        #172.18.144.187


    #titre principal page d'accueil et logo
    logo= PhotoImage(file=logo1)

    titre= Label(app, text="Tchat", bg=theme,fg=ecriture,  font="MV-Boli,80,bold" ) #, image=logo, compound =RIGHT
    titre.pack()
    titre.place(anchor=N ,relx=0.5, rely=0.1)


    #frame contenant la partie de l'identification
    fa= Frame(app, bg=theme)
    fa.pack()
    fa.place(anchor=N ,relx=0.5, rely=0.4)
    
    if wrong==2:
        titre_erreur= Label(fa, text="Désolé ce compte exite déja", bg=theme,fg=Red ,  font="MV-Boli,bold", justify=LEFT,width= 30 )
        titre_erreur.pack()

    if wrong==1:
        titre_erreur= Label(fa, text="vous vous êtes trompé de mot de passe, ou de pseudo", bg=theme,fg=Red,  font="MV-Boli,bold", justify=LEFT,width= 30 )
        titre_erreur.pack()

    titre_login= Label(fa, text="Identifiant :", bg=theme,fg=ecriture,  font="MV-Boli,bold", justify=LEFT,width= 30 )
    titre_login.pack()

    fa3= Frame(fa, bg="#4b4e56", pady=2, padx=2)
    fa3.pack()

    value = StringVar().set("")  #########valeur rentrer par default
    login = Entry(fa3, textvariable=value, width=30, font="MV-Boli,45,bold", relief=FLAT)
    login.pack()

    espace= Frame(fa, bg=theme, height=40)
    espace.pack()


    #le "mot de passe" en dessous
    titre_password= Label(fa, text="Mot de passe :", bg=theme,fg=ecriture,  font="MV-Boli,bold", justify=LEFT, width= 30 )
    titre_password.pack()

    fa2= Frame(fa, bg="#4b4e56", pady=2, padx=2)
    fa2.pack()

    value = StringVar().set("")
    password = Entry(fa2, textvariable=value,show="*", width=30, font="MV-Boli,45,bold", relief=FLAT)
    password.pack()

    #si la souris passe sur le bouton (effet visuel)
    def enter(event):
        bouton_valider.configure(bg="#57609b")
        
    def enter1(event):
        bouton_créer.configure(bg="#57609b")

    #quand la souris ressors du bouton (effet visuel)
    def leave(event):
        bouton_valider.configure(bg="#525a8e")

    def leave1(event):
        bouton_créer.configure(bg="#525a8e")


        #creation de compte
    def id_create():
        disable()
        showinfo("Alerte", password.get()+"\n"+login.get() ) #####temporaire

        if test==False:
            client.send(bytes('<|ACCOUNT|>;<|CREATE|>;'+login.get()+";"+password.get(),"UTF-8"))
            
        app.destroy()
        new =1
        auth =0
        identification(new,auth)

        #autentification
    def id_auth():
        disable()
        showinfo("Alerte", password.get()+"\n"+login.get() ) #####temporaire
        
        if test==False:
            client.send(bytes('<|ACCOUNT|>;<|AUTH|>;'+login.get()+";"+password.get(),"UTF-8"))
        app.destroy()
        auth =1
        new =0
        identification(auth,new)

    #desactive les boutons au moment de la connection
    def disable():
        bouton_valider.configure(state=DISABLED)
        bouton_créer.configure(state=DISABLED)
        bouton_quit.configure(state=DISABLED)
    

    fbouton= Frame(fa, bg=theme, pady=30)
    fbouton.pack()

    fbouton_valider= Frame(fbouton, bg=theme, pady=10)
    fbouton_valider.pack()

    fbouton_créer= Frame(fbouton, bg=theme, pady=10)
    fbouton_créer.pack()

    #bouton pour se connecter
    bouton_valider = Button(fbouton_valider, text="Connection", command=id_auth, relief=FLAT, width=20,bg="#525a8e", fg=ecriture, font="40",pady=10, activebackground="#57609b", bd=0)
    bouton_valider.pack()

    bouton_valider.bind('<Enter>',enter )
    bouton_valider.bind('<Leave>',leave )

    #bouton pour créer un compte
    bouton_créer = Button(fbouton_créer, text="Inscription", command=id_create, relief=FLAT, width=20,bg="#525a8e", fg=ecriture, font="40",pady=10, activebackground="#57609b", bd=0)
    bouton_créer.pack()

    bouton_créer.bind('<Enter>',enter1 )
    bouton_créer.bind('<Leave>',leave1 )

    #bouton pour quitter
    bouton_quit = Button(app, text="Quitter", command=app.destroy, relief=FLAT,bg=theme, activebackground=theme, bd=0, font="40")
    bouton_quit.pack()
    bouton_quit.place(anchor=SE,relx=1.0, rely=1.0)

    app.mainloop()

#----------------------------------

def appli():
    app = Tk()
    app.geometry(taille) 
    app['bg']=theme
    app.minsize(width=600, height=500)
    
    app.bind('<Configure',taille_fenetre )


    app.mainloop()

#----------------------------------

def history():
    pass

#----------------------------------

def compte_enregistré() :
    pass

#----------------------------------

def taille_fenetre(event) :
    pass

#----------------------------------

if __name__=="__main__":
    accueil()


#--------------------------------

#######memorisation auto

#reciveMsg()

#sendFile()

#reciveFile()

#######The Message widget

########les message
    
######l'historique des messages
    
#########langue avec un fichier de langue
    
#######fermer la connection

#########menu avec pour les boutton : compound =   RIGHT (TOP BOTTOM LEFT pour placer l'image a cote d'un texte ) image=... pour mettre l'image
