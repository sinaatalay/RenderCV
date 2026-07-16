import threading
import time
import webbrowser
from typing import Annotated

import typer
import uvicorn

from rendercv.web.web_app import app as web_app

from ..app import app
from ..error_handler import handle_user_errors


@app.command(
    name="web",
    help=(
        "Start the RenderCV web editor for live editing and PDF compilation. "
        "Example: [yellow]rendercv web[/yellow]"
    ),
)
@handle_user_errors
def cli_command_web(
    host: Annotated[
        str,
        typer.Option(
            help="The host address to bind the server to.",
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            help="The port number to run the server on.",
        ),
    ] = 8000,
    no_browser: Annotated[
        bool,
        typer.Option(
            "--no-browser",
            help="Disable automatically opening the web browser.",
        ),
    ] = False,
):
    """Start the RenderCV web editor and server."""
    typer.echo(f"Starting RenderCV web editor on http://{host}:{port}")
    
    if not no_browser:
        def open_browser():
            # Wait for uvicorn to bind to port and start accepting requests
            time.sleep(1.2)
            webbrowser.open(f"http://{host}:{port}")
            
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()

    uvicorn.run(web_app, host=host, port=port)
