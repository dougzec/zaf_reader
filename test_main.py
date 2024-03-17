from main import get_nfc_data

def test_run():
    qrcode_url = 'https://www.sefaz.rs.gov.br/NFCE/NFCE-COM.aspx?p=43201293015006000890651010001540401411138155|2|1|1|A98DB9939667C7114E70D79C2850352E7AF690FC'
    
    data = get_nfc_data(qrcode_url)
    
    assert 'date' in data.keys()