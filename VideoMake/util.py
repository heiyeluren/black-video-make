# -*- encoding: utf-8 -*-

'''
Core utility functions
封装核心基础的操作类

author: heiyeluren
date: 2023/5/10
site: github.com/heiyeluren

'''

import os
import time
import datetime
import platform
import subprocess
import pyttsx3
from PIL import Image
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk
from . import defined
from .defined import *



# 读取文本内容
def get_file_contents(file_path, is_splitlines=True):
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        if is_splitlines is False:
            text = f.read()
            if len(text.strip()) == 0:
                raise Exception("Input text file contents is empty")            
        else:
            text = f.read().splitlines()
            if len(text) == 0:
                raise Exception("Input text file contents is empty")
    return text

# 检查一个命令是否存在
def check_command_exist(command):
    """
    判断一个命令是否存在。
    
    参数：
    command - 要查询的命令名称。
    
    返回值：
    如果命令存在，则返回命令所在的路径；否则返回 None。
    """
    if platform.system() == "Windows":
        where_command = "where"
    else:
        where_command = "which"
    try:
        output = subprocess.check_output([where_command, command], shell=True)
    except subprocess.CalledProcessError:
        return None
    else:
        command_path = output.decode("utf-8").strip()
        return command_path


# 判断ffmpeg是否已安装
def ffmpeg_is_installed() -> bool:
    """
    判断ffmpeg是否已安装

    参数：
    无参数

    返回值：
    如果已安装则返回True，否则返回False
    """
    if check_command_exist("ffmpeg") is None:
        return False
    else:
        return True
    
    ret = os.system("ffmpeg -version")  # 运行ffmpeg命令
    if ret == 0:  # 命令执行成功，说明ffmpeg已安装
        return True
    else:  # 命令执行失败，说明ffmpeg未安装
        return False
    
#判断vlc播放器是否安装
def vlc_is_installed() -> bool:
    """
    判断vlc是否已安装

    参数：
    无参数

    返回值：
    如果已安装则返回True，否则返回False
    """
    if check_command_exist("vlc") is None:
        return False
    else:
        return True
    
    try:
        subprocess.call(['vlc', '--version'])
        return True
    except OSError:
        return False

# 播放视频
def play_video(video_path):
    # print(video_path)
    if os.path.exists(video_path) is False:
        print("Video file not exists!")
        return False
    if vlc_is_installed() is True:
        # s = f'vlc {video_path}'
        subprocess.call(f'vlc {video_path}', shell=True)
        return True
    elif ffmpeg_is_installed() is True:
        subprocess.call(f'ffplay -autoexit {video_path}', shell=True)
        return True
    else:
        print("No video player(vlc or ffmpeg) installed, please install video player!")
        return False


# 获取tts访问密钥
def get_tts_key(key = ''):
    """
    获取Azure TTS服务的认证Key和区域信息

    参数：
    key - 要获取的Key，可选值为：subscription、region

    返回值：
    包含认证Key和区域信息的字典，格式如下：
    {
        "subscription": "<Your Subscription Key>",
        "region": "<Your Region>"
    }
    如果设置了key参数，返回对应的值，否则返回整个字典
    """
    result = {
        "subscription": '',
        "region": ''
    }
    # 用户自己定义subscription_key及region值，用于后续的鉴权和定位Azure TTS服务区域
    subscription = os.environ.get('SPEECH_KEY') 
    region = os.environ.get('SPEECH_REGION')

    if subscription == '' or region == '':
        print("Warning: Please set environment variable SPEECH_KEY and SPEECH_REGION")
        return result

    # 构造包含认证Key和区域信息的字典
    result = {
        "subscription": subscription,
        "region": region
    }
    if key == '':
        return result
    
    if key != '' and key == 'subscription':
        rs = result['subscription']
    if key != '' and key == 'region':
        rs = result['region']
    return str(rs)


