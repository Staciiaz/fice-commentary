import asyncio
import logging
import os

import typer
from pyftg.socket.aio.gateway import Gateway
from pyftg.utils.logging import INFO, set_logging
from typing_extensions import Annotated, Optional

from src.core import DataManager
from src.streams.audio import AudioStream
from src.streams.frame import FrameStream
from src.streams.screen import ScreenStream

app = typer.Typer(pretty_exceptions_enable=False)
logger = logging.getLogger(__name__)


async def start_process(host: str, port: int):
    host = os.environ.get("SERVER_HOST", host)
    port = int(os.environ.get("SERVER_PORT", port))
    gateway = Gateway(host, port)
    data_manager = DataManager()
    frame_stream = FrameStream(data_manager)
    audio_stream = AudioStream(data_manager)
    screen_stream = ScreenStream(data_manager)
    gateway.register_stream(frame_stream)
    gateway.register_stream(audio_stream)
    gateway.register_stream(screen_stream)
    run_game_task = gateway.run_game(["ZEN", "ZEN"], ["BlackMamba", "BlackMamba"], 1)
    stream_task = gateway.start_stream()
    await asyncio.gather(run_game_task, stream_task)


@app.command()
def main(
        host: Annotated[Optional[str], typer.Option(help="Host used by DareFightingICE")] = "127.0.0.1",
        port: Annotated[Optional[int], typer.Option(help="Port used by DareFightingICE")] = 31415):
    asyncio.run(start_process(host, port))


if __name__ == '__main__':
    set_logging(log_level=INFO)
    app()
