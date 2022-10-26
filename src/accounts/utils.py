import json
import os

from django.contrib.auth import authenticate
import jwt
import requests
from guardian.shortcuts import assign_perm, remove_perm


def assign_user_perm(perm, user_or_group, obj, revoke=False) -> None:
    """Assigns permissions for a given object to a given django user or group

    Args:
      perm: permission to be assigned
      user_or_group: django user or group
      obj: object to assign to
      revoke: is is to remove a current permission or not

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
    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    if public_key is None:
        raise Exception('Public key not found.')

    api_identifier = os.environ.get('API_IDENTIFIER')
    issuer = 'https://{}/'.format(auth0_domain)
    return jwt.decode(token, public_key, audience=api_identifier, issuer=issuer, algorithms=['RS256'])
