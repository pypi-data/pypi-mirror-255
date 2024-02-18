import json 
import jwt
import requests
from typing import Optional, Dict
from pydantic import ValidationError
from fastapi import Request, status, HTTPException

from app.core.config import settings
from app.utils.utils import show_error_response


def get_jwks_url(issuer_url) -> str:
    well_known_url = issuer_url + "/.well-known/openid-configuration"
    with requests.get(well_known_url) as response:
        well_known = response.json()
    if not 'jwks_uri' in well_known:
        show_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="jwks_uri not found in OpenID configuration"
            )

    return well_known['jwks_uri']


def get_jwks_public_key(access_token: str, issuer_url: str) -> str:
    # Get JWKS
    public_key_url = get_jwks_url(issuer_url)
    response = requests.get(public_key_url)
    if response.status_code != 200:
        show_error_response(
            response,
            detail="Couldn't find public signing key",
        )
    jwks = response.json()
    public_keys = {}
    for jwk in jwks['keys']:
        kid = jwk['kid']
        public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

    # Get KID from access token
    try:
        kid = jwt.get_unverified_header(access_token)['kid']
    except (
        jwt.exceptions.DecodeError, 
        jwt.exceptions.InvalidSignatureError,
        ValidationError
        ) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: {}".format(e),
        )
    except Exception as e:
        show_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.args
        )
    # Get Public Key from JWKS corresponding to the KID
    public_key = public_keys[kid]

    return public_key


def analytics_jwt_verification(jwt_token: str):
    # public_key = get_dataporten_public_key(jwt_token)
    public_key = get_jwks_public_key(
        access_token=jwt_token, issuer_url=settings.DATAPORTEN_URL
    )
    # Decode and verify signature on JWT token
    try:
        payload = jwt.decode(
            jwt_token, 
            key=public_key, 
            audience=settings.KUDAF_DATASOURCE_AUDIENCE, 
            algorithms=['RS256']
            )
    except (jwt.exceptions.DecodeError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    except Exception as e:
        show_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.args
        )
    
    return payload


async def validate_analytics_user(
    request: Request,
) -> Optional[Dict]:
    auth_header = request.headers.get("Authorization", None)
    if auth_header is None or "Bearer" not in auth_header:
        show_error_response(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_header.split(" ")[1]
    payload = analytics_jwt_verification(token)
    
    return payload


def kudaf_core_jwt_verification(jwt_token: str) -> dict:
    # Get the issuer URL from the token, for verification purposes
    try:
        decoded_jwt = jwt.decode(jwt_token, options={"verify_signature": False})
    except Exception as e:
        show_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.args
        )
    else:
        kudaf_issuer_url = decoded_jwt.get('iss')
        public_key = get_jwks_public_key(
            access_token=jwt_token, 
            issuer_url=kudaf_issuer_url
        )
        
    # Now decode it verifying the signature on the JWT token
    try:
        payload = jwt.decode(
            jwt_token, 
            key=public_key, 
            audience=settings.KUDAF_CORE_AUDIENCE, 
            algorithms=['RS256']
            )
    except (
        jwt.exceptions.DecodeError, 
        jwt.exceptions.InvalidSignatureError,
        ValidationError
        ) as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: {}".format(e),
        )
    except Exception as e:
        show_error_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.args
        )
    
    return payload


def get_kudaf_permissions(
    feide_user_id: str,
) -> list[str]:
    """
    For a given Feide user, it requests from the Kudaf Core API the 
    Variables the user has been granted access to
    """
    kudaf_core_permissions_url = settings.KUDAF_CORE_SERVER_PERMISSIONS_URL + feide_user_id + "/" + settings.DATASOURCE_ID
    response = requests.get(kudaf_core_permissions_url)
    if response.status_code != 200:
        show_error_response(
            response,
            detail="Couldn't complete request",
        )
    
    projects = [p.get('authorizations') for p in response.json() \
                if p is not None or p != "JWT"]
    
    granted_variables = []
    for token in projects:
        payload = kudaf_core_jwt_verification(token)
        granted_variables += [var for var in payload.get('variables')]

    return granted_variables
