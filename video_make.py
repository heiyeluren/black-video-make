# -*- encoding: utf-8 -*-

'''
## Heiyeluren Black-Video-Make ##

Heiyeluren Video Make

author: heiyeluren
date: 2023/5/14
site: github.com/heiyeluren

description:

VideoMake 是一个视频制作工具，可以只是自己输入简单的文字文本内容，然后自动生成一个视频。

本代码是一个整个调用视频生成的完整示例。

'''


import os
import platform
import subprocess
import shutil
import time
import datetime
import random

import pyttsx3
import win32gui, win32ui, win32con, win32api
from PIL import Image
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

from VideoMake.util import *
import VideoMake.util as util
from VideoMake.defined import *
import VideoMake.defined as defined
from VideoMake.audio import *
import VideoMake.audio as audio
from VideoMake.img import *
import VideoMake.img as img
from VideoMake.video import *
import VideoMake.video as video
from VideoMake.voice import *
import VideoMake.voice  as voice





"""
## 程序概要介绍 ##

Black-Video-Make 是一个视频制作工具，可以只是自己输入简单的文字文本内容，然后自动生成一个视频。
能够方便快速的帮助我们完全无依赖，不需要进行复杂剪辑制作过程，直接通过简单输入文本内容和相应视频背景，就可以生成图片。

其他重要说明：
目前程序除了基本的Python版本和pip安装包，另外主要需要依赖的就是微软Azure的免费账号以及ffmpeg程序即可；
目前本程序在 Windows 10/11 上面运行稳定，Linux环境需要自行测试。


## 依赖环境说明 ##

1. 第三方账号：
必须注册好微软的云服务azure，然后创建好免费账号，然后创建好对应的区域服务，记录下对应的key和区域信息，填写到下面的配置中。
Azure访问网址：https://azure.microsoft.com/zh-cn

设置好Azure的认知服务的key和区域信息，设置环境变量：
Windows平台(Windows 10/11)：
setx SPEECH_KEY "xxxxxxxx"
setx SPEECH_REGION "yyy"

Linux平台：
echo 'export SPEECH_KEY=xxxxxxxx' | sudo /etc/profile
echo 'export SPEECH_REGION=yyyyy' | sudo /etc/profile 
source /etc/profile


2. 程序依赖的第三方库：
pip install azure.cognitiveservices.speech
pip install pydub
pip install pillow
pip install pyttsx

或者直接： pip install -r requirements.txt

3. 第三方软件：

Windows平台(Windows 10/11)：
ffmpeg (必须)： https://github.com/BtbN/FFmpeg-Builds/releases
vlc (可选)： https://www.videolan.org/vlc/index.zh.html

Visual C++ Redistributable Package：(Windows系统 必须)
https://learn.microsoft.com/zh-cn/cpp/windows/latest-supported-vc-redist?view=msvc-170
https://download.visualstudio.microsoft.com/download/pr/8b92f460-7e03-4c75-a139-e264a770758d/26C2C72FBA6438F5E29AF8EBC4826A1E424581B3C446F8C735361F1DB7BEFF72/VC_redist.x64.exe


Linux平台：

ffmpeg (必须)：   sudo apt install ffmpeg / sudo yum install ffmpeg / sudo pacman -S ffmpeg / sudo dnf install ffmpeg
vlc (可选)：      sudo apt install vlc / sudo yum install vlc / sudo pacman -S vlc / sudo dnf install vlc


4. Python版本
必须使用 Python 3.7+ 版本，建议使用 Python 3.10+ 版本


## 程序工作流程 ##


生成视频工作流程：

第一步：准备好基础素材，主要包括视频背景图、视频显示内容文字、视频每个部分内容语音文本
写好自己需要生成的文字文本内容，保存为txt文件，放在raw_input目录下，比如：input/voice_01.txt，主要文本内容包括：
视频背景图：video_bg_XX.png
视频内文本：video_text_XX.png
视频语音：voice_text_XX.mp3

上面的XX主要是编号，比如：01、02、03等等，必须一一对应，就是如果视频背景图和视频内显示文本和视频这个环节的语音文本，都需要编号一致。
(注意：开始文件名和编号数字XX必须一致，否则出来的视频就会错乱)


第二步：生成视频中的语音内容

说明：本步骤主要是按照 input 目录中输入的 voice_text_XX.txt 文件，生成对应的语音内容文件，保存到 output 目录中。


第三步：生成视频中的显示内容
说明：
本步骤是比较复杂的，要求 input 目录中提供好对应视频背景图片、还有对应要显示内容到背景图的文本文件、还有视频中语音内容的文本文件，对应编号要一致。
比如：video_bg_01.png、video_text_01.txt、voice_text_01.txt，这三个文件的编号都是01，这样才能对应上。（文件前缀名必须一致，然后每个文件内容相关的编号必须一致）

video_bg_XX.png：视频背景图
video_text_XX.txt：视频中显示的文本内容
voice_text_XX.txt：视频中语音内容的文本内容

第四步：生成基本视频
说明：
本步骤主要是按照生成视频所有需要的图片，然后图片合并成为视频，然后再合并上对应的语音内容，生成最终的视频。


第五步：生成视频中的语音字幕

这一步骤主要是需要生成语音字幕，可以调用某些字幕工具，或者自己把上面生成视频导入进去出字幕srt文件。
（这一步目前实现了字幕内容还原，但是时间轴无法对齐，会导致显示的时候字幕挤在一起）

备注：如果想要生成更好的字幕，推荐比如“剪影”等视频剪辑工具，可以导出语音中的字幕，可以对应到时间轴。


第六步：合并视频和语音字幕，生成最终视频
这个步骤主要是把字幕文件和视频文件进行合并，生成最终的视频

"""


