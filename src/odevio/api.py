#                                   #
#   Requests to Odevio web server  #
#                                   #
import datetime
import json
import time

import jwt
import requests
from click import ClickException
from rich.prompt import Prompt

from odevio.helpers import print_validation_error
from odevio.settings import (
    API_BASE_URL,
    API_KEY_ENV_VAR,
    console,
    delete_jwt_token,
    get_api_key,
    get_jwt_token,
    write_jwt_token,
)


def _request(method, route, params=None, data=None, files=None, authorization=True, auth_data=None, json_decode=True, tries=5, sse=False, json_body=None):
    """ General request wrapper for Odevio API.

    :return dict of the JSON returned by the API or False if an error occurred
    """
    headers = dict()
    if not sse:
        headers["Accept"] = "application/json"
    if authorization:
        if auth_data is None:
            auth_data = dict()

        auth_headers = get_authorization_header(**auth_data)

        if not auth_headers:
            return False

        headers["Authorization"] = auth_headers

    try:
        response = requests.request(
            method,
            f"{API_BASE_URL}{'/events' if sse else '/api/v1'}{route}",
            headers=headers,
            params=params,
            data=data,
            files=files,
            json=json_body,
            stream=sse
        )
    except requests.exceptions.ConnectionError:
        if tries > 0:
            time.sleep(2)
            return _request(method, route, params, data, files, authorization, auth_data, json_decode, tries-1, sse, json_body)
        raise ClickException("Server not available")

    if response.ok:
        if sse:
            return response
        if json_decode:
            return response.json()
        else:
            return response.content
    else:
        if response.status_code in [400, 401]:
            if response.status_code == 401 and get_api_key():
                # Never fall back to an interactive prompt when an API key was supplied: an automated
                # caller has no way to answer it and would hang or crash instead of failing clearly.
                raise ClickException(
                    f"Authentication failed with the API key from {API_KEY_ENV_VAR}. "
                    "Check the key, or create a new one with 'odevio apikey new'."
                )
            error = response.json()
            print_validation_error(console, error)
            return False
        elif response.status_code == 402:
            console.print(f"Error: {response.json()['detail']}")
            console.print("To upgrade your account, please go to https://odevio.com/plans")
            return False
        elif response.status_code == 403:
            console.print(f"Permission error: {response.json()['detail']}")
            return False
        elif response.status_code == 404:
            raise NotFoundException()
        elif response.status_code in [302, 503] and tries > 0:  # Update or maintenance
            time.sleep(2)
            return _request(method, route, params, data, files, authorization, auth_data, json_decode, tries-1, sse, json_body)
        else:
            if response.status_code == 503:
                raise ClickException("The server is currently in maintenance. Please try again in a few moments.")
            error = response.reason
            raise ClickException(f"{method.upper()} {route} failed: {error}")


def get(route, params=None, authorization=True, auth_data=None, json_decode=True, sse=False):
    """ GET method wrapper for Odevio API.

    :return dict of the JSON returned by the API or False if an error occurred
    """
    return _request("get", route, params=params, authorization=authorization, auth_data=auth_data, json_decode=json_decode, sse=sse)


def post(route, authorization=True, json_data=None, params=None, files=None, auth_data=None, json_body=None):
    """ POST method wrapper for Odevio API.

    ``json_data`` is form-encoded (used by the file-upload endpoints); ``json_body`` sends an
    ``application/json`` request body, which is what the JSON-only endpoints expect.

    :return dict of the JSON returned by the API or False if an error occurred
    """
    return _request("post", route, params=params, data=json_data, files=files, authorization=authorization, auth_data=auth_data, json_body=json_body)


def put(route, authorization=True, json_data=None, params=None, files=None, json_body=None):
    """ PUT method wrapper for Odevio API

    :return dict of the JSON returned by the API or False if an error occurred
    """
    if json_data:
        json_data = {key: value for key, value in json_data.items() if value is not None}
    if files:
        files = {key: value for key, value in files.items() if value is not None}
    return _request("put", route, params=params, data=json_data, files=files, authorization=authorization, json_body=json_body)


def delete(route, authorization=True, params=None, auth_data=None, json_decode=True):
    """ DELETE method wrapper for Odevio API.

    :return True if the deletion was successful or False if an error occurred
    """
    return _request("delete", route, params=params, authorization=authorization, auth_data=auth_data, json_decode=json_decode)


#                                   #
#   JWT Authentication processes    #
#                                   #


def _generate_new_token(email, password):
    """ Requests the JWT token to the Odevio API by providing email and password.

    :return either returns the JWT token or False if the request failed.
    """
    try:
        response = requests.post(
            url=f"{API_BASE_URL}/api-token-auth/",
            json={
                "email": email,
                "password": password,
            },
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        return json.loads(response.content.decode())["token"]
    else:
        if response.status_code in [400, 401, 403]:
            print_validation_error(console, json.loads(response.content.decode()))
            return False
        else:
            error = response.reason
            raise ClickException(f"Authentication failed: {error}")


def _refresh_token(token):
    try:
        response = requests.post(
            url=f"{API_BASE_URL}/api-token-refresh/",
            json={"token": token},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        return json.loads(response.content.decode())["token"]
    else:
        if response.status_code in [400, 401, 403]:
            print_validation_error(console, json.loads(response.content.decode()))
            return False
        else:
            error = response.reason
            raise ClickException(f"Authentication failed: {error}")


def get_authorization_header(email=None, password=None):
    """ Get the authorization header, either from an API key, or from a JWT token local or remote. """
    # An API key takes precedence over the cached token so that an automated environment behaves the same
    # on every machine, and never falls back to whichever account happens to be signed in locally.
    # Explicit credentials still go through the token flow, so "odevio signin" keeps working as before.
    api_key = get_api_key()
    if api_key and email is None and password is None:
        return f"Token {api_key}"

    token = get_jwt_token()
    if token:
        decoded = jwt.decode(token, options={"verify_signature": False})
        if decoded['exp'] <= datetime.datetime.utcnow().timestamp():
            token = _refresh_token(token)
            if token:
                write_jwt_token(token)
                return f"JWT {token}"
        else:
            return f"JWT {token}"
    if email is None or password is None:
        console.print("If you already have an account, please enter your credentials and we will log you in :")
    if not email:
        email = Prompt.ask("E-mail")
    if not password:
        password = Prompt.ask("Password", password=True)
    token = _generate_new_token(email, password)
    # if the API call for a JWT token failed return False.
    if not token:
        return False

    write_jwt_token(token)
    return f"JWT {token}"


def disconnect():
    """ Removes the JWT token from the local machine. """
    if get_jwt_token() is not None:
        delete_jwt_token()
        console.print("You have been disconnected. See you soon...")
    else:
        console.print("You have already been logged out.")


class NotFoundException(Exception):
    pass
