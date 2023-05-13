
# -*- encoding: utf-8 -*-

'''
Image Process
图片处理处理核心函数

author: heiyeluren
date: 2023/5/12
site: github.com/heiyeluren

'''

import os
import platform
import subprocess
from PIL import Image
from pydub import AudioSegment
import azure.cognitiveservices.speech as speechsdk

from . import defined
from .defined import *
from . import util
from .util import *


'''

把单张图片复制成为180张图片，然后用ffmpeg把图片合成为视频

'''

# 获取音频文件时长
def get_audio_duration(file_path: str, is_int = False):
    """
    获取音频文件的时长

    参数：
    file_path：str，音频文件的路径

    返回值：
    float，音频文件的时长，单位为秒

    调用示例：
    s = get_audio_duration(os.path.join(os.path.dirname(__file__), "output/voice_text_title.mp3"), True)
    print(s)
    """
    #目录把 \\ 转成 /
    file_path = file_path.replace("\\", "/") 

    if not os.path.exists(file_path):
        raise Exception("audio file is not exists")

    
    # 使用pydub读取音频文件
    audio_file = AudioSegment.from_file(file_path)
    # 获取音频文件的时长
    duration = audio_file.duration_seconds
    if is_int:
        return int(duration)
    else:
        return duration

# 获取音频文件大小
def get_audio_file_size(file_path: str) -> float:
    """
    获取音频文件的大小

    参数：
    file_path：str，音频文件的路径

    返回值：
    float，音频文件的大小，单位为MB
    """
    # 使用os获取音频文件的大小
    file_size = os.path.getsize(file_path)
    # 转换为MB
    file_size = file_size / (1024 * 1024)
    return file_size


# 生成每个视频文件需要的图片数量
def make_img_from_audio(audio_file_path: str, src_img_file: str, save_img_dir: str, rate: int = 2):
    """
    生成每个视频文件需要的图片数量

    参数：
    audio_file_path：str，音频文件的路径
    src_img_file：str，源图片文件的路径
    save_img_dir：str，保存图片的文件夹
    rate：int，每秒钟需要生成多少张图片（视频帧率）

    返回值：
    无

    调用示例：
    make_img_from_audio(os.path.join(os.path.dirname(__file__), "output/voice_text_title.mp3"), os.path.join(os.path.dirname(__file__), "output_text.png"), os.path.join(os.path.dirname(__file__), "imgs"), 2)
    """
    #目录把 \\ 转成 /
    audio_file_path = audio_file_path.replace("\\", "/")
    src_img_file = src_img_file.replace("\\", "/")
    save_img_dir = save_img_dir.replace("\\", "/")

    # 获取音频文件的时长
    duration = get_audio_duration(audio_file_path, True)
    # 获取音频文件的大小
    # file_size = get_audio_file_size(audio_file_path)
    # 计算每秒钟需要生成多少张图片
    # rate = int(file_size / 10) + 1
    # 计算总共需要生成多少张图片
    total = duration * rate
    # 读取源图片
    im = Image.open(src_img_file)
    # 创建一个保存图片的文件夹
    if not os.path.exists(save_img_dir):
        os.makedirs(save_img_dir)
    # 保存图片
    for i in range(total):
        output_image_path = os.path.join(save_img_dir, "{0:03d}.png".format(i))  # 文件名为0到179的三位数字，例如"001.jpg"
        im.save(output_image_path)


