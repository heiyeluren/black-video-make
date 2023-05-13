# -*- encoding: utf-8 -*-

'''
Audio process 
音频处理核心函数

author: heiyeluren
date: 2023/5/10
site: github.com/heiyeluren

'''

import os
import subprocess
import azure.cognitiveservices.speech as speechsdk

from . import defined
from .defined import *
from . import util
from .util import *



# 文本转语音
def synthesize_text_to_voice(input_text_file: str, output_wav_file: str, is_output_mp3: bool = False, output_mp3_file: str = "", is_play: bool = False, voice_name: str='zh-CN-YunzeNeural', subscription: str='', region: str='', ) -> None:
    """
    将文本合成为语音，并保存为.wav文件，可选择转换为.mp3文件，并可选择是否播放

    参数：
    voice_name：选择语音人物
    subscription：Azure认知服务的API密钥
    region：Azure认知服务的区域
    input_text_file：输入文本文件的路径
    output_wav_file：输出.wav文件的路径
    is_output_mp3：是否同时输出为.mp3文件，默认为False
    output_mp3_file：输出.mp3文件的路径（仅当is_output_mp3为True时有用）
    is_play_mp3：是否播放生成的.mp3文件，默认为False

    返回值：
    无返回值

    调用示例：
    synthesize_text_to_voice(
        voice_name="zh-CN-YunzeNeural",
        subscription="your_subscription_key",
        region="your_region",
        input_text_file="voice_text.txt",
        output_wav_file="output_text.wav",
        is_output_mp3=True,
        output_mp3_file="output_text.mp3",
        is_play=False
    )

    """

    # 初始化相关tts配置
    if region == '':
        region = get_tts_key()['region']
    if subscription == '':
        subscription = get_tts_key()['subscription']

    voice_language = "zh-CN"
    speech_config = speechsdk.SpeechConfig(subscription=subscription, region=region)
    speech_config.speech_synthesis_language = voice_language
    speech_config.speech_synthesis_voice_name = voice_name
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True, filename=output_wav_file)
    speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    with open(input_text_file, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()
    if text == '':
        raise Exception("input_text_file is empty")

    # 进行tts流读取
    speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
    stream = speechsdk.AudioDataStream(speech_synthesis_result)

    # 保存tts返回内容为wav文件
    ret = stream.save_to_wav_file(output_wav_file)
    if ret is False:
        print("Error: Text to speech is fail, wav file:", output_wav_file)
        raise Exception("Text to speech is fail.")

    if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesized for text [{}]\n".format(text))
    elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print("Speech synthesis canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print("Error details: {}".format(cancellation_details.error_details))
                print("Did you set the speech resource key and region values?")

    # 转换音频文件格式为mp3
    if is_output_mp3 and output_mp3_file=="":
        raise Exception("output_mp3_file params is required when is_output_mp3 is True")
    if is_output_mp3:
        if not output_mp3_file:
            output_mp3_file = os.path.splitext(output_wav_file)[0] + ".mp3"
        if ffmpeg_is_installed() == False:
            raise Exception("ffmpeg is not installed, please from https://github.com/BtbN/FFmpeg-Builds/releases download ffmpeg and install it")
        subprocess.call(['ffmpeg', '-y', '-i', output_wav_file, '-b:a', '192k', output_mp3_file])

    # 播放返回的音频内容
    if is_play:
        if ffmpeg_is_installed() == False:
            raise Exception("ffmpeg is not installed, please from https://github.com/BtbN/FFmpeg-Builds/releases download ffmpeg and install it")
        # subprocess.call(['vlc', output_mp3_file]) #也可以调用vlc播放mp3
        subprocess.call(['ffplay', '-nodisp', '-autoexit', output_wav_file])


# 合并多个音频文件
def merge_audio_files(audio_list, output_path: str, output_file_name = 'final.wav'):

    # 创建一个保存视频的文件夹
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))
    # list = video_list.split("\n")
    tmp_audio_file_name = "audiolist.txt"
    list_file = output_path +"/"+tmp_audio_file_name
    list_file = list_file.replace("\\", "/")
    with open(list_file, "w") as f:
        for item in audio_list:
            item = item.replace("\\", "/")
            f.write(f"file '{item}'\n")
        os.chmod(list_file, 0o777)

    # 使用ffmpeg把多个音频文件进行合并
    output_file = output_path + "/" + output_file_name
    output_file = output_file.replace("\\", "/")
    subprocess.call(f'ffmpeg -f concat -safe 0 -i {list_file} -c copy {output_file}', shell=True)
    # ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.wav