# 第0步：设置一些基本配置信息
G_OUTPUT_BASE_VIDEO_NAME    = 'base'    # 基本视频文件名
G_OUTPUT_FINAL_VIDEO_NAME   = 'final'   # 最终生成的视频文件名

'''
分段完成配置
#
想要生成那个环节就开启设置为True，如果有些步骤已经生成了，可以设置为True，然后跳过这些步骤，直接从下一步开始，
如果是调试使用，建议一步步进行，从上到下开启True，这样可以保证每个步骤都是正常的。
'''
G_IS_MAKE_TEXT_VOICE        = False        # 第二步：是否生成语音内容
G_IS_MAKE_IMG_FILES         = False        # 第三步：是否生成视频中的显示内容
G_IS_MAKE_BASE_VIDEO        = False        # 第四步：是否生成基本视频
G_IS_MAKE_RAW_SRT_FILE      = False        # 第五步：是否生成字幕文件（目前功能效果不好，测试可以用，推荐关闭）
G_IS_MAKE_FINAL_VIDEO       = False        # 第六步：是否生成最终视频（如果第五步字幕没有，本步骤可以跳过关闭）




#  第一步：检测输入的原始文件是否准备好，设置基本输出信息
dnames = util.check_input_files()
# print(dnames)

# 第二步：生成视频中的语音内容
'''
说明：本步骤主要是按照 input 目录中输入的 voice_text_XX.txt 文件，生成对应的语音内容文件，保存到 output 目录中。
'''
if G_IS_MAKE_TEXT_VOICE == True:
    for num in dnames:
        
        fname = dnames[num][VOICE_TEXT_FILE]
        input_text_file = INPUT_ROOT_PATH  + fname
        # output_wav_file = OUTPUT_ROOT_PATH + num +''+ WAV_SUFFIX  #fname.replace(TEXT_SUFFIX, WAV_SUFFIX)
        output_wav_file = get_output_wav_file_path(num)
        output_mp3_file = get_output_mp3_file_path(num)

        # print(input_text_file)
        # print(output_wav_file)
        # print(output_mp3_file)

        # 文字转音频
        synthesize_text_to_voice(
            input_text_file=input_text_file,
            output_wav_file=output_wav_file,
            is_output_mp3=False,
            output_mp3_file=output_mp3_file,
            is_play=False
        )
        
        # 等待几秒再生成下一个
        sed = random.randint(5, 10)
        time.sleep(sed)


