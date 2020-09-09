# -*- coding: utf-8 -*-

"""
 _  ________    _        
| |/ /  ____|  | |       
| ' /| |__ ___ | |_ ___  
|  < |  __/ _ \| __/ _ \ 
| . \| | | (_) | || (_) |
|_|\_\_|  \___/ \__\___/  
                                       
 Creato da.....: Marco Valaguzza
 Piattaforma...: Python3.6 con OpenCv
 Data prima ver: 30/10/2018
 Descrizione...: Il programma permette di scattare una foto e di caricarla dentro SMILE-Oracle
                 Come parametro d'ingresso (riga di comando) va passato l'indirizzo IP del server a cui collegarsi (es. qreader 10.0.4.11)

 Alcune note per la creazione dell'eseguibile che poi si può distribuire 
   - deve essere installato il pkg pyinstaller
   - per il funzionamento del programma sono ovviamente necessarie le librerie della gestione immagini, ecc. (v. sezione import)
   - eseguire il file KFoto_Compile.bat che esegue tutto il lavoro (fare riferimento a questo file per i commenti e le particolarità del caso)
   - accertarsi che nella dir del sorgente di questo programma NON siano presenti directory dist e build    
"""

# Libreria per connessione webcam ed elaborazione immagini
import cv2
# Importa libreria gestione avanzata array 
#import numpy as np
# Libreria per collegamento a Oracle
import cx_Oracle
# Libreria per leggere informazioni di sistema (es. nome utente)
import getpass
# Libreria di collegamento alle API di windows (tramite le API posso agire per tenere la window sempre al top di tutte le altre)
import win32gui
import win32con
from  win32api import GetSystemMetrics
# Libreria di sistema
import sys

def scrivi_in_ut_kfoto():
    """
       Scrive quanto contenuto in p_immagine nella tabella oracle UT_KFOTO
    """
    # Collegamento a Oracle
    #try:
    # Stringa di connessione (l'indirizzo IP viene ricavato dal parametro d'ingresso e se non presente si collega al server di backup)
    if len(sys.argv) > 1:
        v_indirizzo_ip = sys.argv[1]
    else:
        v_indirizzo_ip = '10.0.4.11'            
    v_connect_string = 'SMILE/SMILE@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(COMMUNITY=TCP)(PROTOCOL=TCP)(Host=' + v_indirizzo_ip + ')(Port=1521)))(CONNECT_DATA=(SID=SMIG)))'        
    v_oracle_db = cx_Oracle.connect(v_connect_string)   
    #except:
    #    return 'ko'
    
    # Apertura del cursore e scrittura nella tabella di lavoro fatta con nome utente e il dato appena letto    
    v_oracle_cursor = v_oracle_db.cursor()    
    # Leggo il file che contiene la foto scattata
    v_file_blob = open('foto_scattata.jpg', 'rb')                                                                                                
    v_blob_value = v_oracle_cursor.var(cx_Oracle.BLOB)                            
    v_blob_value.setvalue(0,v_file_blob.read())                                    
    v_istruzione_sql = "insert into UT_KFOTO values('"+getpass.getuser()+"',:immagine)";        
    print(v_istruzione_sql)
    #v_oracle_cursor.setinputsizes (immagine = cx_Oracle.BLOB)
    v_oracle_cursor.execute(v_istruzione_sql, {'immagine':v_blob_value})                            
    # Committo
    v_oracle_db.commit()                                
    # Chiudo il cursore 
    v_oracle_cursor.close()    
        
