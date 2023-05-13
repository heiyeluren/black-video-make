# -*- encoding: utf-8 -*-

'''
Image Process
图片处理处理核心函数

author: heiyeluren
date: 2023/5/11
site: github.com/heiyeluren

'''

import os
import subprocess
from typing import List, Tuple
from PIL import Image, ImageDraw, ImageFont, ImageColor

from . import defined
from .defined import *
from . import util
from .util import *


# 添加文字到图片上
def add_text_to_image(image_file: str, text: List[str], font_size: int, text_color: Tuple, bg_color: str, output_file: str, 
                      bold_lines: int, bold_font_file = BOLD_FONT_FILE, normal_font_file = NORMAL_FONT_FILE):
    
    """
    参数说明：
    add_text_to_image(image_file: str, text: List[str], font_size: int, 
                    text_color: str, bg_color: str, output_file: str, bold_lines: int)

    输入参数:
        image_file : str : 原始图像的文件路径
        text : List[str] : 按行分隔的文本列表
        font_size : int : 字体的大小（磅值）
        text_color : str : 文本的颜色，格式为 "R, G, B"（整数值，范围为0-255）
        bg_color : str : 背景色，格式为 "R, G, B"（整数值，范围为0-255）
        output_file : str : 输出图像的文件路径
        bold_lines : int : 前多少行文本需要加粗显示

    输出：
        无返回值

    调用示例：
    image_file = "input.png"
    text = [
        "This is the first line. This should be printed in bold",
        "This is the second line. This should be printed in bold too",
        "This is the third line. This should be printed in regular font.",
        "And this is the last line. This should also be regular font"
    ]
    font_size = 36
    text_color = "255, 255, 255"
    bg_color = "0, 0, 0"
    output_file = "output.png"

    add_text_to_image(image_file, text, font_size, text_color, bg_color, output_file, bold_lines=2)

    颜色参考：
    black	黑色
    white	白色
    red	    红色
    green	绿色
    blue	蓝色
    yellow	黄色
    orange	橙色
    purple	紫色
    pink	粉红色
    gray	灰色
    brown	棕色
    gold	金色
    silver	银色
    (64, 64, 64) 深灰色
    (192, 192, 192) 浅灰色
    """
    
    # 打开原始图像
    base_image = Image.open(image_file).convert("RGBA")
    # 创建 draw 对象
    draw = ImageDraw.Draw(base_image)

    # 加载字体文件
    if bold_font_file == '':
        bold_font_file = BOLD_FONT_FILE
    if normal_font_file == '':
        normal_font_file = NORMAL_FONT_FILE

    bold_font = ImageFont.truetype(bold_font_file, font_size)
    normal_font = ImageFont.truetype(normal_font_file, font_size)

    # 设置文本行高
    line_height = max([draw.textbbox((0, 0), line, font=bold_font)[3] - draw.textbbox((0, 0), line, font=bold_font)[1] for line in text])

    # line_height = max([draw.textsize(line, font=bold_font)[1] for line in text])
    text_height = 0

    # 绘制文本
    # i = 0
    # print(bold_lines)
    # a = "aaaaaaa"
    # A = "AAAAAAA"
    # return
    for i in range(len(text)):
        line = text[i]
        # font_type = normal_font
        font_type = bold_font if i < bold_lines else normal_font  # 前面 bold_lines 行加粗
        bbox = draw.textbbox((0, 0), line, font=font_type)
        text_width, _ = bbox[2] - bbox[0], bbox[3] - bbox[1]
        if line:  # 如果该行不为空，则绘制
            draw.text(((base_image.width - text_width) // 2, text_height), line, fill=text_color, font=font_type)
        text_height += line_height    
    # 保存图像
    base_image.save(output_file)


# 绘制文本到图片基础函数
def draw_text2img_base(input_text_file, output_img_file, bg_img_file, font_size, text_color, bg_color, bold_lines, normal_font_file, bold_font_file):
    # 输入文字的参数
    # fontfile = BOLD_FONT_FILE # 字体文件的全路径
    # fontcolor = "white" # 字体颜色
    # fontsize = 32 # 字体大小
    # font_size = 100
    # bg_color = "0, 0, 0"
    # text_color = (64, 64, 64 )# 深灰色

    bg_img_file         = bg_img_file       # 背景图片
    input_text_file     = input_text_file   # 输入文本文件
    output_img_file     = output_img_file   # 输出图片文件
    font_size           = font_size         # 字体大小
    text_color          = text_color        # 字体颜色
    bg_color            = bg_color          # 背景颜色
    bold_lines          = bold_lines        # 前多少行文本需要加粗显示
    bold_font_file      = bold_font_file    # 粗体字体文件
    normal_font_file    = normal_font_file  # 普通字体文件


    text = get_file_contents(input_text_file)
    add_text_to_image(bg_img_file, text, font_size, text_color, bg_color, output_img_file, bold_lines, bold_font_file=bold_font_file, normal_font_file=normal_font_file)   



# 首页图片文字绘制
'''
字体大小：100
字体颜色：深灰色
背景颜色：白色
输出内容前多少行加粗显示: 10行
'''
def draw_first_page(text_file, output_img_file, bg_img_file, font_size=100, text_color=(64, 64, 64), bg_color="0, 0, 0", bold_lines=10, normal_font_file = BOLD_FONT_FILE, bold_font_file = BOLD_FONT_FILE):
     draw_text2img_base(text_file, output_img_file, bg_img_file, font_size, text_color, bg_color, bold_lines, normal_font_file, bold_font_file)


# 内容页图片文字绘制
'''
字体大小: 70
字体颜色：深灰色
背景颜色：白色
输出内容前多少行加粗显示: 1行
'''
def draw_contents_page(text_file, output_img_file, bg_img_file, font_size=70, text_color=(64, 64, 64), bg_color="0, 0, 0", bold_lines=1, normal_font_file = BOLD_FONT_FILE, bold_font_file = BOLD_FONT_FILE):
    draw_text2img_base(text_file, output_img_file, bg_img_file, font_size, text_color, bg_color, bold_lines, normal_font_file, bold_font_file)


# 尾页图片文字绘制
'''
字体大小：100
字体颜色：深灰色
背景颜色：白色
输出内容前多少行加粗显示: 10行
'''
def draw_end_page(text_file, output_img_file, bg_img_file, font_size=100, text_color=(64, 64, 64), bg_color="0, 0, 0", bold_lines=10, normal_font_file = BOLD_FONT_FILE, bold_font_file = BOLD_FONT_FILE):
    draw_text2img_base(text_file, output_img_file, bg_img_file, font_size, text_color, bg_color, bold_lines, normal_font_file, bold_font_file)

