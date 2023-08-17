import sqlite3
import re
import ast

def extract_data_from_file(filename):
    with open(filename, 'r') as file:
        content = file.read()
        # Using a regular expression to extract data between []
        blocks = re.findall(r'\[\(.*?\]\]', content, re.DOTALL)  # aggiunto re.DOTALL per gestire più righe
        data_list = []
        for block in blocks:
            try:
                data_list.append(ast.literal_eval(block))
            except SyntaxError:
                print(f"Error interpreting block: {block}")
    return data_list

def extract_relevant_data(data_list):
    relevant_data_list = []
    for data in data_list:
        relevant_data = {}
        has_valid_importo_ritenuta = False  # Variabile per verificare se il record ha un ImportoRitenuta valido

        for tup in data:
            # Verifica che la tupla abbia almeno 2 elementi prima di accedervi
            if len(tup) >= 2:
                if tup[0] in ['PrestatoreCedenteIdFiscaleIVA','PrestatoreCedenteDenominazione','PrestatoreCedenteCognome','CodiceFiscale', 'RagSoc1', 'Numero', 'TipoRitenuta', 'ImportoRitenuta', 'CausalePagamento']:
                    relevant_data[tup[0]] = tup[1]
                # Se il campo è "ImportoRitenuta" e ha un valore, imposta has_valid_importo_ritenuta a True
                if tup[0] == 'ImportoRitenuta' and tup[1].strip():
                    has_valid_importo_ritenuta = True

        # Aggiungi solo i record che hanno un ImportoRitenuta valido alla lista
        if has_valid_importo_ritenuta:
            relevant_data_list.append(relevant_data)

    return relevant_data_list

def create_db():
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE Data (
        PrestatoreCedenteIdFiscaleIVA TEXT,
        PrestatoreCedenteDenominazione TEXT,
        PrestatoreCedenteCognome TEXT,
        CodiceFiscale TEXT,
        RagSoc1 TEXT,
        Numero TEXT,
        TipoRitenuta TEXT,
        ImportoRitenuta TEXT,
        CausalePagamento TEXT
    )
    ''')
    conn.commit()
    return conn, cursor

def insert_data(cursor, data):
    for item in data:
        cursor.execute('''
        INSERT INTO Data (PrestatoreCedenteIdFiscaleIVA, PrestatoreCedenteDenominazione, PrestatoreCedenteCognome, CodiceFiscale, RagSoc1, Numero, TipoRitenuta, ImportoRitenuta, CausalePagamento)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (item['PrestatoreCedenteIdFiscaleIVA'], item['PrestatoreCedenteDenominazione'], item['PrestatoreCedenteDenominazione'], item['CodiceFiscale'], item['RagSoc1'], item['Numero'], item.get('TipoRitenuta', ''), item.get('ImportoRitenuta', ''), item.get('CausalePagamento', '')))

def print_data(cursor):
    cursor.execute("SELECT * FROM Data")
    rows = cursor.fetchall()

    print('Cedente | CodiceFiscaleCliente | RagSoc1 | Numero | TipoRitenuta | ImportoRitenuta | CausalePagamento')
    print('-'*100)
    for row in rows:
        print('|'.join(map(str, row)))

def main():
    data_list = extract_data_from_file('log.txt')
    relevant_data = extract_relevant_data(data_list)
    conn, cursor = create_db()
    insert_data(cursor, relevant_data)
    print_data(cursor)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    main()
