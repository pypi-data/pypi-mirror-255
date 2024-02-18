import base64
import hashlib
import secrets
import socket
import webbrowser
from contextlib import closing
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Optional, Sequence
from urllib.parse import parse_qs, urlencode, urlparse

import requests
from pydantic import parse_obj_as

from unfolded.data_sdk.environment import AUTH_CONFIGS, AuthEnvironment
from unfolded.data_sdk.errors import AuthenticationError
from unfolded.data_sdk.models import Credentials
from unfolded.data_sdk.utils import raise_for_status

# Whitelisted ports for a redirect_uri on localhost
REDIRECT_URI_PORT_RANGE = range(8050, 8054)


def authenticate(
    *,
    auth_env: AuthEnvironment = AuthEnvironment.PRODUCTION,
) -> Credentials:
    auth_config = AUTH_CONFIGS[auth_env]

    nonce = secrets.token_urlsafe(32)
    code_verifier = secrets.token_urlsafe(32)

    # The last = needs to be stripped off
    # https://www.oauth.com/oauth2-servers/pkce/authorization-request/
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode()).digest()
    ).rstrip(b"=")

    # Choose hostname and port
    hostname = "localhost"
    port = find_available_port(hostname, REDIRECT_URI_PORT_RANGE)
    redirect_uri = f"http://{hostname}:{port}"

    authorization_params = {
        "response_type": "code",
        "response_mode": "query",
        "audience": auth_config.audience,
        "state": nonce,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "client_id": auth_config.client_id,
        "redirect_uri": redirect_uri,
        "scope": auth_config.scope,
    }

    authorization_url = f"{auth_config.auth_url}/authorize?" + urlencode(
        authorization_params
    )
    webbrowser.open(authorization_url)

    # Receive token from successful flow
    code = receive_token(hostname=hostname, port=port, nonce=nonce)

    refresh_token_params = {
        "grant_type": "authorization_code",
        "audience": auth_config.audience,
        "client_id": auth_config.client_id,
        "code_verifier": code_verifier,
        "code": code,
        "redirect_uri": redirect_uri,
    }

    refresh_token_url = f"{auth_config.auth_url}/oauth/token"
    r = requests.post(refresh_token_url, json=refresh_token_params)
    raise_for_status(r)
    return parse_obj_as(Credentials, r.json())


def receive_token(
    *, port: int, hostname: str = "localhost", global_timeout: int = 600, nonce: str
) -> str:
    """Set up HTTPServer on localhost to receive code and state query params from OAuth2

    Kwargs:
        hostname (str): hostname for server to accept "code". Defaults to "localhost".
        port (int): port for HTTPServer.
        global_timeout (int, optional): Timeout (in seconds) beyond which the Python server shuts down. Defaults to 600.

    Returns:
        Tuple[str, Optional[str]]: code and state
    """
    code: Optional[str] = None

    class Handler(BaseHTTPRequestHandler):
        """Custom request handler to intercept GET query parameters"""

        def do_GET(self) -> None:
            query = urlparse(self.path).query
            parsed = parse_qs(query)

            # The error is expected to be one of the enum values at the bottom of this url:
            # https://www.oauth.com/oauth2-servers/authorization/the-authorization-response/
            error = parsed.get("error", [""])[0]
            if error:
                self.send_response(HTTPStatus.FORBIDDEN)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                message = f"Error message: {error}"
                self.wfile.write(message.encode())
                return

            nonlocal code
            code = parsed.get("code", [""])[0]
            state = parsed.get("state", [""])[0]

            if not state or state != nonce:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                message = f"Internal error: state was missing or not equal to nonce ({nonce})."
                self.wfile.write(message.encode())
                return

            if not code:
                self.send_response(HTTPStatus.BAD_REQUEST)
                self.send_header("Content-type", "text/html")
                self.end_headers()

                message = "Internal error: code was not sent from authorize page."
                self.wfile.write(message.encode())
                return

            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            message = "Success! You may now close this page."
            self.wfile.write(message.encode())

        # Turn off default printing of HTTP requests
        def log_request(
            self, *args: Any, **kwargs: Any  # pylint: disable=unused-argument
        ) -> None:
            return

    with HTTPServer((hostname, port), Handler) as httpd:
        # NOTE(kyle): I _think_ we only need to call `handle_request` once, rather than in a loop,
        # and it will automatically time out after `timeout`
        # https://docs.python.org/3/library/socketserver.html#socketserver.BaseServer.timeout
        httpd.timeout = global_timeout
        httpd.handle_request()

    if not code:
        raise AuthenticationError(
            "Timeout while waiting for user to finish authentication."
        )

    return code


def find_available_port(host: str, port_range: Sequence[int]) -> int:
    """Find available/open port in range on specified host"""
    for port in port_range:
        if check_socket(host, port):
            return port

    raise OSError(f"No port in range {port_range} is available")


def check_socket(host: str, port: int) -> bool:
    """Check if port is available

    https://stackoverflow.com/a/35370008

    Returns True if port is available, otherwise False
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        return sock.connect_ex((host, port)) != 0
