from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.screen_data import ScreenData

from src.core import DataManager


class ScreenStream(StreamInterface):
    def __init__(self, data_manager: DataManager) -> None:
        self.data_manager = data_manager

    def get_screen_data_flag(self) -> bool:
        return True

    def get_screen_data(self, screen_data: ScreenData):
        self.data_manager.on_screen_data_recv(screen_data)
