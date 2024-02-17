# MJMS - A client for  https://mailsrv.marcusj.org

**Usage**

```python3
from mjms import MJMS

mjms = MJMS('API_KEY')

mjms.send_mail('example@email.com', 'This is the subject!', html='<h1>Hello world</h1>') # the first argument can also be a list of emails. text is also a valid kwarg

res = mjms.verify_email('example@email.com') 
# {'ok': True, 'token': 'XXXXXXX'} or {'ok': False, 'error': '...'}
print(mjms.check_verified(res['token']))
```

API keys can be obtained by visiting https://mailsrv.marcusjt.tech and signing in with [replit](https://replit.com).