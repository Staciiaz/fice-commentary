import asyncio
import os
import logging

import typer
from pyftg.utils.gateway import get_async_gateway
from pyftg.utils.logging import DEBUG, set_logging
from typing_extensions import Annotated, Optional

from src.core import FightingStream

app = typer.Typer(pretty_exceptions_enable=False)
logger = logging.getLogger(__name__)


async def start_process(host: str, port: int):
    host = os.environ.get("SERVER_HOST", host)
    port = int(os.environ.get("SERVER_PORT", port))
    try:
        gateway = get_async_gateway(host, port, use_grpc=False)
        stream = FightingStream()
        gateway.register_stream(stream)
        await gateway.start_stream()
        await gateway.close()
    except ConnectionResetError:
        logger.info("Connection closed by server")


@app.command()
def main(
        host: Annotated[Optional[str], typer.Option(help="Host used by DareFightingICE")] = "127.0.0.1",
        port: Annotated[Optional[int], typer.Option(help="Port used by DareFightingICE")] = 31415):
    asyncio.run(start_process(host, port))


if __name__ == '__main__':
    set_logging(log_level=DEBUG)
    app()
