import logging
import time

import cv2
import numpy as np
from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.game_data import GameData
from pyftg.models.round_result import RoundResult
from pyftg.models.screen_data import ScreenData
from pyftg_sound.sound_manager import SoundManager
from pyftg_sound.models.sound_renderer import SoundRenderer
from pyftg_sound.models.audio_source import AudioSource
from pyftg_sound.openal import al, alc

from src.utils import put_text_on_image

logger = logging.getLogger(__name__)


class FightingStream(StreamInterface):
    frame_data: FrameData
    audio_data: AudioData
    screen_data: ScreenData
    sound_manager: SoundManager
    audio_source: AudioSource
    previous_frame: int = -1

    def __init__(self) -> None:
        self.sound_manager = SoundManager()
        default_renderer = SoundRenderer.create_default_renderer()
        self.sound_manager.set_default_renderer(default_renderer)
        self.audio_source = self.sound_manager.create_audio_source()

    def initialize(self, game_data: GameData):
        pass

    def get_information(self, frame_data: FrameData):
        if self.previous_frame + 1 != frame_data.current_frame_number:
            logger.warning(f"Frame skipped: {self.previous_frame} -> {frame_data.current_frame_number}")
        self.frame_data = frame_data
        self.previous_frame = self.frame_data.current_frame_number

    def get_audio_data(self, audio_data: AudioData):
        self.audio_data = audio_data

    def get_screen_data(self, screen_data: ScreenData):
        self.screen_data = screen_data

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number < 0:
            return

        audio = np.frombuffer(self.audio_data.raw_data_bytes, dtype=np.float32)
        audio = np.int16(audio * 32767)
        audio = audio.reshape((2, 1024))[:, :800]
        self.sound_manager.playback(self.audio_source, al.AL_FORMAT_STEREO16, audio.tobytes(), 48000)
        
        image = np.frombuffer(self.screen_data.display_bytes, dtype=np.uint8)
        image = image.reshape((640, 960, 3))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        put_text_on_image(image, "Hello World! From DareFightingICE !!", x=480, y=600)
        cv2.imshow("DareFightingICE", image)
        cv2.waitKey(1)

    def round_end(self, round_result: RoundResult):
        self.sound_manager.stop_playback(self.audio_source)
        image = np.zeros((640, 960, 3), dtype=np.uint8)
        put_text_on_image(image, "Waiting for Round Start", x=480, y=200)
        cv2.imshow("DareFightingICE", image)
        cv2.waitKey(1)

    def game_end(self):
        cv2.destroyAllWindows()

    def close(self):
        pass
