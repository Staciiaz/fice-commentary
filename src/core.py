import logging
from threading import Thread

import cv2
import numpy as np
from pyftg.aiinterface.stream_interface import StreamInterface
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.game_data import GameData
from pyftg.models.round_result import RoundResult
from pyftg.models.screen_data import ScreenData
from pyftg_sound.models.audio_source import AudioSource
from pyftg_sound.models.sound_renderer import SoundRenderer
from pyftg_sound.openal import al
from pyftg_sound.sound_manager import SoundManager

from src.models.tts import TextToSpeechModel
from src.utils import put_text_on_image

logger = logging.getLogger(__name__)


class FightingStream(StreamInterface):
    frame_data: FrameData
    audio_data: AudioData
    screen_data: ScreenData
    sound_manager: SoundManager
    game_audio_source: AudioSource
    speech_audio_source: AudioSource
    tts_model: TextToSpeechModel
    current_text: str = None
    current_speech: np.ndarray[np.int16] = None
    previous_frame: int = -1

    def __init__(self) -> None:
        self.sound_manager = SoundManager()
        default_renderer = SoundRenderer.create_default_renderer()
        self.sound_manager.set_default_renderer(default_renderer)
        self.game_audio_source = self.sound_manager.create_audio_source()
        self.speech_audio_source = self.sound_manager.create_audio_source()
        self.tts_model = TextToSpeechModel()

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

    def generate_commentary_thread(self):
        text = "Hello World! From DareFightingICE !!"
        self.current_speech = self.tts_model.generate_speech(text)
        self.current_text = text
        self.sound_manager.playback(self.speech_audio_source, al.AL_FORMAT_MONO16, self.current_speech.tobytes(), 16000)

    def play_game_audio(self):
        audio = np.frombuffer(self.audio_data.raw_data_bytes, dtype=np.float32)
        audio = np.int16(audio * 32767)
        audio = audio.reshape((2, 1024))[:, :800]
        self.sound_manager.playback(self.game_audio_source, al.AL_FORMAT_STEREO16, audio.tobytes(), 48000)

    def processing(self):
        if self.frame_data.empty_flag or self.frame_data.current_frame_number < 0:
            return

        if self.frame_data.current_frame_number % 300 == 60:
            thread = Thread(target=self.generate_commentary_thread)
            thread.start()
        
        image = np.frombuffer(self.screen_data.display_bytes, dtype=np.uint8)
        image = image.reshape((640, 960, 3))
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if self.sound_manager.is_playing(self.speech_audio_source):
            put_text_on_image(image, self.current_text, x=480, y=600)
        cv2.imshow("DareFightingICE", image)
        cv2.waitKey(1)

    def round_end(self, round_result: RoundResult):
        self.sound_manager.stop_playback(self.speech_audio_source)
        self.sound_manager.stop_playback(self.game_audio_source)
        if round_result.current_round < 3:
            image = np.zeros((640, 960, 3), dtype=np.uint8)
            put_text_on_image(image, "Waiting for Round Start", x=480, y=200)
            cv2.imshow("DareFightingICE", image)
            cv2.waitKey(1)
        else:
            cv2.destroyAllWindows()

    def game_end(self):
        pass

    def close(self):
        pass
