import requests
import json
import os

pdf_path = r'c:\Users\alexj\Desktop\ktu-result\result_AIK S4.pdf'
if not os.path.exists(pdf_path):
    print("PDF not found, skipping full test.")
    exit(0)

try:
    print(f"Testing upload of {pdf_path}...")
    files = {'pdf_file': ('test.pdf', open(pdf_path, 'rb'), 'application/pdf')}
    data = {'batch_year': '2022'}
    
    r = requests.post('http://127.0.0.1:8000/upload', files=files, data=data)
    print(f"Status Code: {r.status_code}")
    
    res = r.json()
    print("Response:")
    print(json.dumps(res, indent=2))
    
    if res.get('status') == 'success' and 'session_id' in res:
        session_id = res['session_id']
        print(f"\nDownloading generated Excel for session {session_id}...")
        
        down_r = requests.get(f'http://127.0.0.1:8000/download/{session_id}')
        if down_r.status_code == 200:
            out_file = os.path.join(os.environ.get('TEMP', '.'), 'test_output.xlsx')
            with open(out_file, 'wb') as f:
                f.write(down_r.content)
            print(f"Excel downloaded successfully to: {out_file} ({len(down_r.content)} bytes)")
        else:
            print(f"Download failed with status {down_r.status_code}")
except Exception as e:
    print(f"Error: {e}")
