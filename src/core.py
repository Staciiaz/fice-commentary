import asyncio
import logging

import cv2
import numpy as np
from pyftg.models.audio_data import AudioData
from pyftg.models.frame_data import FrameData
from pyftg.models.screen_data import ScreenData
from pyftg_sound.models.sound_renderer import SoundRenderer
from pyftg_sound.openal import al
from pyftg_sound.sound_manager import SoundManager
from typing_extensions import List

from src.embeddings import embedding_frame_data, process_frame_data
from src.models.commentary import CommentaryModel
from src.models.tts import TextToSpeechModel
from src.utils import put_text_on_image

logger = logging.getLogger(__name__)


class DataManager:
    def __init__(self) -> None:
        self.initialize_sound()
        self.initialize_model()
        self.initialize_data()

    def initialize_model(self):
        self.commentary_model = CommentaryModel()
        # self.tts_model = TextToSpeechModel()
        logger.info("Model initialized")

    def initialize_sound(self):
        self.sound_manager = SoundManager()
        default_renderer = SoundRenderer.create_default_renderer()
        self.sound_manager.set_default_renderer(default_renderer)
        self.game_audio_source = self.sound_manager.create_audio_source()
        self.speech_audio_source = self.sound_manager.create_audio_source()
        logger.info("Sound manager initialized")

    def initialize_data(self):
        self.frames_data: List[FrameData] = []
        self.audio_data = AudioData()
        self.screen_data = ScreenData()
        self.last_frame = 0
        self.current_round = 1
        self.current_commentary = ''
        self.current_speech: np.ndarray[np.int16] = None
        self.is_commentary_generating = False
        self.is_tts_generating = False
        logger.info("Data initialized")

    def do_commentary_generation(self, current_round: int, frame_embedding: List[float]):
        self.is_commentary_generating = True
        logger.info("Generating commentary ...")
        commentary = self.commentary_model.generate_commentary(frame_embedding)
        logger.info(f"Generated commentary: {commentary}")
        # logger.info("Generating speech ...")
        # speech = self.tts_model.generate_speech(commentary)
        # logger.info("Generated speech")
        self.is_commentary_generating = False
        if current_round == self.current_round:
            self.current_commentary = commentary
            # self.current_speech = speech
            # self.sound_manager.playback(self.speech_audio_source, al.AL_FORMAT_MONO16, speech.tobytes(), 16000)

    def on_frame_data_recv(self, frame_data: FrameData):
        if frame_data.empty_flag or frame_data.current_frame_number < 0:
            return
        
        self.frames_data.append(frame_data)
        while len(self.frames_data) > 3:
            self.frames_data.pop(0)

        if len(self.frames_data) >= 3 and not self.is_commentary_generating and frame_data.current_frame_number >= self.last_frame + 300:
            self.last_frame = frame_data.current_frame_number
            frame_embedding: List[float] = []
            for frame_data in reversed(self.frames_data):
                frame_dict = process_frame_data(frame_data)
                frame_embedding.extend(embedding_frame_data(frame_dict))
            loop = asyncio.get_event_loop()
            loop.run_in_executor(None, self.do_commentary_generation, self.current_round, frame_embedding)

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
            if self.current_commentary:
                put_text_on_image(image, self.current_commentary, 480, 600)
            cv2.imshow("DareFightingICE", image)
            cv2.waitKey(1)

    def on_round_end(self):
        self.last_frame = 0
        self.current_round += 1
        self.current_commentary = ''
        self.sound_manager.stop_playback(self.game_audio_source)
        cv2.destroyAllWindows()
