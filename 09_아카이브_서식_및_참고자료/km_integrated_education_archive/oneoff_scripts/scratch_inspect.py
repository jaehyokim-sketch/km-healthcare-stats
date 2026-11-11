import os
import requests
import openpyxl

def inspect_excel():
    excel_path = r"d:\행정\한의학 교육과 의료 통합\한의학 교육 분석.xlsx"
    if os.path.exists(excel_path):
        try:
            wb = openpyxl.load_workbook(excel_path)
            print("Excel Sheet names:", wb.sheetnames)
            for sheet in wb.sheetnames:
                ws = wb[sheet]
                print(f"=== Sheet: {sheet} (rows: {ws.max_row}, cols: {ws.max_column}) ===")
                for r in list(ws.iter_rows(values_only=True))[:30]:
                    if any(r):
                        print(r)
        except Exception as e:
            print("Error loading excel:", e)
    else:
        print("Excel file not found.")

def download_gdrive_file(file_id, output_path):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    session = requests.Session()
    response = session.get(url, stream=True)
    # Check if confirmation token is needed
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            url = f"https://drive.google.com/uc?export=download&confirm={value}&id={file_id}"
            response = session.get(url, stream=True)
            break
            
    content_type = response.headers.get('Content-Type', '')
    print(f"Response status: {response.status_code}, Content-Type: {content_type}")
    
    # Also try direct usercontent download if html returned
    if 'text/html' in content_type:
        alt_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
        response2 = session.get(alt_url, stream=True)
        if response2.status_code == 200 and 'text/html' not in response2.headers.get('Content-Type', ''):
            response = response2
            
    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=32768):
            if chunk:
                f.write(chunk)
    print(f"Downloaded to {output_path}, file size: {os.path.getsize(output_path)} bytes")

if __name__ == "__main__":
    inspect_excel()
    download_gdrive_file("1v6Obf8PU57qdBCBatOe2_wecLPlwHo2H", r"d:\행정\한의학 교육과 의료 통합\curriculum_downloaded.bin")
