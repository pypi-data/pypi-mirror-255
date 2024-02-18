name = 'insertokname-authlib'
version = '1.3.0'
author = 'Hsiaoming Yang <me@lepture.com>'
homepage = 'https://insertokname-authlib.org/'
default_user_agent = f'{name}/{version} (+{homepage})'

default_json_headers = [
    ('Content-Type', 'application/json'),
    ('Cache-Control', 'no-store'),
    ('Pragma', 'no-cache'),
]
