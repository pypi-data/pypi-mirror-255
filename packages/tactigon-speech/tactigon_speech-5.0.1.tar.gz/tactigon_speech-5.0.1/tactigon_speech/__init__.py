__version__ = "5.0.1"

__all__ = ['TSkin_Speech', 'TSkinConfig', 'AudioSource', 'HotWord', 'TSpeech', 'TSpeechObject', 'TSpeechCommandEnum', 'VoiceConfig', 'Transcription',
           'Gesture', 'GestureConfig', 'Hand', 'Angle', 'Touch', 'OneFingerGesture', 'TwoFingerGesture', 'Gyro', 'Acceleration']

import sys
import threading
import logging
import time
import ctypes

from typing import Optional
from multiprocessing import Process, Pipe, Value

if sys.platform == "win32":
    from multiprocessing.connection import PipeConnection
else:
    from multiprocessing.connection import Pipe as PipeConnection
    
from multiprocessing.sharedctypes import SynchronizedBase

from tactigon_gear import TSkin, TSkinConfig, Gesture, GestureConfig, Hand, Angle, Touch, OneFingerGesture, TwoFingerGesture, Gyro, Acceleration
from .middleware import Tactigon_Speech
from .models import AudioSource, HotWord, TSpeech, TSpeechObject, TSpeechCommandEnum, VoiceConfig, Transcription, TSkinState

class TSkin_Speech(TSkin):
    logger: logging.Logger
    audio_source: AudioSource = AudioSource.TSKIN

    _process_pipe: PipeConnection
    _interface_pipe: PipeConnection
    
    _command: SynchronizedBase

    process: Process
    interface_process: threading.Thread

    _transcription: Optional[Transcription] = None

    def __init__(self, 
                config: TSkinConfig,
                voice_config: VoiceConfig,
                audio_source: AudioSource = AudioSource.TSKIN,
                debug: bool = False
                ):
        
        self.audio_source = audio_source

        if self.audio_source == AudioSource.TSKIN:
            self.adpcm_rx, self.adpcm_tx = Pipe(duplex=False)
        
        super().__init__(config, debug)

        self._command = Value(ctypes.c_int, TSpeechCommandEnum.NOT_INITIALIZED.value)
        self._process_pipe, self._interface_pipe = Pipe()
        self.process = Process(
            target=Tactigon_Speech, 
            args=(
                self._process_pipe, 
                self._command,
                self.adpcm_rx,
                audio_source,
                voice_config,
                self.logger.level
                )
            )
        self.interface_process = threading.Thread(target=self._interface_process)
    
    def _interface_process(self):
        self.logger.debug("[TSkin_Speech] Started interface process")
        while True:
            current_command = self.command

            if current_command == TSpeechCommandEnum.END:
                self.logger.debug("[TSkin_Speech] Stopping interface process")
                break
            elif current_command == TSpeechCommandEnum.LISTEN:
                while not self._interface_pipe.poll():
                    pass

                self._transcription = self._interface_pipe.recv()
                self.logger.debug("[TSkin_Speech] Got transcription from interface pipe %s", self._transcription)
                self.select_sensors()
            elif current_command == TSpeechCommandEnum.RECORD:
                while not self._interface_pipe.poll():
                    pass

                filename = self._interface_pipe.recv()
                self.logger.debug("[TSkin_Speech] Got filename from interface pipe %s", filename)
                self.select_sensors()

    def start(self):
        super().start()
        self.process.start()
        self.interface_process.start()
        
    def terminate(self):
        with self._command.get_lock():
            self._command.get_obj().value = TSpeechCommandEnum.END.value
        self.process.terminate()
        self.interface_process.join(1.0)
        super().terminate()

    @property
    def initialized(self) -> bool:
        with self._command.get_lock():
            return self._command.get_obj().value != TSpeechCommandEnum.NOT_INITIALIZED.value
        
    @property
    def state(self) -> TSkinState:
        return TSkinState(
            self.connected,
            self.battery,
            self.ble.selector,
            self.touch,
            self.angle,
            self.gesture,
            self._get_transcription(True)
        )
    
    @property
    def command(self) -> TSpeechCommandEnum:
        with self._command.get_lock():
            return TSpeechCommandEnum(self._command.get_obj().value)

    def play(self, file_path: str) -> bool:
        with self._command.get_lock():
            if self._command.get_obj().value != TSpeechCommandEnum.NONE.value:
                self.logger.warning("[TSpeech] Cannot set play command while another command is running (%s)", TSpeechCommandEnum(self._command.get_obj().value))
                return False

            self._interface_pipe.send(file_path)
            self._command.get_obj().value = TSpeechCommandEnum.PLAY.value
        return True

    @property
    def is_playing(self) -> bool:
        with self._command.get_lock():
            return self._command.get_obj().value == TSpeechCommandEnum.PLAY.value
        
    def record(self, file_path: str) -> bool:
        with self._command.get_lock():
            if self._command.get_obj().value != TSpeechCommandEnum.NONE.value:
                self.logger.warning("[TSpeech] Cannot set record command while another command is running (%s)", TSpeechCommandEnum(self._command.get_obj().value))
                return False
            
            if self.audio_source == AudioSource.TSKIN:
                self.select_voice()

            self._interface_pipe.send(file_path)
            self._command.get_obj().value = TSpeechCommandEnum.RECORD.value

        return True

    @property
    def is_recording(self) -> bool:
        with self._command.get_lock():
            return self._command.get_obj().value == TSpeechCommandEnum.RECORD.value

    def listen(self, tspeech: TSpeechObject) -> bool:
        with self._command.get_lock():
            if self._command.get_obj().value != TSpeechCommandEnum.NONE.value:
                self.logger.warning("[TSpeech] Cannot set listen command while another command is running (%s)", TSpeechCommandEnum(self._command.get_obj().value))
                return False
            
            if self.audio_source == AudioSource.TSKIN:
                self.select_voice()
            
            self._interface_pipe.send(tspeech)
            self._command.get_obj().value = TSpeechCommandEnum.LISTEN.value
        return True

    @property
    def is_listening(self) -> bool:
        with self._command.get_lock():
            return self._command.get_obj().value == TSpeechCommandEnum.LISTEN.value

    def stop(self):
        with self._command.get_lock():
            self._command.get_obj().value = TSpeechCommandEnum.STOP.value
        
        while self.cmd_running:
            time.sleep(0.1)

        if self.audio_source == AudioSource.TSKIN:
            self.select_sensors()

    @property
    def transcription(self) -> Optional[Transcription]:
        return self._get_transcription(False)
    
    def _get_transcription(self, preserve: bool = False):
        t = self._transcription
        if not preserve:
            self._transcription = None
        return t

    @property
    def cmd_running(self) -> bool:
        with self._command.get_lock():
            return self._command.get_obj().value != TSpeechCommandEnum.NONE.value