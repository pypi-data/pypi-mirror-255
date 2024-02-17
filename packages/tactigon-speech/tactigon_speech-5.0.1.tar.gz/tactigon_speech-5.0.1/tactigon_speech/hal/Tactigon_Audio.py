import sys
import struct
import queue
import pyaudio
import threading

import logging

if sys.platform == "win32":
    from multiprocessing.connection import PipeConnection
else:
    from multiprocessing.connection import Pipe as PipeConnection

from typing import Optional, List

from ..models import AudioSource, TStreamStatus

class ADPCMEngine(object):
    """DPCM Engine class.
    It contains all the operations and parameters necessary to decompress the
    received audio.
    """
    
    DATA_LENGTH_BYTES = 20
    AUDIO_PACKAGE_SIZE = 40
    
    def __init__(self): 
        """Constructor."""

        # Quantizer step size lookup table .
        self._step_size_table=[7,8,9,10,11,12,13,14,16,17,
            19,21,23,25,28,31,34,37,41,45,
            50,55,60,66,73,80,88,97,107,118,
            130,143,157,173,190,209,230,253,279,307,
            337,371,408,449,494,544,598,658,724,796,
            876,963,1060,1166,1282,1411,1552,1707,1878,2066,
            2272,2499,2749,3024,3327,3660,4026,4428,4871,5358,
            5894,6484,7132,7845,8630,9493,10442,11487,12635,13899,
            15289,16818,18500,20350,22385,24623,27086,29794,32767]

        # Table of index changes.
        self._index_table = [-1,-1,-1,-1,2,4,6,8,-1,-1,-1,-1,2,4,6,8]
        
        self._index = 0
        self._pred_sample = 0

    def decode(self, code) -> int: 
        """ADPCM_Decode.
        
        Args:
            code (byte): It contains a 4-bit ADPCM sample.
        
        Returns:
            int: A 16-bit ADPCM sample.
        """
        # 1. get sample
        step = self._step_size_table[self._index]

        # 2. inverse code into diff 
        diffq = step>> 3
        if ((code&4)!=0):
            diffq += step
        
        if ((code&2)!=0):
            diffq += step>>1
        

        if ((code&1)!=0):
            diffq += step>>2

        # 3. add diff to predicted sample
        if ((code&8)!=0):
            self._pred_sample -= diffq
        
        else:
            self._pred_sample += diffq
        
        # check for overflow
        if (self._pred_sample > 32767):
            self._pred_sample = 32767

        elif (self._pred_sample < -32768):
            self._pred_sample = -32768

        # 4. find new quantizer step size 
        self._index += self._index_table [code]
        #check for overflow
        if (self._index < 0):
            self._index = 0
            
        if (self._index > 88):
            self._index = 88

        # 5. save predict sample and index for next iteration 
        # done! static variables 

        # 6. return speech sample
        return self._pred_sample
    
    def extract_data(self, data) -> List[int]:
        """Extract the data from the feature's raw data.

        Args:
            data (bytearray): The data read from the feature (a 20 bytes array).
        
        Returns:
            :class:`blue_st_sdk.feature.ExtractedData`: Container of the number
            of bytes read (20)  and the extracted data (audio info, the 40
            shorts array).
        """
        if len(data) != ADPCMEngine.DATA_LENGTH_BYTES:
            return []
        
        data_byte = bytearray(data)
        
        data_pkt = [0] * self.AUDIO_PACKAGE_SIZE
        for x in range(0, int(self.AUDIO_PACKAGE_SIZE / 2)):
            data_pkt[2*x] = self.decode((data_byte[x] & 0x0F))
            data_pkt[(2*x)+1] = self.decode(((data_byte[x] >> 4) & 0x0F))
        
        return data_pkt

    @staticmethod
    def int16_to_bytes(value: int) -> bytes:
        return struct.pack("<i", value)[0:2]

class Tactigon_Audio(ADPCMEngine):
    sample_rate: int = 16000
    frame_duration: int = 20
    tskin_frame_length: int = 80 // 2 # packet length is 80, but we have 2 bits per packet!
    frame_per_seconds: int = 50
    frame_buffer_length: int

    audio_source: AudioSource
    is_running: bool
    in_pipe: Optional[PipeConnection]
    buffer_queue: queue.Queue
    pa: pyaudio.PyAudio
    stream_status: TStreamStatus
    block_size: int

    thread: threading.Thread
    stream: pyaudio.Stream

    is_clearing_queue: bool = False

    def __init__(self, in_pipe: Optional[PipeConnection], audio_source: AudioSource, logger_level: int):

        self.logger = logging.getLogger()
        self.logger.setLevel(logger_level)
        self.logger.addHandler(logging.StreamHandler())

        self.audio_source = audio_source
        self.is_running = True
        self.is_clearing_queue = False
        self.in_pipe = in_pipe
        self.frame_buffer_length = self.sample_rate * self.frame_duration // 1000 // self.tskin_frame_length

        self.buffer_queue = queue.Queue()
        self.pa = pyaudio.PyAudio()
        self.stream_status = TStreamStatus.STOPPED

        if self.audio_source == AudioSource.TSKIN:
            super().__init__()
            self.thread = threading.Thread(target=self.tskin_audio)
            self.thread.start()
        else:
            def stream_callback(in_data, f_count, t_info, st):
                if not self.is_clearing_queue:
                    self.buffer_queue.put(in_data)
                return (None, pyaudio.paContinue)

            self.stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=int(self.sample_rate / self.frame_per_seconds),
                stream_callback=stream_callback,
                start=False
            )  

    def tskin_audio(self):
        if self.in_pipe is None: 
            raise TypeError("Audio source is TSKIN but no pipe is provided")

        n_buffer = 0
        data = b''
        while self.is_running:
            if not self.in_pipe.poll(1):
                if self.stream_status == TStreamStatus.STREAMING:
                    self.logger.warning("[TAudio] Audio source is TSKIN but no audio is streaming from TSkin")
                continue

            pipe_data = self.in_pipe.recv()
            if self.stream_status == TStreamStatus.STREAMING or n_buffer > 0:
                adpcm_data = self.extract_data(pipe_data)
                data += b''.join([self.int16_to_bytes(d) for d in adpcm_data])
                n_buffer += 1
                if not n_buffer < self.frame_buffer_length:
                    if not self.is_clearing_queue:
                        self.buffer_queue.put(data)
                    data = b''
                    n_buffer = 0

    def start_stream(self):
        if self.audio_source == AudioSource.TSKIN:
            self.stream_status = TStreamStatus.STREAMING
        else:
            self.stream.start_stream()

    def stop_stream(self):
        if self.audio_source == AudioSource.TSKIN:
            self.stream_status = TStreamStatus.STOPPED
        else:
            self.stream.stop_stream()

    def clear(self):
        self.is_clearing_queue = True
        while self.buffer_queue.qsize() > 0:
            self.buffer_queue.get()

        self.is_clearing_queue = False

    def read(self) -> bytes:
        return self.buffer_queue.get()

    def destroy(self):
        self.is_running = False
        if self.audio_source == AudioSource.TSKIN:
            self.thread.join(1.0)
        else:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
        self.pa.terminate()
  