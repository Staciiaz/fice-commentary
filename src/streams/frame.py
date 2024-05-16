from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.frame_data import FrameData
from pyftg.models.round_result import RoundResult

from src.core import DataManager


class FrameStream(StreamInterface):
    def __init__(self, data_manager: DataManager):
        self.data_manager = data_manager
        self.frame_data = FrameData()

    def get_frame_data_flag(self) -> bool:
        return True

    def get_information(self, frame_data: FrameData):
        self.frame_data = frame_data
        self.data_manager.on_frame_data_recv(self.frame_data)

    def processing(self):
        pass

    def round_end(self, round_result: RoundResult):
        self.data_manager.on_round_end()
