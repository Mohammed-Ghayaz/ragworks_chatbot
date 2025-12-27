import requests
r = requests.post('http://127.0.0.1:8000/upload', headers={'Authorization':'Bearer test'}, files={'uploaded_files': open('frontend/package.json','rb')})
print(r.status_code)
print(r.text)
