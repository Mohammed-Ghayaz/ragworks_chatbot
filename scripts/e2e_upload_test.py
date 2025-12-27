import requests

BASE = 'http://127.0.0.1:8000'

# Register a test user
res = requests.post(f'{BASE}/auth/register', json={'name': 'E2E Tester', 'email': 'e2e@example.com', 'password': 'secret'})
print('register', res.status_code, res.text)
if res.status_code != 200:
    # maybe user exists; try login
    res = requests.post(f'{BASE}/auth/login', json={'email': 'e2e@example.com', 'password': 'secret'})
    print('login', res.status_code, res.text)

token = res.json()['access_token']
print('got token', token[:16])

# Upload a file
files = {'uploaded_files': open('frontend/package.json','rb')}
headers = {'Authorization': f'Bearer {token}'}
r = requests.post(f'{BASE}/upload', headers=headers, files=files, timeout=300)
print('upload', r.status_code)
print(r.text)
