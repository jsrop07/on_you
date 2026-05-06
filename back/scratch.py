import json
import urllib.request
try:
    req = urllib.request.Request(
        'http://127.0.0.1:8001/users/login',
        data=b'{"email":"test@test.com", "password":"test"}',
        headers={'Content-Type':'application/json'}
    )
    urllib.request.urlopen(req)
except Exception as e:
    print(e)
    if hasattr(e, 'read'):
        print(e.read().decode())
