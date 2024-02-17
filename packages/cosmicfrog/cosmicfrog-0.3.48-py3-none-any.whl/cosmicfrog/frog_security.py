"""
    Functions for service authentication
"""

from typing import Dict
import os
import httpx
import jwt
from .sync_wrapper import sync_wrapper


# Environment
SECURITY_TIMEOUT = os.getenv("SECURITY_TIMEOUT") or 20.0
ADMIN_APP_KEY = os.getenv("ADMIN_APP_KEY")  # Note: Deliberate, no defaults for urls
ATLAS_SERVICE_URL = os.getenv("ATLAS_SERVICE_URL")
ATLAS_API_BASE_URL = os.getenv("ATLAS_API_BASE_URL")


def validate_jwt(jwt_token):
    """
    Offline validation for api token
    This will throw DecodeError if token cannot be decoded
    """
    jwt.decode(jwt_token, options={"verify_signature": False})


def validate_bearer_token(bearer_token):
    """
    Fast offline validation of bearer token
    Will throw if invalid, else can be checked online
    """
    assert bearer_token is not None, "Bearer token is missing"
    assert bearer_token.startswith("Bearer "), "Bearer token is missing prefix"
    assert bearer_token.strip() != "Bearer", "Bearer token is missing jwt"
    jwt_token = bearer_token[7:]
    validate_jwt(jwt_token)


def extract_credentials(*args):
    """
    Utility to support calling security related functions with a header or individual keys
    """
    if len(args) == 1 and hasattr(args[0], "get"):
        headers = args[0]
        app_key = headers.get("X-App-KEY", None)
        api_key = headers.get("X-API-KEY", None)
        bearer_token = headers.get("Authorization", None)
    else:
        app_key, api_key, bearer_token = args

    return app_key, api_key, bearer_token


def _make_header(app_key: str, api_key: str, bearer_token: str) -> Dict[str, str]:
    """
    Create header for platform api calls
    """

    if not (app_key or api_key or bearer_token):
        assert False, "No authentication was provided (all keys empty)"

    # Basic bearer key validation
    if not (app_key or api_key):
        validate_bearer_token(bearer_token)

    base_url = os.getenv("ATLAS_API_BASE_URL")

    assert base_url

    # set up header with app key or api key depending on value set
    if app_key:
        header_key = "X-APP-KEY"
    else:
        header_key = "X-API-KEY"

    return {header_key: app_key or api_key or bearer_token.replace("Bearer ", "")}


async def _get_app_key_async(*args):
    """
    Given an api key or bearer token, fetch an app key

    Warning: Ensure keys are authenticated before calling, will use sub claim
    """

    assert ADMIN_APP_KEY, "ADMIN_APP_KEY is not configured"
    assert ATLAS_SERVICE_URL, "ATLAS_SERVICE_URL is not configured"

    app_key, api_key, bearer_token = extract_credentials(*args)

    if app_key:
        return app_key

    if not api_key:
        validate_bearer_token(bearer_token)
        api_key = bearer_token.replace("Bearer ", "")
    else:
        validate_jwt(api_key)

    # Get client ID from the token
    decoded_data = jwt.decode(api_key, options={"verify_signature": False})

    data = {"userId": decoded_data["sub"], "name": "Issuing Cosmic Frog key"}

    headers = {"x-app-key": ADMIN_APP_KEY}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{ATLAS_SERVICE_URL}", headers=headers, json=data, timeout=SECURITY_TIMEOUT
        )

        if response.status_code != 200:
            raise ValueError(f"Failed to get a token: {response.content}")

        return response.json().get("appkey")


_get_app_key = sync_wrapper(_get_app_key_async)


async def _get_account_async(*args):
    """
    Fetch account details from platform

    Pass (app_key, api_key, bearer_token) or (request.headers)

    """

    assert ATLAS_API_BASE_URL, "ATLAS_API_BASE_URL is not configured"

    app_key, api_key, bearer_token = extract_credentials(*args)

    new_headers = _make_header(app_key, api_key, bearer_token)

    url = f'{ATLAS_API_BASE_URL.strip("/")}/account'

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=new_headers, timeout=SECURITY_TIMEOUT)
        response.raise_for_status()
        return response.json()


_get_account = sync_wrapper(_get_account_async)


async def socket_secured_async(app_key: str, api_key: str, bearer_token: str):
    """
    Used for socket.io
    """
    acc = await _get_account_async(app_key, api_key, bearer_token)

    assert acc

    return acc


socket_secured = sync_wrapper(socket_secured_async)
