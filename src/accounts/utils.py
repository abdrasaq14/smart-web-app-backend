# import json
# import os
# from django.http import JsonResponse
# import jwt
# from functools import wraps

# from django.contrib.auth import authenticate
# import requests
# from guardian.shortcuts import assign_perm, remove_perm


# def assign_user_perm(perm, user_or_group, obj, revoke=False) -> None:
#     """Assigns permissions for a given object to a given django user or group

#     Args:
#       perm: permission to be assigned
#       user_or_group: django user or group
#       obj: object to assign to
#       revoke: is is to remove a current permission or not

#     Example:
#     `assign_user_perm('is_super_user', user, project)` (Default value = False)

#     Returns: None
#     """
#     if not revoke:
#         assign_perm(perm, user_or_group, obj)
#     else:
#         remove_perm(perm, user_or_group, obj)


# def jwt_get_username_from_payload_handler(payload):
#     username = payload.get('sub').replace('|', '.')
#     authenticate(remote_user=username)
#     return username


# def jwt_decode_token(token):
#     header = jwt.get_unverified_header(token)
#     auth0_domain = os.environ.get('AUTH0_DOMAIN')
#     jwks = requests.get('https://{}/.well-known/jwks.json'.format(auth0_domain)).json()
#     public_key = None
#     for jwk in jwks['keys']:
#         if jwk['kid'] == header['kid']:
#             public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

#     if public_key is None:
#         raise Exception('Public key not found.')

#     api_identifier = os.environ.get('API_IDENTIFIER')
#     issuer = 'https://{}/'.format(auth0_domain)
#     return jwt.decode(token, public_key, audience=api_identifier, issuer=issuer, algorithms=['RS256'])


# def get_token_auth_header(request):
#     """Obtains the access token from the Authorization Header
#     """
#     auth = request.META.get("HTTP_AUTHORIZATION", None)
#     parts = auth.split()
#     token = parts[1]

#     return token


# def requires_scope(required_scope):
#     """Determines if the required scope is present in the access token
#     Args:
#         required_scope (str): The scope required to access the resource
#     """
#     def require_scope(f):
#         @wraps(f)
#         def decorated(*args, **kwargs):
#             token = get_token_auth_header(args[0])
#             decoded = jwt.decode(token, verify=False)
#             if decoded.get("scope"):
#                 token_scopes = decoded["scope"].split()
#                 for token_scope in token_scopes:
#                     if token_scope == required_scope:
#                         return f(*args, **kwargs)
#             response = JsonResponse({'message': 'You don\'t have access to this resource'})
#             response.status_code = 403
#             return response
#         return decorated
#     return require_scope


# def get_management_token():
#     management_body = {
#         "client_id": "RLHdjXQH7M3j8Tj1ygx7t8YZ0jgZsnxH",
#         "client_secret": "fmJkyRyv5VLEixz_sDJVpMxv0P34sJVWFO0wkyRd8tRYjXVe9OBIQjVw5wyf6heg",
#         "audience": "https://dev-mgw72jpas4obd84e.us.auth0.com/api/v2/",
#         "grant_type": "client_credentials"
#     }

#     url = "https://dev-mgw72jpas4obd84e.us.auth0.com/oauth/token"
#     headers = {
#         "Content-Type": "application/json",
#     }

#     response = requests.post(url, json=management_body, headers=headers)
#     return response.json()['access_token']


import json
import os
from django.http import JsonResponse
import jwt
from functools import wraps
from django.contrib.auth import authenticate
import requests
from guardian.shortcuts import assign_perm, remove_perm


def assign_user_perm(perm, user_or_group, obj, revoke=False) -> None:
    """Assigns permissions for a given object to a given django user or group

    Args:
      perm: permission to be assigned
      user_or_group: django user or group
      obj: object to assign to
      revoke: is it to remove a current permission or not

    Example:
    `assign_user_perm('is_super_user', user, project)` (Default value = False)

    Returns: None
    """
    if not revoke:
        assign_perm(perm, user_or_group, obj)
    else:
        remove_perm(perm, user_or_group, obj)


def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub').replace('|', '.')
    authenticate(remote_user=username)
    return username


def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)
    auth0_domain = os.environ.get('AUTH0_DOMAIN')
    jwks = requests.get('https://{}/.well-known/jwks.json'.format(auth0_domain)).json()
    print("JWKS keys: {jwks}")
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    api_identifier = os.environ.get('API_IDENTIFIER')
    issuer = 'https://{}/'.format(auth0_domain)
    try:
        decoded_token = jwt.decode(token, public_key, audience=api_identifier, issuer=issuer, algorithms=['RS256'])
        print("Decoded token: {decoded_token}")
        return decoded_token
    except jwt.ExpiredSignatureError:
        print("Token has expired.")
    except jwt.InvalidAudienceError:
        print("Invalid audience.")
    except jwt.InvalidIssuerError:
        print("Invalid issuer.")
    except Exception as e:
        print("Token decoding error: {str(e)}")


def get_token_auth_header(request):
    """Obtains the access token from the Authorization Header"""
     print("Obtains the access token from the Authorization Header")
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if auth:
        print("Authorization header: {auth}")
    parts = auth.split()
    token = parts[1]
    print("Extracted token: {token}")
    return token


def requires_scope(required_scope):
    """Determines if the required scope is present in the access token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            decoded = jwt.decode(token, verify=False)
            if decoded.get("scope"):
                token_scopes = decoded["scope"].split()
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope


def get_management_token():
    management_body = {
        "client_id": "ymRc8UQkScJZM76PsbknMpZRjZWiZIo1",
        "client_secret": "0sa8I6ndW8m1QeqWFZYAIwT2VlRI8j83B3Kwm2AhOrmGLfNULqrZngmqWLHaoFLz",
        "audience": "test api for perms",
        "grant_type": "client_credentials"
    }

    url = "https://dev-mgw72jpas4obd84e.us.auth0.com/oauth/token"
    headers = {
        "Content-Type": "application/json",
    }

    response = requests.post(url, json=management_body, headers=headers)
    return response.json()['access_token']