# 第三步：生成视频中的显示内容（生成图片）
'''
说明：
本步骤是比较复杂的，要求 input 目录中提供好对应视频背景图片、还有对应要显示内容到背景图的文本文件、还有视频中语音内容的文本文件，对应编号要一致。
比如：video_bg_01.png、video_text_01.txt、voice_text_01.txt，这三个文件的编号都是01，这样才能对应上。（文件前缀名必须一致，然后每个文件内容相关的编号必须一致）

video_bg_XX.png：视频背景图
video_text_XX.txt：视频中显示的文本内容
voice_text_XX.txt：视频中语音内容的文本内容
'''
if G_IS_MAKE_IMG_FILES == True:
    total_num = len(dnames)
    for num in dnames:
        num_int = int(num)

        # fname = 
        bg_img_file = INPUT_ROOT_PATH  + dnames[num][VIDEO_BG_FILE]
        input_text_file = get_input_text_file_path(dnames[num][VIDEO_TEXT_FILE])
        output_img_file = get_output_img_file_path(num)

        # print(bg_img_file)
        # print(input_text_file)
        # print(output_img_file)

        # 第一页
        if num_int == 1:
            draw_first_page(input_text_file, output_img_file, bg_img_file)
        # 尾页
        elif num_int == total_num:
            draw_end_page(input_text_file, output_img_file, bg_img_file)
        # 内容页
        else:
            draw_contents_page(input_text_file, output_img_file, bg_img_file)
        
    print("Image file generated: {}".format(output_img_file))


# 第四步：生成基本视频
'''
说明：
本步骤主要是按照生成视频所有需要的图片，然后图片合并成为视频，然后再合并上对应的语音内容，生成最终的视频。
'''
if G_IS_MAKE_BASE_VIDEO == True:
    total_num = len(dnames)
    input_video_list = []
    for num in dnames:
        num_int = int(num)

        # 视频图片帧率（如果不怎动，推荐设置为2，如果语音太长，设置为1帧也可以，生成速度会大幅提高）
        fps = 1

        # 获取各个需要的文件和目录
        img_dir = get_batch_img_dir_path(num)
        audio_file = get_output_wav_file_path(num)
        src_img_file = get_output_img_file_path(num)
        input_video_file = get_input_video_file_path(num)

        if os.path.exists(audio_file) is False:
            raise Exception("Audio file not found: {}".format(audio_file))
        if os.path.exists(src_img_file) is False:
            raise Exception("Image file not found: {}".format(src_img_file))
        
        #生成构建视频需要的图片
        make_img_from_audio(audio_file, src_img_file, img_dir, fps)

        #图片生成视频 img_path, output_path, audio_path, fps
        images_to_video(img_dir, input_video_file, audio_file, fps)

        #构建视频列表
        input_video_list.append(input_video_file)

    # print(input_video_list)
    # 合并视频 get_output_video_file_path
    merge_videos(input_video_list, get_output_video_file_path(G_OUTPUT_BASE_VIDEO_NAME), get_input_video_list_file_path())

    print("Base video file generated: {}".format(get_output_video_file_path(G_OUTPUT_BASE_VIDEO_NAME)))



# 第五步：生成视频中的语音字幕
'''
说明：
调用语音引擎，把视频中的语音内容识别成为字幕文件，保存为 srt 格式的字幕文件（目前效果不好，推荐关闭）
'''
if G_IS_MAKE_RAW_SRT_FILE == True:
    # 设置 API 密钥和服务区域
    speech_key = get_tts_key('subscription')
    service_region = get_tts_key('region')

    # 准备视频文件路径和音频输出文件路径
    video_file_path = get_output_video_file_path(G_OUTPUT_BASE_VIDEO_NAME)
    srt_file_path = get_input_srt_file_path(G_OUTPUT_BASE_VIDEO_NAME)
    srt_audio_file_path = get_input_srt_audio_file_path(G_OUTPUT_BASE_VIDEO_NAME)

    stt = SpeechToText(speech_key, service_region, video_file_path, srt_audio_file_path, srt_file_path)
    stt.recognize_and_save_as_srt()
    # print(stt.text)
    print("Raw srt file generated: {}".format(srt_file_path))



# 第六步：合并视频和语音字幕，生成最终视频
if G_IS_MAKE_FINAL_VIDEO == True:
    # 合并视频和字幕
    merge_video_srt(get_output_video_file_path(G_OUTPUT_BASE_VIDEO_NAME), 
                    get_input_srt_file_path(G_OUTPUT_FINAL_VIDEO_NAME), 
                    get_output_video_file_path(G_OUTPUT_FINAL_VIDEO_NAME)
    )
    print("Final video file generated: {}".format(get_output_video_file_path(G_OUTPUT_FINAL_VIDEO_NAME)))