'''

调用示例：
img_path = "img"  #图片文件夹，图片必须以为 001.png, 002.png, 003.png, ...的格式命名
output_path = "output_video.mp4"
frame_rate = 2
video_size = "1920x1080"
video_codec = "libx264"
audio_path = "audio.mp3"

images_to_video(img_path, output_path, audio_path, frame_rate=2, video_size="1920x1080", video_codec='libx264')

'''
def images_to_video(img_path, output_path, audio_path=None, frame_rate=2, video_size="1920x1080", video_codec='libx264'):

    # 创建一个保存视频的文件夹
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

    if audio_path is None:
        subprocess.call(f"ffmpeg -f image2 -r {frame_rate} -i {img_path}/%03d.png -s {video_size} -pix_fmt yuv420p -c:v {video_codec} {output_path}", shell=True)
    else:
        subprocess.call(f"ffmpeg -f image2 -r {frame_rate} -i {img_path}/%03d.png -i {audio_path} -s {video_size} -pix_fmt yuv420p -c:v {video_codec} -c:a aac -map 0:v:0 -map 1:a:0? {output_path}", shell=True)

    #修改文件权限
    os.chmod(output_path, 0o777)


# 把多个视频文件进行合并
"""

mylist.txt文件内容：
file '/path/to/file1'
file '/path/to/file2'
file '/path/to/file3'
file '/path/to/file4'
...

"""
def merge_videos(video_list: list, output_video_file_path: str, video_list_file: str): #, output_file_name: str = ""):
    # 创建一个保存视频的文件夹
    with open(video_list_file, "w") as f:
        for item in video_list:
            item = item.replace("\\", "/")
            f.write(f"file '{item}'\n")
        os.chmod(video_list_file, 0o777)

    # 使用ffmpeg把多个视频文件进行合并
    cmd = f'ffmpeg -f concat -safe 0 -i {video_list_file} -c copy {output_video_file_path}'
    # print(cmd)
    subprocess.call(cmd, shell=True)
    # os.remove("videolist.txt")




"""
从字幕文件中给视频添加字幕

    ref: https://blog.csdn.net/qq_21743659/article/details/109305411

    #字幕转换 srt转成vtt或ass
    # ffmpeg -i test_1280x720_3.srt test_1280x720_3_1.vtt
    # ffmpeg -i test_1280x720_3.srt test_1280x720_3_1.ass
    
    #进行合并
    # ffmpeg -i video.mp4 -i subtitle.srt -c copy -c:s mov_text output.mp4
    # ffmpeg -i test_1280x720_3.mp4 -i test_1280x720_3.srt -c copy output.mkv  #添加软字幕，目标文件只能是mkv格式
    # ffmpeg -i test_1280x720_3.mp4 -vf subtitles='test_1280x720_3.srt' out.mp4  #添加硬字幕，注意 subtitle 必须是相对路径

    测试代码：
    video_file_path = os.path.join(os.path.dirname(__file__), "output/final_raw.mp4")
    srt_file_path = os.path.join(os.path.dirname(__file__), "output/final_raw.srt")
    output_file_path = os.path.join(os.path.dirname(__file__), "output/final.mp4")
    merge_video_src(video_file_path, srt_file_path, output_file_path)


"""
def merge_video_srt(video_file_path, srt_file_path, output_file_path, is_play=False):

    #文件是否存在
    if not os.path.exists(video_file_path):
        raise Exception("video file not exist.")
    if not os.path.exists(srt_file_path):
        raise Exception("srt file not exist.")
    

    srt_file_path = srt_file_path.replace("\\", "/")
    video_file_path = video_file_path.replace("\\", "/")
    output_file_path = output_file_path.replace("\\", "/")
    srt_dir_path = os.path.dirname(srt_file_path)
    srt_file = os.path.basename(srt_file_path)

    # cd d:/Code/self/python/video3 && ffmpeg -i d:/Code/self/python/video3/output/final_raw.mp4 -vf subtitles=output/final_raw.srt d:/Code/self/python/video3/output/final.mp4
    cmdLine = 'cd {srt_dir_path} && ffmpeg -i {video_file_path} -vf subtitles="{srt_file}" {output_file_path}'
    cmdLine = cmdLine.format(srt_dir_path=srt_dir_path, video_file_path=video_file_path, srt_file=srt_file, output_file_path=output_file_path)
    # print(cmdLine)
    
    subprocess.call(cmdLine, shell=True)

    #播放最终视频
    if is_play:
        play_video(output_file_path)

