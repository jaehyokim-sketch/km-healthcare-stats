import os
import requests

file_id = "1Mc3xA1YDVu6Km515MQd0wHjYzr7x3Ws-"
url = f"https://drive.google.com/uc?export=download&id={file_id}"
session = requests.Session()
response = session.get(url, stream=True)

for key, value in response.cookies.items():
    if key.startswith('download_warning'):
        url = f"https://drive.google.com/uc?export=download&confirm={value}&id={file_id}"
        response = session.get(url, stream=True)
        break

content_type = response.headers.get('Content-Type', '')
print(f"Response status: {response.status_code}, Content-Type: {content_type}")

if 'text/html' in content_type:
    alt_url = f"https://drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t"
    response2 = session.get(alt_url, stream=True)
    if response2.status_code == 200 and 'text/html' not in response2.headers.get('Content-Type', ''):
        response = response2

output_path = r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\kascom_evaluation_standards.bin"
with open(output_path, "wb") as f:
    for chunk in response.iter_content(chunk_size=32768):
        if chunk:
            f.write(chunk)

print(f"Downloaded to {output_path}, file size: {os.path.getsize(output_path)} bytes")

# Check header
with open(output_path, "rb") as f:
    header = f.read(100)
    print("Header:", header[:32])

if header.startswith(b"%PDF"):
    pdf_path = r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\kascom_evaluation_standards.pdf"
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    os.rename(output_path, pdf_path)
    print("Renamed to kascom_evaluation_standards.pdf")
elif header.startswith(b"PK"):
    print("It is a ZIP/Office/HWPX file!")
