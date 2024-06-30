from main import get_nfc_data, upload_to_gbq

def test_run():
    qrcode_url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43201293015006000890651010001540401411138155|2|1|1|A98DB9939667C7114E70D79C2850352E7AF690FC'
    
    data = get_nfc_data(qrcode_url)
    
    assert 'date' in data.keys()

def test_upload_to_gbq():
    data = {
    "company": "COMPANHIA ZAFFARI COMERCIO E INDUSTRIA",
    "cnpj": "93.015.006/0008-90",
    "address": "RUA PARAGUAI, 100,, RIO BRANCO, PORTO ALEGRE, RS",
    "payment": "Cartão de Crédito",
    "date": "02/12/2020 19:18:11",
    "numero": "154040",
    "serie": "101",
    "chave_de_acesso": "4320 1293 0150 0600 0890 6510 1000 1540 4014 1113 8155",
    "items": [
      {
        "product_name": "PAO CACETINHO               .ZAF",
        "code": "2650230000004",
        "quantity": 0.284,
        "unit": "KG",
        "unit_price": 8.98,
        "total_price": 2.55
      }
    ]
  }

    response = upload_to_gbq(data)
    
    assert response == []

def test_read_and_write():
    qrcode_url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43201293015006000890651010001540401411138155|2|1|1|A98DB9939667C7114E70D79C2850352E7AF690FC'
    
    data = get_nfc_data(qrcode_url)

    response = upload_to_gbq(data)

    assert response == []