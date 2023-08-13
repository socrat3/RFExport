#!/usr/bin/env python3

"""
Rf Export per Fatture Elettroniche - Roberto Zanardo per Essetre Srl
"""
import glob
import sys
import os
import xmltodict
from datetime import datetime

class main():

    def __init__(self):

        self.folder_path = 'C:\scarica2\FattureRicevute_MLTFRC90P56A089C\Fatture Elettroniche\in'
        self.output_path = 'C:\scarica2\FattureRicevute_MLTFRC90P56A089C\Fatture Elettroniche\out'
        #self.temp_path = ''
        self.prefix = ''
        self.delete_source = ''

        self.folder_path = r'C:\scarica2\FattureRicevute_MLTFRC90P56A089C\Fatture Elettroniche\in'
        self.output_path = r'C:\scarica2\FattureRicevute_MLTFRC90P56A089C\Fatture Elettroniche\out'

        #self.folder_path = self.get_init('in_path')
        #self.output_path = self.get_init('out_path')
        self.prefix_cli = self.get_init('prefix_cli')
        self.prefix = self.get_init('prefix')
        self.suffix = self.get_init('suffix')
        self.delete_source = self.get_init('delete_source')

        #Vediamo se ci sono argomenti per le cartelle di input/output
        if len(sys.argv)==3:
            self.folder_path = sys.argv[1]
            self.output_path = sys.argv[2]

        print ('Input: %s' % (self.folder_path))
        print ('Output: %s' % (self.output_path))

        self.export_button()

    # Qui prendiamo l'elenco campi
    def get_init(self, value):
        res = None
        ini_file = open("_init", "r")
        row = ini_file.readline()

        while row:
            if '#' not in row:
                if value in row:
                    res = row[row.index(':')+1:]
            row = ini_file.readline()
        ini_file.close()
        return res.replace('\n','')

    # Qui prendiamo l'elenco campi
    def get_strutturacampi(self):
        StrutturaCampi = []
        # Prendiamo l'elenco campi da un file .def
        ini_file = open("fields.def", "r")
        row = ini_file.readline()

        while row:
            if '#' not in row:
                row = row[row.index(':')+1:]
                RigaCampi = row.split(',')
                StrutturaCampi.append(RigaCampi)
            row = ini_file.readline()
        ini_file.close()
        return StrutturaCampi

    # Qui prendiamo altri metadati (label e altri metadati)
    def get_metacampi(self):
        MetaCampi = []
        # Prendiamo l'elenco campi da un file .def
        ini_file = open("fields.def", "r")
        row = ini_file.readline()

        while row:
            if '#' not in row:
                row = row[:row.index(':')]
                RigaCampi = row.split(',')
                MetaCampi.append(RigaCampi)
            row = ini_file.readline()
        ini_file.close()
        return MetaCampi

    # Altro metodo per prendere elenco campi specificando il file
    def get_elencocampi(self, filename):
        ElencoCampi = []
        # Prendiamo l'elenco campi da un file .def
        ini_file = open(filename, "r")
        row = ini_file.readline()

        while row:
            if '#' not in row:
                ElencoCampi.append(row.replace('\n', ''))
            row = ini_file.readline()
        ini_file.close()
        return ElencoCampi

    def is_number_format(self, v):
        if '.' in v:
            try:
                n = float(v)
                v = '{0:.2f}'.format(n)
            except:
                pass
        return v

    def list_or_dict(self, v):
        if isinstance(v, list) or isinstance(v, dict) or isinstance(v, bool):
            return True
        else:
            return False

    def normalizza_campo(self, v):
        v = self.extract_field(v, '< ![CDATA[', ']]>')
        if not self.list_or_dict(v):
            v = self.is_number_format(v)
        return v

    def extract_field(self, value, start_tag, end_tag):
        try:
            value = value[value.index(start_tag):value.index(end_tag)]
        except:
            pass
        if not self.list_or_dict(value):
            value = value.replace('\n', ' ')
        return value

    def export_button(self):
        DatiFatture = []
        DatiFattureHeaders = []
        DatiFattureDetails = []

        StrutturaCampi = self.get_strutturacampi()
        MetaCampi = self.get_metacampi()
        path = self.folder_path

        files = []

        for ext in ('*.p7m', '*.xml'):
            files.extend(glob.glob(os.path.join(path, ext)))

        t = len(files)

        if t==0:
            print('NESSUN DATO DA ELABORARE.')
            sys.exit()

        fn = 0
        # Leggiamo tutti i file
        for filename in files:
            fn = fn + 1
            print('INIZIO ELABORAZIONE FILE:%s'%(str(filename)))

            with open(filename) as fd:
                FatturaXML = self.read_fattura(StrutturaCampi, MetaCampi, fd, filename)
                Fattura = FatturaXML[0]

                headers = []

                for datas in Fattura:
                    headers.append(datas)

                DatiFattureHeaders.append(headers)

            #with open(filename) as fd:
                Righe = FatturaXML[1]

                #print('%s'%(str(Righe)))

                details = []
                payment_detail = []
                iva_detail = []
                payment = []

                for datas in Righe:
                    row = []
                    #print('Datas:%s'%(str(datas)))
                    if 'Righe' in datas or 'Righe' in datas[0]:
                        #print('ci sono delle righe')
                        for k, v in datas[1].items():
                            row.append((k, self.normalizza_campo(v)))
                        details.append(row)

                    if 'Pagamenti' in datas or 'Pagamenti' in datas[0]:
                        #print('ci sono delle righe')
                        for k, v in datas[1].items():
                            row.append((k, self.normalizza_campo(v)))
                            #print('ROW:%s'%(str(row)))
                        payment_detail.append(row)

                    if 'Riepiloghi IVA' in datas or 'Riepiloghi IVA' in datas[0]:
                        for k, v in datas[1].items():
                            row.append((k, self.normalizza_campo(v)))
                        iva_detail.append(row)

                payment.append(payment_detail)
                #print('payment_detail: %s'%(str(payment)))
                if len(details) > 0:
                    for detail_rows in details:
                        DatiFattureDetails.append(headers + detail_rows + payment + iva_detail) # + payment_detail + iva_detail

            if self.delete_source=='1':
                os.remove(filename)

        self.write_new_file_headers(DatiFattureHeaders, path)
        self.write_new_file_details(DatiFattureDetails, path)



    def read_fattura(self, StrutturaCampi, MetaCampi, fd, filename):
        Fattura = []
        Righe = []
        #Pagamenti = []
        # Gestione più causali (ad esempio)
        string_list = ''

        file_text = fd.read()
        preformatted_text = file_text

        try:
            # Leviamo eventuali caratteri prima di <?xml version="1.0" encoding="UTF-8"?>:
            tagxml = '<?xml'
            tagxml = file_text[:file_text.index(tagxml)]
            file_text = file_text.replace(tagxml, '')
        except:
            print('Error on file: %s xmltag:%s' % (filename, file_text[:20] + '...'))

        signs = '<ds:Signature'
        signe = '</ds:Signature>'

        if signs in file_text:
            signature_text = file_text[file_text.index(signs):file_text.index(signe) + len(signe)]
            file_text = file_text.replace(signature_text, '')

        doc = xmltodict.parse(file_text)
        # Prendiamo la prima chiave nel dictionary (es: p:FatturaElettronica o ns1:FatturaElettronica)
        root = list(doc.keys())[0]

        field_index = -1
        field_label = ''
        for fieldpath in StrutturaCampi:
            print("-", end="\r", flush=True)
            field_index+=1
            field_label = MetaCampi[field_index][0]

            field1 = ''
            field2 = ''

            string_2_eval = 'doc["' + root + '"]'
            row_dict = {}
            pag_dict = {}
            iva_dict = {}

            for field in fieldpath:
                # memorizziamo il nome del primo e dell'ultimo campo utile
                try:
                    field1 = fieldpath[1]
                    field2 = fieldpath[-1]
                    string_2_eval += '["' + field.replace('\n', '') + '"]'
                except:
                    string_2_eval = fieldpath[0]

            try:
                value = eval(string_2_eval)
            except:
                value = False

            # Verifichiamo che tipo di dato abbiamo:
            # se è un dictionary vuol dire che è una fattura con una sola riga di dettaglio oppure un deattaglio pagamenti
            if isinstance(value, dict) and value:
                #print(str(value) + " E' UN DICTIONARY !\n")
                for k, v in value.items():
                    if "DettaglioPagamento" in k:
                        #print("DETTAGLI PAGAMENTO!:")
                        for vad in v:
                            pag_dict = {}
                            if isinstance(vad, dict):
                                for ka in vad:
                                    pag_dict[ka] = self.normalizza_campo(vad[ka])
                                Righe.append(('Pagamenti:', pag_dict))
                    if not isinstance(v, list) and "NumeroLinea" in value:
                        row_dict[k] = self.normalizza_campo(v)
                if row_dict:
                    Righe.append(('Righe:', row_dict))

            # se è una lista vuol dire che è una fattura con una più righe di dettaglio
            elif isinstance(value, list) and value:
                for l in value:
                    if not isinstance(l, str):
                    #verifichiamo prima se sono righe fatture o riepiloghi iva
                        riepiva = False
                        for k, v in l.items():
                            if k == 'RiferimentoNormativo':
                                riepiva = True
                        #se sono riepiloghi
                        if riepiva:
                            for k, v in l.items():
                                #print(k, ' ', v)
                                # Vedere se il valore è a sua volta una lista o un dict
                                # self.check_type(v)
                                if not isinstance(v, list):
                                    iva_dict[k] = v
                            Righe.append(('Riepiloghi IVA', iva_dict))
                            iva_dict = {}
                        else:
                            for k, v in l.items():
                                #print(k, ' ', v)
                                # Vedere se il valore è a sua volta una lista o un dict
                                # self.check_type(v)
                                if not isinstance(v, list):
                                    row_dict[k] = v
                            Righe.append(('Righe', row_dict))
                            row_dict = {}
                    else:
                        #print(l)
                        string_list += l
                        Fattura.append((field_label, self.normalizza_campo(string_list)))

            # se è un valore vuol dire che è un valore singolo
            elif not isinstance(value, dict) and not isinstance(value, list) and value:
                Fattura.append((field_label, self.normalizza_campo(value)))

            # se è un valore ma non contiene dati aggiungiamo comunque il campo vuoto per non perdere la formattazione delle colonne nel file in uscita
            elif not isinstance(value, dict) and not isinstance(value, list) and not value:
                Fattura.append((field_label, ''))

        ### Fine lettura campi fattura, prepariamo una nuova struttura per la scrittura su file
        return Fattura,Righe

    def write_new_file_headers(self, DatiFatture, path):

        dateTimeObj = datetime.now()
        uniquetime = dateTimeObj.strftime("_%Y%m%d_%H%M%S")

        if self.output_path:
            path = self.output_path
        else:
            path = self.folder_path

        out_file = open(os.path.join(path, self.prefix_cli+uniquetime+"_headers." + self.suffix), "w")

        #Scriviamo le label
        Labels = ['Trek','TipoAnagr','CodClienteEst','Piva','CF','RagSoc1','RagSoc2','Indirizzo','Cap','Localita','Prov','Stato','SDI_Dest','SDI_Pec','TipoSoggFTE','FormaPag','BancaAzienda','DesBancaCliente','AbiCliente','CabCliente']
        i = 0
        for Label in Labels:
            out_file.write('%s;' % (Label))
        out_file.write('\n')

        #Scriviamo i valori
        for Fattura in DatiFatture:

            campi = ['GEN','1','>CodCliEsterno','>Piva','>CF','>RagSoc1','>RagSoc2','>Indirizzo','>Cap','>Localita','>Prov','>Stato','>SDI_Dest','>SDI_Pec','>TipoSoggFTE','>CodPag','>PAR_BancaAzienda','>PAR_DesBancaCliente','>PAR_ABI_Cliente','>PAR_CAB_Cliente',]
            out_file.write(self.custom_rows(campi,Fattura))

        out_file.close()

    def write_new_file_details(self, DatiFatture, path):

        dateTimeObj = datetime.now()
        uniquetime = dateTimeObj.strftime("_%Y%m%d_%H%M%S")

        if self.output_path:
            path = self.output_path
        else:
            path = self.folder_path

        out_file = open(os.path.join(path, self.prefix+uniquetime+"_details." + self.suffix), "w")
        elenco = self.get_elencocampi('mapdetail.def')

        #Scriviamo le label
        for lbl in elenco:
            out_file.write('%s;' % (lbl))
        out_file.write('\n')

        # Passiamo l'elenco campi alla funzione custom_rows: se iniziano per '>' vuol dire che dobbiamo andare a cercare un valore, se no prendiamo il valore fisso indicato tra apici, se iniziano con il simbolo + aggiungiamo quel numero di campi vuoti per mantenere la consistenza del file csv

        i= 0
        r = 0
        c = 0
        #leggiamo i valori delle righe per capire quante sono per ogni fattura
        #prepariamo una lista di tuple con fattura e numero righe
        FattureHeader = []
        Fattureriga = []
        Primafattura = True
        NumeroFattura = ''
        log_file = open(os.path.join(path, "log.txt"), "w")

        payment_detail = []
        iva_detail = []

        for riga in DatiFatture:
            c+=1
            NumeroFattura = self.get_field('Numero',riga)

            log_file.write('--------------------------------------------------\n')
            log_file.write(NumeroFattura+'\n')

            if NumeroFattura not in FattureHeader:
                FattureHeader.append(NumeroFattura)

            NumeroLinea = self.get_field('NumeroLinea',riga)

            log_file.write(str(NumeroLinea)+'\n')
            log_file.write(str(riga)+'\n')

            if NumeroLinea =='1' and Primafattura:
                    Primafattura = False
                    i+=1
                    r=1
            elif (NumeroLinea !='1' and NumeroLinea !='' and not Primafattura):
                    r+=1
            elif NumeroLinea =='1' and not Primafattura:
                    Fattureriga.append((i,r))
                    i+=1
                    r=1
        Fattureriga.append((i,r))
        log_file.close()

        i = 0
        r = 0
        c = 0
        #Scriviamo i valori
        for fattura in Fattureriga:
            indice_fattura = fattura[0]
            numero_righe = fattura[1]
            riga = DatiFatture[r]

            EsigibilitaIVA = self.custom_field('EsigibilitaIVA',riga)
            TDA = '0'
            ### RIGA TESTATA
            if EsigibilitaIVA == 'S':
                TDA = '61'

            campi = ['TES','>NREG','>DREG','>CodCliEsterno','>CodPag','0',' ','+18',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
            out_file.write(self.custom_rows(campi,riga))

            #Verifichiamo la causale sia compilata
            if self.custom_field('Causale',riga)!='':
                ### RIGA CAUSALE
                campi = ['RIG','>NREG','>DREG','>CodCliEsterno',' ','20','0,5',' ',' ','>Causale','+15',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
                out_file.write(self.custom_rows(campi,riga))

            #scriviamo le righe articolo
            for righe in range(numero_righe):
                riga = DatiFatture[r]
                
                ### RIGHE ARTICOLO
                out_file.write(self.custom_row_logic(riga,TDA))
                r += 1

            riga = DatiFatture[r-1]
            payment_detail = self.get_payments(riga)
            iva_detail = self.get_ivasplit(riga)

            iva_start = 1000
            ### RIGA IVA
            if len(iva_detail)>0:
                for iva in iva_detail:
                    iva = eval(iva)
                    codiva = ' '
                    if iva[0][1] == '0.00':
                        codiva=iva[1][1]
                        totiva = '0.00'
                    else:
                        codiva=iva[0][1]
                        totiva = iva[3][1]
                    impiva = iva[2][1]

                    campi = ['IVA','>NREG','>DREG','>CodCliEsterno',' ','0',str(iva_start),'+9',codiva, impiva, totiva,'+6',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
                    out_file.write(self.custom_rows(campi,riga))
                    iva_start+=1
            else:
                campi = ['IVA','>NREG','>DREG','>CodCliEsterno',' ','0',str(iva_start),'+9','>IVA_CodIva','>IVA_ImpTot','>IVA_IvaTot','+6',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
                out_file.write(self.custom_rows(campi,riga))

            par_start = 1100
            ### RIGA PAR
            if len(payment_detail)>0:
                #print('PAGAMENTI MULTIPLI')
                for payment in payment_detail:
                    payment = eval(payment)
                    bancariga = ''
                    abiriga = ''
                    cabriga = ''
                    #try:
                    if payment[0][1] == 'MP05':
                        bancariga = payment[4][1]
                        abiriga = ' '
                        cabriga = ' '
                    else:
                        try:
                            bancariga = payment[4][1]
                            abiriga = payment[5][1]
                            cabriga = payment[6][1]
                        except:
                            bancariga = 'NON PRESENTE'
                            abiriga = 'NON PRESENTE'
                            cabriga = 'NON PRESENTE'
                    #except:
                        #pass
                        
                    campi = ['PAR','>NREG','>DREG','>CodCliEsterno',' ','0', str(par_start),'+12',str(payment[1][1]),str(payment[0][1]),bancariga,abiriga,cabriga,str(payment[2][1]),TDA,'>TipoDocumento']
                    out_file.write(self.custom_rows(campi,riga))
                    par_start+=1
            else:
                campi = ['PAR','>NREG','>DREG','>CodCliEsterno',' ','0', str(par_start),'+12','>PAR_Scad','>CodPag','>PAR_BancaAzienda','>PAR_ABI_Cliente','>PAR_CAB_Cliente','>PAR_Importo',TDA,'>TipoDocumento']
                out_file.write(self.custom_rows(campi,riga))

        out_file.close()

    def custom_row_logic(self, riga,TDA):
        rigacsv_art = ''

        art = self.custom_field('CodArt',riga)
        qta = self.custom_field('Qta',riga)
        imp = self.custom_field('Prezzo',riga)

        if qta !='' or imp!='':
            if art !='':
                #tipo 40
                ### PRIMA RIGA ARTICOLO
                campi = ['RIG','>NREG','>DREG','>CodCliEsterno',' ','40','>NrRiga','>CodArt','>DesRiga',' ','>UM','>Qta','>Prezzo','>Sconto1','>Importo','>CodIva','+9',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
            else:
                #tipo 40 con addebito
                ### PRIMA RIGA ARTICOLO
                campi = ['RIG','>NREG','>DREG','>CodCliEsterno',' ','40','>NrRiga','ADDEBITO','>DesRiga',' ','>UM','>Qta','>Prezzo','>Sconto1','>Importo','>CodIva','+9',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']
        if qta =='' and imp=='':
                #tipo 20
                ### PRIMA RIGA ARTICOLO
                campi = ['RIG','>NREG','>DREG','>CodCliEsterno',' ','20','>NrRiga','>CodArt',' ','>DesRiga','>UM','>Qta','>Prezzo','>Sconto1','>Importo','>CodIva','+9',TDA,'>TipoDocumento','>TipoRitenuta','>ImportoRitenuta','>AliquotaRitenuta','>CausalePagamento']

        rigacsv_art = self.custom_rows(campi,riga)
        return rigacsv_art

    def custom_rows(self, fields, riga):
        #Ritorna la riga con i campi richiesti
        rigacsv = ''
        res = ''
        for f in fields:
            if len(f) > 0:
                if f[0]=='>':
                    res = self.custom_field(f[1:],riga)
                    rigacsv += res + ';'
                elif f[0]=='+':
                    for i in range(int(f[1:])):
                        rigacsv += ';'
                else:
                    rigacsv+= f + ';'

        desrig = int(self.get_init('desrig'))
        if desrig>0 and fields[0]=='RIG':
            r = self.custom_field('DesRiga',riga)[:desrig]
            rigacsv += r + ";"
        else:
            rigacsv += ";"
        rigacsv += '\n'
        return rigacsv


    ### Qui possiamo gestire logiche specifiche per i singoli campi
    def custom_field(self, field, riga):
        #print(field)
        res = 0
        try:
            if field == 'TREK':
                res = 'RIG'
            elif field == 'NREG':
                res = self.get_field('Numero',riga)
            elif field == 'DREG':
                res = self.get_field('Data',riga)
            elif field == 'CodCliEsterno':
                res = self.get_field('CodiceNazione',riga) + self.get_field('Piva',riga)
                if not res:
                    res = 'IT' + self.get_field('CodiceFiscale',riga)
            elif field == 'RagSoc1':
                res = self.get_field('RagSoc1',riga)
                res = res[:29]
            elif field == 'RagSoc2':
                res = self.get_field('RagSoc1',riga)
                res = res[30:]
            elif field == 'CodPag':
                res = self.get_field('FormaPag',riga)
                if len(res)==0:
                    for r in riga:
                        for x in r:
                            try:
                                y = x[0]
                                if 'ModalitaPagamento' in y:
                                    res = x[0][1]
                            except:
                                pass
            elif field == 'Indirizzo':
                res = self.get_field('Indirizzo',riga) + ' '+self.get_field('NumeroCivico',riga)
            elif field == 'TipoRiga':
                res = '40'
            elif field == 'TipoSoggFTE':
                res = self.get_field('SDI_Dest',riga)
                if len(res)<7:
                    res = '1'
                elif len(res)==7:
                    res = '2'
            elif field == 'NrRiga':
                res = self.get_field('NumeroLinea',riga)
            elif field == 'CodArt':
                res = self.get_field('CodiceTipo',riga)
            elif field == 'DesRiga':
                res = self.get_field('Descrizione',riga)
            elif field == 'DesCommento':
                res = self.get_field('Causale',riga)
            elif field == 'UM':
                res = self.get_field('UnitaMisura',riga)
            elif field == 'Qta':
                res = self.get_field('Quantita',riga)
            elif field == 'Prezzo':
                res = self.get_field('PrezzoUnitario',riga)
            elif field == 'Sconto1':
                res = self.get_field('Sconto',riga)
            elif field == 'Importo':
                res = self.get_field('PrezzoTotale',riga)
            elif field == 'CodIva':
                res = self.get_field('AliquotaIVA',riga)
                if res == '0.00':
                    res = self.get_field('Natura',riga)
            elif field == 'IVA_CodIva':
                res = self.get_field('RiepilogoAliquotaIVA',riga)
                if res=='0.00':
                    res = self.get_field('Natura',riga)
            elif field == 'IVA_ImpTot':
                res = self.get_field('ImponibileImporto',riga)
            elif field == 'IVA_IvaTot':
                res = self.get_field('Imposta',riga)
            elif field == 'PAR_Scad':
                res = self.get_field('DataScadenzaPagamento',riga)
            elif field == 'PAR_TipoPag':
                res = self.get_field('CondizioniPagamento',riga)
            elif field == 'ModalitaPagamento':
                res = self.get_field('ModalitaPagamento',riga)
            elif field == 'PAR_BancaAzienda':
                res = self.get_field('FormaPag',riga)
                if res!='MP12':
                    res = self.get_field('BancaAzienda',riga)
                else:
                    res = ''
            elif field == 'PAR_DesBancaCliente':
                res = self.get_field('FormaPag',riga)
                if res=='MP12':
                    res = self.get_field('DesBancaCliente',riga)
                else:
                    res = ''
            elif field == 'PAR_ABI_Cliente':
                res = self.get_field('FormaPag',riga)
                if res=='MP12':
                    res = self.get_field('AbiCliente',riga)
                else:
                    res = ''
            elif field == 'PAR_CAB_Cliente':
                res = self.get_field('FormaPag',riga)
                if res=='MP12':
                    res = self.get_field('CabCliente',riga)
                else:
                    res = ''
            elif field == 'PAR_Importo':
                res = self.get_field('ImportoPagamento',riga)
            elif field == 'TipoDocumento':
                res = self.get_field('TipoDocumento',riga)
            elif field == 'Rata':
                res = self.get_field('Rata',riga)
            else:
                res = self.get_field(field,riga)
        except:
            res = 'ERR'
        return res

    def get_field(self, field, riga):
        res = ''
        for f in riga:
            if f:
                if field == f[0]:
                    res = f[1]
        if res == '':
            for f in riga:
                try:
                    res=f[1][field]
                except:
                    pass
        return res

    def get_ivasplit(self, riga):
        iva_detail = []
        #print(str(riga))
        for v in riga:
            if isinstance(v, list):
                if v:
                    if 'AliquotaIVA' in v[0][0]:
                        iva_detail.append(str(v))
        return iva_detail

    def get_payments(self, riga):
        payment_detail = []
        try:
            for v in riga:
                if isinstance(v, list):
                    if len(v)>0:
                        if 'ModalitaPagamento' in v[0][0][0]:
                            for k in v:
                                payment_detail.append(str(k))
        except:
            pass
        return payment_detail

launch = main()

