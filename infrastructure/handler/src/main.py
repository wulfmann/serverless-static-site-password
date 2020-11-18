from http import cookies
from urllib import parse

import jwt

cookie_name = 'SITE_ACCESS_TOKEN'
algorithm = 'HS256'

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

def validate_access_token(token, secret):
    try:
        jwt.decode(token, secret, algorithms=[algorithm])
        return True
    except Exception as e:
        return False

# responses
def login(redirect):
    return {
        'status': '302',
        'statusDescription': 'Login Redirect',
        'body': 'Redirecting to Login Page',
        'headers': {
            'location': [
                { 'value': f'/login/index.html?redirect={redirect}' }
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
                { 'value': create_expired_cookie(cookie_name) }
            ]
        }
    }

def handler(event, ctx):
    request = event['Records'][0]['cf']['request']
    headers = request['headers']
    secret = 'example-secret'

    print(request)
    if request['uri'].startswith('/_callback'):
        querystring = parse.parse_qs(request['querystring'])

        password = querystring.get('password')
        if password is None:
            return unauthorized()

        redirect = querystring.get('redirect')
        if redirect is None:
            redirect = '/'

        print(password)
        # TODO: handle expiration
        token = jwt.encode({}, secret, algorithm=algorithm).decode()

        return {
            'status': '302',
            'statusDescription': 'Found',
            'body': 'Redirecting',
            'headers': {
                'location': [
                    { 'value': redirect }
                ],
                'set-cookie': [
                    { 'value': create_cookie(cookie_name, token) }
                ]
            }
        }
    elif 'cookie' in headers:
        cookie = parse_cookies(headers)
        access_token = cookie.get(cookie_name)

        if access_token is not None:
            if validate_access_token(access_token, secret):
                return request

    return login(redirect=request['uri'])