# 判断ffmpeg是否已安装
def is_ffmpeg_installed() -> bool:
    """
    判断ffmpeg是否已安装

    参数：
    无参数

    返回值：
    如果已安装则返回True，否则返回False
    """
    ret = os.system("ffmpeg -version")  # 运行ffmpeg命令
    if ret == 0:  # 命令执行成功，说明ffmpeg已安装
        return True
    else:  # 命令执行失败，说明ffmpeg未安装
        return False

# 调用内置tts引擎播放文字
def ttsx3_say(text):
    #	语音模块初始化
    engine = pyttsx3.init()
    #	设置要播报的字符串
    if text == '':    
        text = "你好，我是语音引擎TTSX3，希望你能喜欢我"
    engine.say(text)
    #	等待运行
    engine.runAndWait()


# 扫描原始文件是否准备好
def check_input_files():
    video_bg_files = []
    video_text_files = []
    voice_text_files = []
    video_bg_files_seq = []
    video_text_files_seq = []
    voice_text_files_seq = []

    result = {}

    # 扫描背景图文件
    # print(defined.INPUT_ROOT_PATH)
    for file in os.listdir(defined.INPUT_ROOT_PATH):
        # print(file)
        # 处理视频背景图文件
        if file.startswith(VIDEO_BG_PREFIX) and file.endswith(PNG_SUFFIX):            
            tmp_name = file.replace(VIDEO_BG_PREFIX, "").replace(PNG_SUFFIX, "")
            if tmp_name.isdigit() == False:
                raise Exception("video_bg_files file name must be number")
            video_bg_files.append(file)
            video_bg_files_seq.append(int(tmp_name))
            result.setdefault(tmp_name, {})
            result[tmp_name][VIDEO_BG_FILE] = file


        #处理视频显示文本文件
        if file.startswith(VIDEO_TEXT_PREFIX) and file.endswith(TEXT_SUFFIX):
            tmp_name = file.replace(VIDEO_TEXT_PREFIX, "").replace(TEXT_SUFFIX, "")
            if tmp_name.isdigit() == False:
                raise Exception("video_text_files file name must be number")
            video_text_files.append(file)
            video_text_files_seq.append(int(tmp_name))
            result.setdefault(tmp_name, {})
            result[tmp_name][VIDEO_TEXT_FILE] = file

        #处理视频语音文本文件
        if file.startswith(VOICE_TEXT_PREFIX) and file.endswith(TEXT_SUFFIX):
            tmp_name = file.replace(VOICE_TEXT_PREFIX, "").replace(TEXT_SUFFIX, "")
            if tmp_name.isdigit() == False:
                raise Exception("voice_text_files file name must be number")
            voice_text_files.append(file)
            voice_text_files_seq.append(int(tmp_name))
            result.setdefault(tmp_name, {})
            result[tmp_name][VOICE_TEXT_FILE] = file


    # 判断三个文件列表是否一致
    if len(video_bg_files) != len(video_text_files) or len(video_bg_files) != len(voice_text_files):
        print("Error: Input ' video_text_files / voice_text_files / video_bg_img ' must be same length, please check path:", defined.INPUT_ROOT_PATH, "\n")
        raise Exception("video_bg_files and video_text_files and voice_text_files must be same length")
    
    #判断列表中序列号是否一致
    if video_bg_files_seq != video_text_files_seq or video_bg_files_seq != voice_text_files_seq:
        print("Error: Input video_bg_files and video_text_files and voice_text_files must be same sequence number, please check path:", defined.INPUT_ROOT_PATH, "\n")
        raise Exception("video_bg_files and video_text_files and voice_text_files must be same sequence number")
        
    #返回文件列表
    return result

# 获取输出的wav文件路径
def get_output_wav_file_path(num):
    if os.path.exists(INPUT_AUDIO_ROOT_PATH) is False:
        os.makedirs(INPUT_AUDIO_ROOT_PATH)        
    output_file = INPUT_AUDIO_ROOT_PATH + num +''+ WAV_SUFFIX 
    return output_file

