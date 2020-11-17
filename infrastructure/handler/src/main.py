from http import cookies

cookie_name = 'SITE_ACCESS_TOKEN'

# UTILS
def parse_cookies(headers):
    cookie = cookies.SimpleCookie()
    cookie.load(headers['cookie'][0]['value'])
    return {
        key: value.value
        for key, value in cookie.items()
    }

def create_expired_cookie(name):
    return create_cookie(name, '', {
        'path': '/',
        'expires': 'Sun Feb 01 1970 00:00:00 GMT-0600 (Central Standard Time)'
    })

def create_cookie(name, value, attributes={}):
    cookie = cookies.SimpleCookie()
    cookie[name] = value
    for attr in attributes:
        cookie[name][attr] = attributes[attr]
    return cookie.output(header='').strip()

def validate_access_token(token):
    return True

# responses
def login(redirect):
    return {
        'status': '302',
        'statusDescription': 'Login Redirect',
        'body': 'Redirecting to Login Page',
        'headers': {
            'location': [
                { 'value': '/login' }
            ],
            'set-cookie': [
                { 'value': create_expired_cookie(cookie_name) }
            ]
        }
    }

def unauthorized():
    return {
        'status': '401',
        'statusDescription': 'Unauthorized',
        'body': 'Unauthorized',
        'headers': {
            'set-cookie': [
                { 'value': create_expired_cookie('TOKEN') }
            ]
        }
    }

def handler(event, ctx):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']

    if request['uri'].startswith('/_callback'):
        print(request)
        request['uri'] = '/'
        return request
    elif 'cookie' in headers:
        cookie = parse_cookies(headers)
        access_token = cookie.get(cookie_name)
        if access_token is not None:
            if validate_access_token(access_token):
                return request

    return login(redirect=request['uri'])
