# -*- encoding: utf-8 -*-

'''
Image Process
图片处理处理核心函数

author: heiyeluren
date: 2023/5/13
site: github.com/heiyeluren

'''

import os
import time
import azure.cognitiveservices.speech as speechsdk # pip install azure-cognitiveservices-speech
from pydub import AudioSegment  # pip install pydub
import shutil

from . import defined
from .defined import *
from . import util
from .util import *


'''

语音成材文本

把视频文件中的内容识别成为文本，并保存为 srt 格式的字幕文件


Example:

speech_key = "YOUR_SPEECH_KEY"
service_region = "YOUR_SERVICE_REGION"
video_file_path = "YOUR_VIDEO_FILE_PATH"

stt = SpeechToText(speech_key, service_region, video_file_path, audio_file_path="path/to/audio.wav", srt_file_path="path/to/output.srt")
stt.recognize_and_save_as_srt()


'''
class SpeechToText:
    def __init__(self, speech_key, service_region, video_file_path, audio_file_path=None, srt_file_path=None):
        self.speech_key = speech_key
        self.service_region = service_region
        self.video_file_path = video_file_path
        self.text = ''
        self.done = False

        if audio_file_path is not None:
            self.audio_file_path = audio_file_path
        else:
            self.audio_file_path = ''

        if srt_file_path is not None:
            self.srt_file_path = srt_file_path
        else:
            self.srt_file_path = ''
        # or os.path.splitext(video_file_path)[0] + '.wav'
        # self.srt_file_path = srt_file_path or os.path.splitext(video_file_path)[0] + '.srt'


    # 提取音频文件
    def extract_audio(self):
        # 判断音频文件格式
        audio_file_format = os.path.splitext(self.video_file_path)[1][1:].lower()

        # 判断音频文件是否存在
        if not os.path.exists(self.video_file_path):
            raise Exception("Video file is not exists: {}".format(self.video_file_path))

        if audio_file_format in ["mp3", "wav"]:
            # 将非wav格式的音频文件转换为wav格式
            if audio_file_format == "mp3":
                audio = AudioSegment.from_file(self.video_file_path, "mp3")
                audio.export(self.audio_file_path, format="wav")
            else:  # 已经是wav格式，直接复制
                # os.system(f"cp {self.video_file_path} {self.audio_file_path}")
                if self.audio_file_path != self.video_file_path:
                    shutil.copy2(self.video_file_path, self.audio_file_path)
        elif audio_file_format == "mp4":
            # 从mp4视频中提取音频
            audio = AudioSegment.from_file(self.video_file_path, "mp4")
            audio.export(self.audio_file_path, format="wav")            
            # clip = VideoFileClip(self.video_file_path)
            # clip.audio.write_audiofile(self.audio_file_path)
        else:
            raise Exception("Only support mp4, mp3 and wav audio format.")

    def create_speech_recognizer(self):
        # 创建语音识别器
        speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.service_region)
        speech_config.speech_recognition_language = "zh-CN"
        audio_config = speechsdk.AudioConfig(filename=self.audio_file_path)
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # 连接回调函数
        speech_recognizer.recognizing.connect(self.recognizing_cb)
        speech_recognizer.recognized.connect(self.recognized_cb)
        speech_recognizer.session_started.connect(self.session_started_cb)
        speech_recognizer.session_stopped.connect(self.session_stopped_cb)
        speech_recognizer.canceled.connect(self.canceled_cb)
        speech_recognizer.session_stopped.connect(self.stop_cb)
        speech_recognizer.canceled.connect(self.stop_cb)

        self.speech_recognizer = speech_recognizer

    def recognizing_cb(self, evt):
        pass

    def recognized_cb(self, evt):
        self.text += evt.result.text
        self.text += '\n'

    def session_started_cb(self, evt):
        pass

    def session_stopped_cb(self, evt):
        pass

    def canceled_cb(self, evt):
        pass

    def stop_cb(self, evt):
        self.done = True

    def filter_srt(self):
        # 去除标点符号
        punctuation = '！？。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～ '
        filtered_text = ''.join([char for char in self.text if char not in punctuation])

        # 生成 srt 格式的字幕文件
        duration = len(AudioSegment.from_file(self.audio_file_path)) / 1000
        with open(self.srt_file_path, "w", encoding='utf-8', errors='ignore') as srt_file:
            srt_file.write("1\n")
            srt_file.write("00:00:00,000 --> {:02d}:{:02d}:{:02d},{:03d}\n".format(int(duration // 3600),
                                                                                int((duration % 3600) // 60),
                                                                                int(duration % 60),
                                                                                int((duration % 1) * 1000)))
            if all(u'\u4e00' <= char <= u'\u9fff' for char in filtered_text):
                srt_file.write("{}\n\n".format(filtered_text))
            else:
                srt_file.write("{}\n\n".format(self.text))

    def recognize_and_save_as_srt(self):
        self.extract_audio()
        self.create_speech_recognizer()
        self.speech_recognizer.start_continuous_recognition()
        while not self.done:
            time.sleep(.5)
        self.speech_recognizer.stop_continuous_recognition()
        self.filter_srt()        

