from qrreader import capture_qr
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
from datetime import datetime

def run():
    qr = capture_qr()
    # print(qr)
#     qr = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43201293015006000890651010001540401411138155|2|1|1|A98DB9939667C7114E70D79C2850352E7AF690FC'
    # url_frame = 'https://www.sefaz.rs.gov.br/ASP/AAE_ROOT/NFE/SAT-WEB-NFE-NFC_QRCODE_1.asp?p=43201293015006000890651010001540401411138155%7C2%7C1%7C1%7CA98DB9939667C7114E70D79C2850352E7AF690FC'

    response = get(qr)
    # print(response.text[:500])
    # print('\n')
    soup = BeautifulSoup(response.text, 'html.parser')
    # type(soup)

    url_frame = soup.find_all('iframe')[0]['src']
    url_frame

    response = get(url_frame)
    # print(response.text[:500])
    # print('\n')
    soup = BeautifulSoup(response.text, 'html.parser')
    # type(soup)


    gdp_table = soup.find_all("table", attrs={"class": 'NFCCabecalho'})[3]
    # print(type(gdp_table))
    # print(len(gdp_table))


    # gdp_table = soup.find("table", attrs={"class": "wikitable"})
    gdp_table_data = gdp_table.find_all("tr")  # contains 2 rows

    # Get all the headings of Lists
    headings = []
    for td in gdp_table_data[0].find_all("td"):
        # remove any newlines and extra spaces from left and right
        headings.append(td.text)

    data = []

    for row in gdp_table_data[1:]:
        data_inter = {}
        for col, heading in zip(row.find_all('td'), headings):

            valor = col.text
            if heading in ['Qtde', 'Vl Unit', 'Vl Total']:
                valor = valor.replace(',', '.')
                valor = float(valor)
            else:
                pass

            data_inter.update({heading: valor})
        data.append(data_inter)

    # print(data)


    loja = soup.find_all("table", attrs={"class": 'NFCCabecalho'})[0].find_all('td')[1].text
    dia = soup.find_all("td", attrs={'class': 'NFCCabecalho_SubTitulo'})[2].text.split('Data de Emissão: ')[-1]
    dia = datetime.strptime(dia, '%d/%m/%Y  %H:%M:%S')
    nota = soup.find_all("td", attrs={'class': 'NFCCabecalho_SubTitulo'})[2].text.split('\n')[1].split('NFC-e nº: ')[-1]
    nota = int(nota)


    df = pd.DataFrame(data)
    df['Loja'] = loja
    df['Dia'] = dia
    df['Nota'] = nota
    df


    try:
        df_base = pd.read_csv('database.csv', )
        df_base = df_base[df_base['Nota'] != nota]
        df_base = pd.concat([df_base, df])
    except:
        df_base = df.copy()
        
    df_base.to_csv('database.csv', index=None)
        
    print('Feito')
    
    return df