# 获取输出的mp3文件路径
def get_output_mp3_file_path(num):
    if os.path.exists(INPUT_AUDIO_ROOT_PATH) is False:
        os.makedirs(INPUT_AUDIO_ROOT_PATH)    
    output_file = INPUT_AUDIO_ROOT_PATH + num +''+ MP3_SUFFIX
    return output_file

# 获取背景图片文件路径
def get_bg_img_file_path(num):
    if os.path.exists(INPUT_ROOT_PATH) is False:
        os.makedirs(INPUT_ROOT_PATH)
    output_file = INPUT_ROOT_PATH + num +''+ PNG_SUFFIX
    return output_file

# 获取输出的图片文件路径
def get_output_img_file_path(num):
    if os.path.exists(INPUT_IMGS_ROOT_PATH) is False:
        os.makedirs(INPUT_IMGS_ROOT_PATH)
    output_file = INPUT_IMGS_ROOT_PATH + num +''+ PNG_SUFFIX
    return output_file

# 获取输入的文本文件路径
def get_input_text_file_path(fname):
    if os.path.exists(INPUT_ROOT_PATH) is False:
        os.makedirs(INPUT_ROOT_PATH)
    output_file = INPUT_ROOT_PATH + fname
    return output_file

# 获取批量生成图片的目录
def get_batch_img_dir_path(num):
    img_dir = INPUT_IMGS_ROOT_PATH + num
    if os.path.exists(img_dir) is False:
        os.makedirs(img_dir)
    return img_dir

# 获取中途视频文件目录
def get_input_video_file_path(num):
    # print(1111111111111111111111)
    if os.path.exists(INPUT_VIDEO_ROOT_PATH) is False:
        # print(222222222222222222222)
        os.makedirs(INPUT_VIDEO_ROOT_PATH)    
    video_file_path = INPUT_VIDEO_ROOT_PATH +''+ num + MP4_SUFFIX
    return video_file_path


# 获取生成视频的路径
def get_output_video_file_path(file_name = ''):
    if file_name != '':
        output_file = OUTPUT_ROOT_PATH + file_name + MP4_SUFFIX
        return output_file
    
    # 获取年月日时分秒
    now = datetime.datetime.now()
    fname = str(now.year) +""+ str(now.month) +""+ str(now.day) +"-"+ str(now.hour) +""+ str(now.minute) +""+ str(now.second)

    output_file = OUTPUT_ROOT_PATH + 'final'+ '-' + fname + MP4_SUFFIX
    return output_file

# 获取需要合成最终视频的临时list文件路径
def get_input_video_list_file_path(file_name = 'videolist'):
    if os.path.exists(INPUT_VIDEO_ROOT_PATH) is False:
        os.makedirs(INPUT_VIDEO_ROOT_PATH)    
    video_list_file = INPUT_VIDEO_ROOT_PATH +''+ file_name + TEXT_SUFFIX
    return video_list_file   


# 获取字幕文件
def get_input_srt_file_path(video_name = ''):
    if os.path.exists(INPUT_SRT_ROOT_PATH) is False:
        os.makedirs(INPUT_SRT_ROOT_PATH)        
    if video_name == '':
        video_name = 'final'
    srt_file_path = INPUT_SRT_ROOT_PATH +''+ video_name + SRT_SUFFIX
    return srt_file_path

# 字幕文件来源的临时文件路径
def get_input_srt_audio_file_path(audio_name = ''):
    if os.path.exists(INPUT_AUDIO_ROOT_PATH) is False:
        os.makedirs(INPUT_AUDIO_ROOT_PATH)        
    if audio_name == '':
        audio_name = 'final'
    audio_file_path = INPUT_AUDIO_ROOT_PATH +''+ audio_name + WAV_SUFFIX
    return audio_file_path

