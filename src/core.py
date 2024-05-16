import cv2
import numpy as np
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.screen_data import ScreenData
from pyftg_sound.models.sound_renderer import SoundRenderer
from pyftg_sound.openal import al
from pyftg_sound.sound_manager import SoundManager


class DataManager:
    def __init__(self) -> None:
        self.frame_data = FrameData()
        self.audio_data = AudioData()
        self.screen_data = ScreenData()
        self.sound_manager = SoundManager()
        default_renderer = SoundRenderer.create_default_renderer()
        self.sound_manager.set_default_renderer(default_renderer)
        self.game_audio_source = self.sound_manager.create_audio_source()
        self.speech_audio_source = self.sound_manager.create_audio_source()

    def on_frame_data_recv(self, frame_data: FrameData):
        self.frame_data = frame_data

    def on_audio_data_recv(self, audio_data: AudioData):
        self.audio_data = audio_data
        audio = np.frombuffer(self.audio_data.raw_data_bytes, dtype=np.float32)
        audio = np.int16(audio * 32767)
        audio = audio.reshape((2, 1024))[:, :800]
        self.sound_manager.playback(self.game_audio_source, al.AL_FORMAT_STEREO16, audio.tobytes(), 48000)

    def on_screen_data_recv(self, screen_data: ScreenData):
        self.screen_data = screen_data
        if self.screen_data.display_bytes:
            image = np.frombuffer(self.screen_data.display_bytes, dtype=np.uint8)
            image = image.reshape((640, 960, 3))
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imshow("DareFightingICE", image)
            cv2.waitKey(1)

    def on_round_end(self):
        self.sound_manager.stop_playback(self.game_audio_source)
        cv2.destroyAllWindows()
