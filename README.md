# RFExport
Custom tool for export from XML invoices (Italian accounting)
Codice python che interpreta le fatture xml di un folder e le esporta in due file contenenti rispettivamente le intestazioni e le righe di dettaglio.
Il tracciato di uscita è personalizzato secondo le esigenze di un cliente specifico.I meccanismi di base possono essere riutilizzati per altri tipi di esportazione.

RF_EXPORT
E' possibile indicare le cartella di input e di output da linea di comando con i parametri directory di input e directory di output, es.:
rf_export.exe ‘c:\temp\in’  ‘c:\temp\out'

Di default prende i parametri dal file _init presente nella stessa directory
_init
#init params
in_path :D:\Essetre\rf_export\in
out_path :D:\Essetre\rf_export\out
#

#Se impostato a 1 elimina i file sorgente
delete_source :0

#prefisso ed estensione per i file di output
prefix :FTV
suffix :csv

il file fields.def contiene i percorsi di accesso ai tag XML per recuperare le informazioni richieste
il file mapdetail.def contiene l’elenco campi per il file di dettagliio righe

La funzione principale che gestisce la scrittura del file con i clienti/intestazioni è:
write_new_file_headers

La funzione principale che gestisce la scrittura del file con il dettaglio righe è:
write_new_file_details

Il meccanismo di scrittura delle righe di dettaglio è definito nella funzione:
custom_rows(campi,riga)
Qui passiamo l'elenco campi alla funzione: se iniziano per '>' vuol dire che dobbiamo andare a cercare un valore, se no prendiamo il valore fisso indicato tra apici, se iniziano con il simbolo + aggiungiamo quel numero di campi vuoti per mantenere la consistenza del file csv.
Esempio:
 campi = ['TES','>NREG','>DREG','>CodCliEsterno','>CodPag','0',' ','+19']

Qui è definita la logica di scrittura della riga di dettaglio articolo.
custom_row_logic(self, riga)

Altre logiche specifiche per i singoli campi possono essere gestite dalla funzione:
custom_field(self, field, riga)

