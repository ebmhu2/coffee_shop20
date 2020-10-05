# third-party imports
import json
from flask import request, _request_ctx_stack, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

AUTH0_DOMAIN = 'udacity2020.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'coffee_shop_api'

'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    """
    Obtains the Access Token from the Authorization Header
    this function copied from lessons and Auth0 documentation
    https://auth0.com/docs/quickstart/backend/python/01-authorization
    """
    # get the header from request.
    auth = request.headers.get('Authorization', None)

    # Raise an AuthError if no header is present.
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    # split header into two parts[bearer , token].
    parts = auth.split()

    # Raise an AuthError if the header is malformed
    # malformed if first part is not bearer
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    # the header is malformed if len of parts = 1
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    # the header is malformed if len of parts > 2
    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    #  return the token part of the header
    token = parts[1]
    return token


def check_permissions(permission, payload):
    """
   check permissions
   this function copied from lessons.
   Parameters
    ----------
        permission : string
            string permission (i.e. 'post:drink').
        payload : string
            decoded jwt payload
    """
    # Raise an AuthError if permissions are not included in the payload
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    # Raise an AuthError if the requested permission
    # string is not in the payload permissions array
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 403)
    return True


def verify_decode_jwt(token):
    """
     verify_decode_jwt
     this function copied from lessons.
     Parameters
      ----------
          token : string
              a json web token
    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    #  Auth0 token should be with key id (kid)
    # should verify the token using Auth0 /.well-known/jwks.json
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # decode the payload from the token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, '
                               'check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    """
    requires_auth
    this function copied from lessons.
    Parameters
     ----------
         permission : string
             string permission (i.e. 'post:drink')
    """
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # use the get_token_auth_header method to get the token
            token = get_token_auth_header()
            try:
                # use the verify_decode_jwt method to decode the jwt
                payload = verify_decode_jwt(token)
            except:
                abort(401)
            # use the check_permissions method validate
            # claims and check the requested permission
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
