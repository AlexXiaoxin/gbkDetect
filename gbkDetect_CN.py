#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import chardet
import codecs
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def detect_encoding(file_path):
    """
    检测文件编码
    :param file_path: 文件路径
    :return: 检测到的编码名称，若失败则返回 None
    """
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            return result['encoding']
    except Exception as e:
        logger.error(f"检测 {file_path} 编码时出错: {e}")
        return None

def is_chinese_character(char):
    """
    检查字符是否为中文字符
    :param char: 单个字符
    :return: 布尔值，表示是否为中文字符
    """
    return '\u4e00' <= char <= '\u9fff'

def has_chinese_text(text):
    """
    检查文本是否包含中文字符
    :param text: 输入文本
    :return: 布尔值，表示是否包含中文字符
    """
    return any(is_chinese_character(char) for char in text)

def find_chinese_garbled_chars(text):
    """
    查找可能的乱码中文字符
    :param text: 输入文本
    :return: 乱码字符列表，格式为 [(行号, 位置, 字符)]
    """
    garbled_chars = []
    garbled_patterns = ['锟斤拷', '锘', '��', '\ufffd']
    
    for line_num, line in enumerate(text.split('\n'), 1):
        for pattern in garbled_patterns:
            if pattern in line:
                pos = line.index(pattern)
                garbled_chars.append((line_num, pos, pattern))
    
    return garbled_chars

def convert_to_gbk(file_path):
    """
    将文件编码转换为GBK
    :param file_path: 文件路径
    :return: 布尔值，表示转换是否成功
    """
    try:
        encoding = detect_encoding(file_path)
        if not encoding:
            logger.warning(f"无法检测 {file_path} 的编码")
            return False
            
        with codecs.open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        
        with codecs.open(file_path, 'w', encoding='gbk', errors='ignore') as f:
            f.write(content)
            
        logger.info(f"已将 {file_path} 从 {encoding} 转换为GBK")
        return True
    except Exception as e:
        logger.error(f"转换 {file_path} 时出错: {e}")
        return False

def check_gbk_file_for_garbled_text(file_path):
    """
    检查GBK文件中的乱码中文文本
    :param file_path: 文件路径
    :return: 布尔值，表示是否发现乱码文本
    """
    try:
        with codecs.open(file_path, 'r', encoding='gbk') as f:
            content = f.read()
        
        garbled_chars = find_chinese_garbled_chars(content)
        if garbled_chars:
            for line_num, pos, char in garbled_chars:
                logger.warning(f"发现乱码文本在 {file_path} 的第 {line_num} 行: {char}")
            return True
        return False
    except Exception as e:
        logger.error(f"读取 {file_path} 时出错: {e}")
        return False

def process_file(file_path):
    """
    处理单个文件
    :param file_path: 文件路径
    """
    logger.info(f"正在处理: {file_path}")
    detected_encoding = detect_encoding(file_path)
    
    if not detected_encoding:
        logger.warning(f"无法确定 {file_path} 的编码")
        return
    
    detected_encoding = detected_encoding.lower()
    
    if detected_encoding.startswith('gb') or detected_encoding.startswith('windows'):
        logger.info(f"{file_path} 已经是GBK兼容编码")
        if check_gbk_file_for_garbled_text(file_path):
            logger.warning(f"警告: 在 {file_path} 中发现乱码文本")
    else:
        logger.info(f"正在将 {file_path} 从 {detected_encoding} 转换为GBK...")
        if convert_to_gbk(file_path):
            logger.info(f"成功转换 {file_path}")

def process_cpp_files(directory):
    """
    处理目录中的所有.cpp文件
    :param directory: 目录路径
    """
    cpp_files = list(Path(directory).rglob("*.cpp"))
    logger.info(f"找到 {len(cpp_files)} 个 .cpp 文件")
    
    with ThreadPoolExecutor() as executor:
        executor.map(process_file, cpp_files)

if __name__ == "__main__":
    directory = input("请输入目录路径 (或按回车键使用当前目录): ").strip() or "."
    if not os.path.exists(directory):
        logger.error(f"目录 {directory} 不存在")
        exit(1)
    
    process_cpp_files(directory)
    logger.info("处理完成。")