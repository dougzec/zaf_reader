
from requests import get
from bs4 import BeautifulSoup
import re
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from google.cloud import bigquery
import datetime
from dotenv import load_dotenv

load_dotenv(override=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This is for development only; specify your front-end domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_nfc_data(qrcode_url):
   
    if "www.sefaz.rs.gov.br" not in qrcode_url:
        qrcode_url = "https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=" + qrcode_url

    response = get(qrcode_url)
    # print(response.text[:500])
    # print('\n')
    soup = BeautifulSoup(response.text, 'html.parser')
    # type(soup)

    # Coletar os itens
    table = soup.find("table", attrs={"id": 'tabResult'})

    # Initialize an empty list to hold all items
    items = []

    # Iterate through each row in the table, skipping the header row if present
    for row in table.find_all('tr'):
        # Initialize a dictionary to store the item details
        item_details = {}
        
        # Extracting details from the row
        # Adjust the class names and structure based on your actual HTML
        item_details['product_name'] = row.find('span', class_='txtTit').text.strip()
        item_details['code'] = row.find('span', class_='RCod').text.strip().split('\n')[1].strip()
        item_details['quantity'] = row.find('span', class_='Rqtd').strong.next_sibling.strip()
        item_details['quantity'] = float(item_details['quantity'].replace(',', '.'))
        item_details['unit'] = row.find('span', class_='RUN').strong.next_sibling.strip()
        item_details['unit_price'] = row.find('span', class_='RvlUnit').strong.next_sibling.strip()
        item_details['unit_price'] = float(item_details['unit_price'].replace(',', '.'))
        item_details['total_price'] = row.find('td', class_='txtTit noWrap').find('span', class_='valor').text.strip()
        item_details['total_price'] = float(item_details['total_price'].replace(',', '.'))        
        # Append the dictionary to the list
        items.append(item_details)


    # Coletar o cabeçalho
        
    header = soup.find("div", attrs={"class": 'txtCenter'})

    company = header.find_all('div')[0].text

    try:
        cnpj_raw = header.find_all('div')[1].text
        cnpj = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}', cnpj_raw).group()
        cnpj = cnpj.strip()
    except:
        cnpj = "-"

    try:
        address_raw = header.find_all('div')[2].text
        address = re.sub(r'\s+', ' ', address_raw).strip()
        address = re.sub(r'\s+,', ',', address)
    except:
        address = "-"


    # Outras informações

    # Forma de pagamento
    payment = soup.find("label", attrs={"class": 'tx'}).text
    payment = re.sub(r'\s+', ' ', payment).strip()

    # Data,numero, serie e chave de acesso
    text = soup.find("div", attrs={"id": "infos"}).text

    # Regular expressions for each field
    date_re = r'Emissão:\s*(\d{2}/\d{2}/\d{4}\s\d{2}:\d{2}:\d{2})'
    number_re = r'Número:\s*(\d+)'
    serie_re = r'Série:\s*(\d+)'
    access_key_re = r'(\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4}\s\d{4})' # r'([\d\s]{54})'

    # Search for each pattern in the text
    date_match = re.search(date_re, text)
    number_match = re.search(number_re, text)
    serie_match = re.search(serie_re, text)
    access_key_match = re.search(access_key_re, text)

    # Extracting the matched groups if found
    date = date_match.group(1) if date_match else "-"
    numero = number_match.group(1) if number_match else "-"
    serie = serie_match.group(1) if serie_match else "-"
    chave_de_acesso = access_key_match.group(1) if access_key_match else "-"



    # make a json with all the info
    data = {
        "company": company,
        "cnpj": cnpj,
        "address": address,
        "payment": payment,
        "date": date,
        "numero": numero,
        "serie": serie,
        "chave_de_acesso": chave_de_acesso,
        "items": items
    }

    return data

def upload_to_gbq(data):
    data.update({"created_at": datetime.datetime.now().isoformat()})
    client = bigquery.Client()
    table_id = "backend.notas_fiscais"
    rows_to_insert = [data]
    return client.insert_rows_json(table_id, rows_to_insert)

@app.get("/get_nfc_data_from_qrcode/")
def get_nfc_data_from_qrcode(qrcode_url: str):

    # return checkking for error and incorporating status code
    try:
        data = get_nfc_data(qrcode_url)
        return {"status": "success", "data": data}
    except:
        return {"status": "error", "data": "Invalid URL or QR code"}
    
@app.get("/get_nfc_data_from_qrcode_and_upload_to_gbq/")
def get_nfc_data_from_qrcode(qrcode_url: str, user: str = "Não informado"):

    # return checkking for error and incorporating status code
    
    try:
        data = get_nfc_data(qrcode_url)
        data.update({"user": user})
        # upload to GBQ
        errors = upload_to_gbq(data)
        if errors == []:
            return {"status": "success", "data": data}
        else:
            return {"status": "error", "data": "Error uploading to GBQ"}
    except:
        return {"status": "error", "data": "Invalid URL or QR code"}
