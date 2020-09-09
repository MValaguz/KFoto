rmdir dist\KFoto /S /Q
rem COMPILAZIONE del programma KFoto (il parametro --windowed non fa comparire la window console quando viene mandato in esecuzione
pyinstaller --windowed --icon=KFoto.ico KFoto.py
rem copia della libreria di connessione Oracle (essa è stata ricavata prendendola dal package di installazione oracle "instant client"
rem attenzione perché sul client di destinazione dovrà essere settata la variabile NLS_LANG
xcopy oraociei11.dll dist\KFoto
rem copia dell'immagine di KFoto (verrà utilizzata come sfondo nel caso non venga trovata una telecamera collegata)
xcopy KFoto.png dist\KFoto 
rmdir build /S /Q
pause
