from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.screen_data import ScreenData

from src.core import DataManager


class ScreenStream(StreamInterface):
    def __init__(self, data_manager: DataManager) -> None:
        self.data_manager = data_manager
        self.screen_data = ScreenData()

    def get_screen_data_flag(self) -> bool:
        return True

    def get_screen_data(self, screen_data: ScreenData):
        self.screen_data = screen_data

    def processing(self):
        self.data_manager.on_screen_data_recv(self.screen_data)