def main():        
    global v_immagine
    global v_exit   
    global v_click_foto
    global v_x
    global v_y
    global v_oracle_problems
    global v_win_size
    global v_screen_altezza
    global v_screen_larghezza
    
    # variabile globale che indica se si deve uscire dal programma 
    # (in realtà è possibile uscire dal programma anche tramite il tasto q)    
    v_exit  = False
    # variabile globale che indica se è stata scattata la foto
    v_click_foto = False    
    # variabile che riporta la posizione x per il disegno dei pittogrammi
    v_x = 1
    # altezza e larghezza dello schermo
    v_screen_altezza = GetSystemMetrics(1)
    v_screen_larghezza = GetSystemMetrics(0)    
    
    def controllo_eventi_del_mouse(event, x, y, flags, param):
        """
           Controllo eventi del mouse (da notare le variabili globali)
        """
        global v_immagine
        global v_exit
        global v_click_foto
        global v_x
        global v_y
        global v_oracle_problems
        global v_win_size
        
        # è stato premuto il pulsante del mouse in rilascio..controllo dove...
        if event == cv2.EVENT_LBUTTONUP:                
            # è stato premuto il tasto per scattare una foto            
            if x > (int(v_win_size[0]/2)-25) and x < (int(v_win_size[0]/2)+25) and y > (v_win_size[1]-75) and y < (v_win_size[1]-25):                  
                v_click_foto = True            
            # è stato premuto il tasto No--> quindi vuol dire che la lettura non va considerata
            # e il programma ritorna a mettersi in scansione
            if x > v_x and x < (v_x + 70) and y > v_y and y < (v_y + 70):                  
                v_click_foto = False            
            # è stato premuto il tasto Si--> quindi vuol dire che la lettura va considerata
            # valida e si deve uscire dal programma
            if x > v_x and x < (v_x + 70) and y > (v_y +80) and y < (v_y + 150):                  
                # Scrive il dato trovato nel DB di SMILE
                cv2.imwrite('foto_scattata.jpg', v_immagine)
                if scrivi_in_ut_kfoto()=='ko':
                    v_oracle_problems = True                        
                # se il dato è stato scritto --> passo alla prossima lettura
                else:
                    v_click_foto = False                                

    """
      Ciclo principale di apertura e lettura del flusso dati proveniente dalla webcam
    """        
    # Definizione di un font per la scrittura a video e relativo colore testo
    font = cv2.FONT_HERSHEY_SIMPLEX
    v_text_color = (0,0,0)
        
    # Attiva le webcam per la cattura del video        
    capture = cv2.VideoCapture(0)        
            
    # Se la webcam non è presente o non è riconosciuta...
    if not capture.isOpened():
        v_webcam = False
        #img = np.zeros((512,512,3), np.uint8)   questa istruzione crea un'immagine nera
        # Carico un'immagine di sfondo che riporta attenzione sul fatto che la webcam non è stata trovata
        img = cv2.imread('KFoto.png')
        # Ottengo la tupla con la dimensione dell'immagine
        v_win_size = img.shape
    else:        
        v_webcam = True
        
    # Inizia il ciclo di lettura del flusso video proveniente dalla webcam o dall'immagine fissa            
    v_1a_volta = True
    v_oracle_problems = False
    v_pos_text_riga1 = (10, 10)            
    v_pos_text_riga2 = (10, 20)                            
    while True:       
        # Se premuto il tasto q oppure richiesto da apposito flag, esco dal form
        if (cv2.waitKey(1) & 0xFF in (ord('q'),ord('Q'))) or (v_exit):
            break   
        # Se premuta la X sulla window, esco dal form
        if cv2.getWindowProperty('KFoto 1.0b', 0) < 0 and not v_1a_volta:
            break
                               
        # Se webcam è presente, leggo il prossimo frame che mi sta passando        
        if v_webcam:
            if not v_click_foto:                
                ret, img = capture.read()                                    
                v_immagine = img.copy()                  
            
            v_win_size = (int(capture.get(cv2.CAP_PROP_FRAME_WIDTH)),
                          int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT)))                        
            # Posizione del testo dei messaggi in fondo alla window
            v_pos_text_riga1 = (10, v_win_size[1]-50)            
            v_pos_text_riga2 = (10, v_win_size[1]-20)                        
            # definisco il rettagolo che contiene il mirino e quindi il crop dell'immagine che viene effettivamente scansionata
            v_larghezza_mirino = 300 
            v_altezza_mirino = 200
            v_mirino_top_left = ( int((v_win_size[0]-v_larghezza_mirino)/2), int((v_win_size[1]-v_altezza_mirino)/2) )                        
                                                                                                                              
            # Disegna il mirino (rosso se non ha letto nulla)            
            if v_click_foto:                
                v_colore = (0,255,0)                                
                # Disegno i pittogrammi-pulsanti
                v_x = int(v_win_size[0]-75)            
                v_y = int((v_win_size[1]-150)/2)            
                cv2.rectangle(img, (v_x,v_y),    (v_x+70,v_y+70) , (0,0,255),2)                                  
                cv2.rectangle(img, (v_x,v_y+80), (v_x+70,v_y+150) ,(0,255,0),2)                      
                cv2.putText(img,'No', (v_x + 17,  v_y+43),  font, 1, (0,0,255), 2,cv2.LINE_AA)                                
                cv2.putText(img,'Si', (v_x + 17,  v_y+123), font, 1, (0,255,0), 2,cv2.LINE_AA)                                                            
            else:
                v_colore = (0,0,255)
                            
            cv2.circle(img,(int(v_win_size[0]/2), v_win_size[1]-50), 40, v_colore, 2, 2)      
            cv2.circle(img,(int(v_win_size[0]/2), v_win_size[1]-50), 30, v_colore, -2, 2)      
            cv2.line(img, ( v_mirino_top_left[0] + int(v_larghezza_mirino/2), v_mirino_top_left[1] + int(v_altezza_mirino/2) - 20) , 
                          ( v_mirino_top_left[0] + int(v_larghezza_mirino/2), v_mirino_top_left[1] + int(v_altezza_mirino/2) + 20) ,
                          v_colore,
                          2)
            cv2.line(img, ( v_mirino_top_left[0] + int(v_larghezza_mirino/2) - 20, v_mirino_top_left[1] + int(v_altezza_mirino/2) ) , 
                          ( v_mirino_top_left[0] + int(v_larghezza_mirino/2) + 20, v_mirino_top_left[1] + int(v_altezza_mirino/2) ) ,
                          v_colore,
                          2)     
                                                                   
        # Emette la scritta se ci sono problemi di connessione a Oracle
        if v_oracle_problems:
            cv2.putText(img,'Problema connessione a SMILE!', v_pos_text_riga1, font, 1, (0,0,255), 1, cv2.LINE_AA)                          
        
        # Aggiorna lo schermo                                
        cv2.imshow('KFoto 1.0b', img)            
        # Riposiziono la finestra a destra dello schermo
        cv2.moveWindow('KFoto 1.0b', v_screen_larghezza - v_win_size[0], int( (v_screen_altezza - v_win_size[1]) / 2))           
        
        # Ricerco il puntatore della finestra 
        v_win_handle = win32gui.FindWindow(None, 'KFoto 1.0b')
        # Se finestra trovata --> ne forzo la visualizzazione davanti a tutte le window aperte in questo momento 
        # in questo modo l'applicazione rimane sempre in primo piano
        if v_win_handle is not None:            
            win32gui.SetWindowPos(v_win_handle, win32con.HWND_TOPMOST, 0, 0, 0, 0,win32con.SWP_NOSIZE | win32con.SWP_NOMOVE)            
        
        # associo la funzione che controlla gli eventi del mouse
        cv2.setMouseCallback('KFoto 1.0b', controllo_eventi_del_mouse)    
        
        v_1a_volta = False
                                    
    # Chiudo la webcam e la window
    capture.release()
    cv2.destroyAllWindows()		
    
if __name__ == "__main__":    
    main()