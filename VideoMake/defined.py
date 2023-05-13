# -*- encoding: utf-8 -*-

'''
Const defined variables

一些主要常量的定义

author: heiyeluren
date: 2023/5/10
site: github.com/heiyeluren

'''

import os
import platform


# 全局变量 input / output 目录定义
ROOT_PATH               = os.path.abspath(os.path.join(os.path.dirname(__file__), "../")).replace("\\", "/") + "/"
INPUT_ROOT_PATH         = os.path.abspath(os.path.join(os.path.dirname(__file__), "../input/")).replace("\\", "/") + "/"
INPUT_IMGS_ROOT_PATH    = os.path.abspath(os.path.join(os.path.dirname(__file__), "../input/img/")).replace("\\", "/") + "/"
INPUT_AUDIO_ROOT_PATH   = os.path.abspath(os.path.join(os.path.dirname(__file__), "../input/audio/")).replace("\\", "/") + "/"
INPUT_VIDEO_ROOT_PATH   = os.path.abspath(os.path.join(os.path.dirname(__file__), "../input/video/")).replace("\\", "/") + "/"
INPUT_SRT_ROOT_PATH     = os.path.abspath(os.path.join(os.path.dirname(__file__), "../input/srt/")).replace("\\", "/") + "/"
OUTPUT_ROOT_PATH        = os.path.abspath(os.path.join(os.path.dirname(__file__), "../output/")).replace("\\", "/") + "/"

# 文件前缀设定
VIDEO_BG_PREFIX         = "video_bg_"
VIDEO_TEXT_PREFIX       = "video_text_"
VOICE_TEXT_PREFIX       = "voice_text_"

# 文件后缀设定
PNG_SUFFIX              = ".png"
TEXT_SUFFIX             = ".txt"
MP3_SUFFIX              = ".mp3"
WAV_SUFFIX              = ".wav"
MP4_SUFFIX              = ".mp4"
SRT_SUFFIX              = ".srt"

# 关键文件名KEY设定
VIDEO_BG_FILE           = "video_bg_file"
VIDEO_TEXT_FILE         = "video_text_file"
VOICE_TEXT_FILE         = "voice_text_file"

FINAL_VIDEO_NAME        = "final"


# 操作系统
SYSTEM                  = platform.system()
OS_IS_WINDOWS           = True if SYSTEM == "Windows" else False

#字体文件定义
BOLD_FONT_FILE          = "C:/Windows/Fonts/msyhbd.ttc"  #粗体，注意：Linux字体文件在 /usr/share/fonts/ 目录
NORMAL_FONT_FILE        = "C:/Windows/Fonts/msyh.ttc"    #普通字体，注意：Linux字体文件在 /usr/share/fonts/ 目录


# 视频声音类型选择（本内容是提供给需要视频声音类型的切换参考，可以把 zh-CN-XXX 这段文本在调用中替换为对应的声音类型）
VOICE_TYPE_NAME         = {
    "zh-CN-XiaoxiaoNeural": "小小 - 女",
    "zh-CN-XiaohanNeural": "小涵 - 女",
    "zh-CN-XiaomoNeural": "小墨 - 女",
    "zh-CN-XiaoruiNeural": "小蕊 - 女",
    "zh-CN-XiaoxuanNeural": "小璇 - 女",
    "zh-CN-XiaomengNeural": "小梦 - 女",
    "zh-CN-XiaoyouNeural": "小优 - 女 - 儿童",
    "zh-CN-XiaoxinNeural": "小欣 - 女",
    "zh-CN-XiaochenNeural": "小陈 - 女",
    "zh-CN-XiaoqiuNeural": "小秋 - 女",
    "zh-CN-XiaoshuangNeural": "小双 - 女性、儿童",
    "zh-CN-XiaoxiaoNeural": "小小 - 女",
    "zh-CN-XiaoyanNeural": "小妍 - 女",
    "zh-CN-XiaoyiNeural": "小艺 - 女",
    "zh-CN-XiaozhenNeural": "小珍 - 女",
    "zh-CN-YunfengNeural": "云风 - 男",
    "zh-CN-YunhaoNeural": "云浩 - 男",
    "zh-CN-YunjianNeural": "云剑 - 男",
    "zh-CN-YunxiaNeural": "云峡 - 男",
    "zh-CN-YunxiNeural": "云溪 - 男",
    "zh-CN-YunyangNeural": "云阳 - 男",
    "zh-CN-YunyeNeural": "云烨 - 男",
    "zh-CN-YunzheNeural": "云哲 - 男",    
}

