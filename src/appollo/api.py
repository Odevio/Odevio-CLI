#                                   #
#   Requests to Appollo web server  #
#                                   #
import datetime
import json

import jwt
from click import ClickException

import requests
from rich.prompt import Prompt
from appollo.helpers import print_validation_error

from appollo.settings import API_BASE_URL, console, get_jwt_token, write_jwt_token, delete_jwt_token


def get(route, params=None, authorization=True, auth_data=None, json_decode=True):
    """ GET method wrapper for Appollo API.

    :return dict of the JSON returned by the API or False if an error occurred
    """
    headers = dict()
    headers["Accept"] = "application/json"
    if authorization:
        if auth_data is None:
            auth_data = dict()

        auth_headers = get_authorization_header(**auth_data)

        if not auth_headers:
            return False

        headers["Authorization"] = auth_headers

    try:
        response = requests.get(
            f"{API_BASE_URL}/api/v1{route}",
            headers=headers,
            params=params,
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        if json_decode:
            return response.json()
        else:
            return response.content
    else:
        if response.status_code in [400, 401, 403]:
            error = response.json()
            print_validation_error(console, error)
            return False
        elif response.status_code == 404:
            raise NotFoundException()
        else:
            error = response.reason
            raise ClickException(f"GET {route} failed: {error}")


def post(route, authorization=True, json_data=None, params=None, files=None, auth_data=None):
    """ POST method wrapper for Appollo API.

    :return dict of the JSON returned by the API or False if an error occurred
    """
    headers = dict()
    headers["Accept"] = "application/json"
    if authorization:
        if auth_data is None:
            auth_data = dict()

        auth_headers = get_authorization_header(**auth_data)

        if not auth_headers:
            return False

        headers["Authorization"] = auth_headers

    try:
        response = requests.post(
            f"{API_BASE_URL}/api/v1{route}",
            headers=headers,
            params=params,
            data=json_data,
            files=files,
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        return response.json()
    else:
        if response.status_code in [400, 401, 403]:
            error = response.json()
            print_validation_error(console, error)
        elif response.status_code == 404:
            raise NotFoundException()
        else:
            error = response.reason
            raise ClickException(f"POST {route} failed: {error}")

def put(route, authorization=True, json_data=None, params=None, files=None):
    """ PUT method wrapper for Appollo API

    :return dict of the JSON returned by the API or False if an error occurred
    """

    headers = {}

    if authorization:
        auth_headers = get_authorization_header()

        if not auth_headers:
            return False

        headers["Authorization"] = auth_headers

    if json_data:
        json_data = {key: value for key, value in json_data.items() if value is not None}
    if files:
        files = {key: value for key, value in files.items() if value is not None}

    try:
        response = requests.put(
            f"{API_BASE_URL}/api/v1{route}",
            headers=headers,
            params=params,
            data=json_data,
            files=files,
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        return response.json()
    else:
        if response.status_code in [400, 401, 403]:
            error = response.json()
            print_validation_error(console, error)
        elif response.status_code == 404:
            raise NotFoundException()
        else:
            error = response.reason
            raise ClickException(f"PUT {route} failed: {error}")


def delete(route, authorization=True, params=None, auth_data=None):
    """ DELETE method wrapper for Appollo API.

    :return True if the deletion was successful or False if an error occurred
    """
    headers = dict()
    headers["Accept"] = "application/json"
    if authorization:
        if auth_data is None:
            auth_data = dict()

        auth_headers = get_authorization_header(**auth_data)

        if not auth_headers:
            return False

        headers["Authorization"] = auth_headers

    try:
        response = requests.delete(
            f"{API_BASE_URL}/api/v1{route}",
            headers=headers,
            params=params,
        )
    except requests.exceptions.ConnectionError:
        raise ClickException("Server not available")

    if response.ok:
        return True
    else:
        if response.status_code in [400, 401, 403]:
            error = response.json()
            print_validation_error(console, error)
        elif response.status_code in [404]:
            console.print("Cannot delete something that does not exist.")
        else:
            error = response.reason
            raise ClickException(f"DELETE {route} failed: {error}")


#                                   #
#   JWT Authentication processes    #
#                                   #


def _generate_new_token(email, password):
    """ Requests the JWT token to the Appollo API by providing email and password.

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
    """ Get the authorization header (JWT token), either locally or remotely. """
    token = get_jwt_token()
    if token:
        decoded = jwt.decode(token, options={"verify_signature": False})
        if decoded['exp'] <= datetime.datetime.utcnow().timestamp():
            token = _refresh_token(token)
            write_jwt_token(token)
    else:
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
