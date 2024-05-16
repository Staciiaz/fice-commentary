from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.audio_data import AudioData

from src.core import DataManager


class AudioStream(StreamInterface):
    def __init__(self, data_manager: DataManager) -> None:
        self.data_manager = data_manager

    def get_audio_data_flag(self) -> bool:
        return True

    def get_audio_data(self, audio_data: AudioData):
        self.data_manager.on_audio_data_recv(audio_data)
