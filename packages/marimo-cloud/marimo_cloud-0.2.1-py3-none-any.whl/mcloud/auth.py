import os
import time
import http.server
import socketserver
import webbrowser
import urllib.parse
from rich.console import Console

from mcloud.config import read_credentials, write_credentials, Credentials, delete_credentials
from mcloud.constants import LOGIN_URL

console = Console()

def is_logged_in():
    """
    Checks if the user is logged in. This does not actually check if the token is valid,
    but will short circuit if the token is empty or expired.
    """
    credentials = read_credentials()
    if not credentials:
        return False
    if credentials.expires_at is not None and credentials.expires_at < time.time():
        return False
    return credentials.access_token is not None

def login():
    """
    Logs the user in. Will open a browser window to the login page and return the credentials.
    """

    # Start the login server
    with _LoginHttpServer(('localhost', 0), _LoginHttpRequestHandler) as httpd:
        # The server is running on this URL
        server_url = f'http://{httpd.server_address[0]}:{httpd.server_address[1]}'

        # Open the web browser with the redirect URL
        login_url = f'{LOGIN_URL}/cli/token?redirect_url={urllib.parse.quote(server_url)}'
        webbrowser.open(f'{LOGIN_URL}/cli/token?redirect_url={urllib.parse.quote(server_url)}')
        console.print(f"Opening [bold]{login_url}[/bold] ...")

        # Run the server until the 'token' parameter is received
        with console.status("[green]Waiting for response from browser..."):
            while httpd.running:
                httpd.handle_request()

        # The 'token' parameter is now stored in the server
        write_credentials(Credentials(
            created_at=time.time(),
            access_token=httpd.token,
            # Expires in 30 days
            expires_at=time.time() + 30 * 24 * 60 * 60,
            email=httpd.email
        ))
        console.print(f"Successfully logged in as [bold]{httpd.email}[/bold]")

def logout():
    """
    Logs the user out by deleting the credentials file.
    """
    delete_credentials()
    console.print("Successfully logged out")

def get_access_token() -> str:
    """
    Returns the access token. If the user is not logged in, this will log the user in.
    """
    credentials = read_credentials()
    if not is_logged_in() or not credentials.access_token:
        login()
        return get_access_token()
    return credentials.access_token


class _LoginHttpRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Parse the URL and its parameters
        url = urllib.parse.urlparse(self.path)
        params = urllib.parse.parse_qs(url.query)

        # If the 'token' parameter is present, store it and stop the server
        if 'token' in params:
            self.server.token = params['token'][0]
            self.server.email = params['email'][0]
            self.server.running = False

        # Redirect to success page
        self.send_response(301)
        self.send_header('Location', f'{LOGIN_URL}/cli/success')
        self.end_headers()

# This is the HTTP server
class _LoginHttpServer(socketserver.TCPServer):
    allow_reuse_address = True

    def __init__(self, server_address, RequestHandlerClass):
        super().__init__(server_address, RequestHandlerClass)
        self.token = None
        self.email = None
        self.running = True
